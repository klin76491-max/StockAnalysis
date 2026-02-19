"""主程式的執行區，只有此程式與其他套件相依降低耦合度，並被主程式引用"""
import pandas as pd
import backtrader as bt
import os
import pandas as pd
import uuid
import Plot.Plot as plot
import Infrastructure.Query.Query as qry
import Infrastructure.Data.StrategyReport as StrategyReport
import Infrastructure.Log.SaveLog as savelog
import Tools.DirectoryUtils as dir_utils

def run_backtest_engine(df, strategy_class, initial_cash, commission):
    """
    初始化 Cerebro 引擎，設定策略與分析器，並執行回測

    參數:
    df (pd.DataFrame): 準備好的股票數據 (需包含 OHLCV)
    strategy_class (class): 要執行的策略類別
    initial_cash (float): 初始資金
    commission (float): 交易手續費率

    回傳:
    tuple: (策略執行結果物件, Cerebro 引擎物件, 最終資金數值)
    """
    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.addstrategy(strategy_class)
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    
    # 加入分析器
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)
    
    print(f"初始資金: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    final_val = cerebro.broker.getvalue()
    print(f"最終資金: {final_val:.2f}")
    
    return results[0], cerebro, final_val

def calculate_metrics(strat_res, initial_cash, final_val, from_date, to_date):
    """
    從分析器提取並計算關鍵績效指標

    參數:
    strat_res (bt.Strategy): 策略執行結果物件
    initial_cash (float): 初始資金
    final_val (float): 最終資金
    from_date (str): 開始日期
    to_date (str): 結束日期

    回傳:
    dict: 包含各項績效指標的字典
    """
    trade_anl = strat_res.analyzers.trades.get_analysis()
    dd_anl = strat_res.analyzers.drawdown.get_analysis()
    sharpe_anl = strat_res.analyzers.sharpe.get_analysis()

    total_trades = trade_anl.get('total', {}).get('closed', 0)
    win_trades = trade_anl.get('won', {}).get('total', 0)
    days = (pd.to_datetime(to_date) - pd.to_datetime(from_date)).days
    
    # 計算報酬率
    total_ret = (final_val - initial_cash) / initial_cash
    annual_ret = ((1 + total_ret) ** (365/days) - 1) * 100 if days > 0 else 0.0

    # 處理進出場時間
    first_entry = None
    last_exit = None
    if hasattr(strat_res, 'trades_log') and strat_res.trades_log:
        first_entry = str(strat_res.trades_log[0]['Time'])
        last_exit = str(strat_res.trades_log[-1]['Time'])

    return {
        'total_trades': total_trades,
        'win_rate': (win_trades / total_trades * 100) if total_trades > 0 else 0.0,
        'max_dd': dd_anl.get('max', {}).get('drawdown', 0.0),
        'sharpe': sharpe_anl.get('sharperatio', 0.0) or 0.0,
        'total_ret_pct': total_ret * 100,
        'annual_ret_pct': annual_ret,
        'hold_days': trade_anl.get('len', {}).get('total', 0),
        'first_entry': first_entry,
        'last_exit': last_exit
    }

def calculate_equity_curve(strat_res, initial_cash, index):
    """
    計算每日權益曲線

    參數:
    strat_res (bt.Strategy): 策略執行結果物件
    initial_cash (float): 初始資金
    index (pd.Index): 日期索引

    回傳:
    pd.Series: 每日權益數值
    """
    returns = pd.Series(strat_res.analyzers.returns.get_analysis())
    equity = (1 + returns).cumprod() * initial_cash
    return equity.reindex(index, method='ffill').fillna(initial_cash)

def get_trade_log(strat_res):
    """
    取得交易紀錄 DataFrame

    參數:
    strat_res (bt.Strategy): 策略執行結果物件

    回傳:
    pd.DataFrame: 交易紀錄
    """
    if hasattr(strat_res, 'trades_log'):
        return pd.DataFrame(strat_res.trades_log)
    return pd.DataFrame()

def prepare_stock_data(db_path, table_name, from_date, to_date):
    """
    從資料庫讀取並清洗資料

    參數:
    db_path (str): 資料庫路徑
    table_name (str): 資料表名稱
    from_date (str): 開始日期 (YYYY-MM-DD)
    to_date (str): 結束日期 (YYYY-MM-DD)

    回傳:
    pd.DataFrame: 處理後的股票數據，若無資料則回傳 None
    """
    df = qry.GetData(db=db_path, table=table_name, from_date=from_date, to_date=to_date)
    if df.empty: return None
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    return df.set_index('Date')[['Open', 'High', 'Low', 'Close', 'Volume']]

def save_backtest_results(strat_res, metrics, trades, symbol, from_date, to_date, initial_cash, commission, report_db_path, log_db_path):
    """
    儲存回測報告與交易日誌

    參數:
    strat_res (bt.Strategy): 策略執行結果
    metrics (dict): 計算出的績效指標
    trades (pd.DataFrame): 交易紀錄
    symbol (str): 股票代號
    from_date (str): 開始日期
    to_date (str): 結束日期
    initial_cash (float): 初始資金
    commission (float): 手續費率
    report_db_path (str): 回測結果資料庫路徑
    log_db_path (str): 交易日誌資料庫路徑
    """
    uid = str(uuid.uuid4())
    res_obj = StrategyReport.BacktestResult(
        backtest_uuid=uid,
        strategy_name=strat_res.__class__.__name__,
        symbol=symbol, timeframe='daily', start_date=from_date, end_date=to_date,
        initial_capital=initial_cash,
        total_return=metrics['total_ret_pct'],
        max_drawdown=metrics['max_dd'],
        sharpe_ratio=metrics['sharpe'],
        trade_count=metrics['total_trades'],
        win_rate=metrics['win_rate'],
        commission_rate=commission, 
        slippage=0.0,
        parameter_note=str({k: v for k, v in strat_res.params._getitems()}),
        first_entry_date=metrics['first_entry'],
        last_exit_date=metrics['last_exit'],
        total_holding_times=metrics['hold_days'],
        annual_return=metrics['annual_ret_pct']
    )
    StrategyReport.save_backtest_result(report_db_path, res_obj)
    if not trades.empty:
        savelog.save_trade_logs(log_db_path, trades, uid)
        print(f"\n交易紀錄 (共 {len(trades)} 筆):")
        print(trades.to_string(index=False))

def create_charts(df, trades, equity, final_val, initial_cash, cerebro, symbol, strategy_name, from_date, to_date, output_dir):
    """
    生成並儲存圖表

    參數:
    df (pd.DataFrame): 歷史股價資料
    trades (pd.DataFrame): 交易紀錄
    equity (pd.Series): 每日權益變化
    final_val (float): 最終資產總值
    initial_cash (float): 初始投入資金
    cerebro (bt.Cerebro): Backtrader 引擎物件
    symbol (str): 股票代號
    strategy_name (str): 策略名稱
    from_date (str): 回測開始日期
    to_date (str): 回測結束日期
    output_dir (str): 圖表與報告輸出目錄
    """
    dir_utils.ensure_directory_exists(output_dir)
    file_name = os.path.join(output_dir, f"{symbol}_{strategy_name}_{from_date}_{to_date}")
    plot.generate_plotly_chart(df, trades, equity, final_val, initial_cash).write_html(f'{file_name}.html')
    print(f"\n圖表已保存: {file_name}.html")
    cerebro.plot()[0][0].savefig(f'{file_name}.png')
