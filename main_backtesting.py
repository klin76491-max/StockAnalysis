#%%
import Query.Query as gd
import Strategy.StrategyBacktesting as gcs

import pandas as pd
from backtesting import Backtest

if __name__ == '__main__':
    """大盤資料有 volumn 的期間：20030102 ~ 20261231"""
    table = 'yfince_TWII_1950_2026'
    db = 'GenData/data/daily/stock_data.db'
    from_date = '2025-10-05'
    to_date = '2027-01-01'
    # 資料欄位 Date Close High Low Open Volume
    df = gd.GetData(db = db, table = table, from_date = from_date, to_date = to_date)
    
    
    # 執行回測
    bt = Backtest(df, gcs.GoldenCrossStrategy, cash=100000, commission=.002)
    stats = bt.run()
    
    # 獲取交易日誌
    trades_df = pd.DataFrame(stats._strategy.trades_log)
    
    # 顯示回測結果
    print("=" * 60)
    print("MA5/MA20 黃金交叉策略回測結果")
    print("=" * 60)
    print(stats)
    print("\n" + "=" * 60)
    print("重要指標統計")
    print("=" * 60)
    print(f"初始資金: ${stats['Start']:.2f}")
    print(f"最終資金: ${stats['End']:.2f}")
    print(f"總報酬率: {stats['Return [%]']:.2f}%")
    print(f"年化報酬率: {stats['Return (Ann.) [%]']:.2f}%")
    print(f"最大回撤: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"勝率: {stats['Win Rate [%]']:.2f}%")
    print(f"獲利因子: {stats['Profit Factor']:.2f}")
    print(f"交易次數: {stats['# Trades']:.0f}")
    print(f"夏普比例: {stats['Sharpe Ratio']:.2f}")
    
    # 顯示交易詳情
    print("\n" + "=" * 80)
    print("交易詳情明細")
    print("=" * 80)
    print(trades_df.to_string(index=False))
    
    # 繪製回測圖表
    bt.plot(filename='Report/backtest_result.html')
    print("\n圖表已保存到: Report backtest_result.html")
    
#%%