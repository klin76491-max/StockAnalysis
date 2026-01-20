#%%
import pandas as pd
import backtrader as bt
import Query.Query as qry
import Strategy.Strategy as strategy
import Plot.Plot as plot

if __name__ == '__main__':
    # 1. 準備資料
    df = qry.GetData(db='GenData/data/daily/stock_data.db', 
                     table='yfince_TWII_1950_2026', 
                     from_date='2025-10-05', to_date='2027-01-01')
    
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')[['Open', 'High', 'Low', 'Close', 'Volume']]

    # 2. 設定回測
    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.addstrategy(strategy.GoldenCrossStrategyBacktrader)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.002)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns')

    # 3. 執行
    print(f"初始資金: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    final_val = cerebro.broker.getvalue()
    print(f"最終資金: {final_val:.2f}")

    # 4. 處理結果
    strat_res = results[0]
    trades = pd.DataFrame(strat_res.trades_log)
    
    returns = pd.Series(strat_res.analyzers.returns.get_analysis())
    equity = (1 + returns).cumprod() * 100000
    equity = equity.reindex(df.index, method='ffill').fillna(100000)

    if not trades.empty:
        print("\n交易紀錄:")
        # 印出 dataframe 格式對齊的版本
        print(trades.to_string(index=False))

    # 5. 繪圖 poltly 客製化圖表 
    plot.generate_plotly_chart(df, trades, equity, final_val, 100000).write_html('Report/backtest_result.html')
    print("\n圖表已保存: Report backtrader_result.html")

    # 6. 繪圖 backtrader 圖表
    cerebro.plot()[0][0].savefig('Report/backtrader_result.png')    
    
#%%