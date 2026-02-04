#%%
import pandas as pd
import backtrader as bt
import Query.Query as qry
import Strategy.Strategy as strategy
import Plot.Plot as plot
import GenData.StrategyReport as report

if __name__ == '__main__':
    # 設定回測參數
    symbol = 'TWII'
    from_date = '2023-01-01'
    to_date = '2026-01-01'
    initial_cash = 100000.0
    commission = 0.002

    # 1. 準備資料
    df = qry.GetData(db='GenData/data/daily/stock_data.db', 
                     table='yfince_TWII_1950_2026',
                     from_date=from_date, to_date=to_date)
    
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')[['Open', 'High', 'Low', 'Close', 'Volume']]

    # 2. 設定回測
    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.addstrategy(strategy.GoldenCrossStrategyBacktrader)
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)

    # 3. 執行
    print(f"初始資金: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    final_val = cerebro.broker.getvalue()
    print(f"最終資金: {final_val:.2f}")

    # 4. 處理結果
    strat_res = results[0]
    trades = pd.DataFrame(strat_res.trades_log)
    
    returns = pd.Series(strat_res.analyzers.returns.get_analysis())
    equity = (1 + returns).cumprod() * initial_cash
    equity = equity.reindex(df.index, method='ffill').fillna(initial_cash)

    # 計算回測指標並存入資料庫
    trade_analysis = strat_res.analyzers.trades.get_analysis()
    drawdown_analysis = strat_res.analyzers.drawdown.get_analysis()
    sharpe_analysis = strat_res.analyzers.sharpe.get_analysis()

    # 提取指標
    total_trades = trade_analysis.get('total', {}).get('closed', 0)
    win_trades = trade_analysis.get('won', {}).get('total', 0)
    win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0.0
    max_dd = drawdown_analysis.get('max', {}).get('drawdown', 0.0)
    sharpe_ratio = sharpe_analysis.get('sharperatio', 0.0)
    if sharpe_ratio is None: sharpe_ratio = 0.0

    # 計算年化報酬率 (簡單估算)
    days_diff = (pd.to_datetime(to_date) - pd.to_datetime(from_date)).days
    total_return_pct = (final_val - initial_cash) / initial_cash
    annual_return_pct = ((1 + total_return_pct) ** (365/days_diff) - 1) * 100 if days_diff > 0 else 0.0
    
    # 取得進出場時間
    first_entry = str(strat_res.trades_log[0]['Time']) if strat_res.trades_log else None
    last_exit = str(strat_res.trades_log[-1]['Time']) if strat_res.trades_log else None
    
    # 建立回測結果物件
    backtest_result = report.BacktestResult(
        strategy_name=strat_res.__class__.__name__,
        symbol=symbol,
        timeframe='daily',
        start_date=from_date,
        end_date=to_date,
        initial_capital=initial_cash,
        total_return=total_return_pct * 100, # 轉為百分比
        max_drawdown=max_dd,
        sharpe_ratio=sharpe_ratio,
        trade_count=total_trades,
        win_rate=win_rate,
        commission_rate=commission,
        slippage=0.0,
        parameter_note=str({k: v for k, v in strat_res.params._getitems()}),
        first_entry_date=first_entry,
        last_exit_date=last_exit,
        total_holding_times=trade_analysis.get('len', {}).get('total', 0),
        annual_return=annual_return_pct
    )
    
    # 存入資料庫
    report.save_backtest_result('GenData/report/daily/backtest_results.db', backtest_result)

    if not trades.empty:
        print("\n交易紀錄:")
        # 印出 dataframe 格式對齊的版本
        print(trades.to_string(index=False))

    # 5. 繪圖 poltly 客製化圖表 
    plot.generate_plotly_chart(df, trades, equity, final_val, initial_cash).write_html('Report/backtest_result.html')
    print("\n圖表已保存: Report backtrader_result.html")

    # 6. 繪圖 backtrader 圖表
    cerebro.plot()[0][0].savefig('Report/backtrader_result.png')    
    
#%%