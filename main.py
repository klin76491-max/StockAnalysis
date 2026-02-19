#%%
""" 主程式 """
from Execute.BacktestExecutor import run_backtest_engine, calculate_metrics, calculate_equity_curve, get_trade_log, prepare_stock_data, save_backtest_results, create_charts
import Strategy.Strategy as strategy

def main():
    """主程式入口：協調各模組執行回測流程"""
    # 參數設定
    symbol, from_date, to_date = 'TWII', '2023-01-01', '2026-01-01'
    initial_cash, commission = 100000.0, 0.002
    table_name = 'DataYfince_TWII_1950_2026'

    # 策略選擇
    strategy_model = strategy.GoldenCrossStrategyBacktrader
    
    # 檔案路徑設定
    db_path = 'DB/StockData.db'        # 股價資料庫
    report_db_path = 'DB/StockData.db' # 回測結果資料庫
    log_db_path = 'DB/StockData.db'    # 交易日誌資料庫
    output_dir = 'Report'                     # 圖表輸出目錄

    # 1. 準備資料
    df = prepare_stock_data(db_path, table_name, from_date, to_date)
    if df is None: print(f"No data found for {symbol}"); return

    # 2. 執行回測
    strat_res, cerebro, final_val = run_backtest_engine(
        df, strategy_model, initial_cash, commission
    )

    # 3. 計算指標與處理結果
    metrics = calculate_metrics(strat_res, initial_cash, final_val, from_date, to_date)
    trades = get_trade_log(strat_res)
    equity = calculate_equity_curve(strat_res, initial_cash, df.index)

    # 4. 存檔與繪圖
    save_backtest_results(strat_res, metrics, trades, symbol, from_date, to_date, initial_cash, commission, report_db_path, log_db_path)
    create_charts(df, trades, equity, final_val, initial_cash, cerebro, symbol, strat_res.__class__.__name__, from_date, to_date, output_dir)

if __name__ == '__main__':
    main()
#%%