# 定義 MA5/MA20 黃金交叉策略
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

class GoldenCrossStrategy(Strategy):
        """MA5/MA20 黃金交叉策略"""
        
        def init(self):
            # 計算 MA5 和 MA20
            self.ma5 = self.I(SMA, self.data.Close, 5)
            self.ma20 = self.I(SMA, self.data.Close, 20)
            # 記錄交易詳情
            self.trades_log = []
        
        def next(self):
            # MA5 從下往上穿越 MA20 - 買進信號 (黃金交叉)
            if crossover(self.ma5, self.ma20):
                if not self.position:
                    buy_price = self.data.Close[-1]
                    self.trades_log.append({
                        '時間': self.data.index[-1],
                        '交易動作': '買進',
                        '價格': buy_price,
                        '買進資金': self.equity,
                        '賣出資金': 0,
                        '目前資金': self.equity
                    })
                    self.buy()
            
            # MA5 從上往下穿越 MA20 - 賣出信號 (死亡交叉)
            elif crossover(self.ma20, self.ma5):
                if self.position:
                    sell_price = self.data.Close[-1]
                    sell_value = self.position.size * sell_price
                    self.trades_log.append({
                        '時間': self.data.index[-1],
                        '交易動作': '賣出',
                        '價格': sell_price,
                        '買進資金': 0,
                        '賣出資金': sell_value,
                        '目前資金': self.equity
                    })
                    self.position.close()
    