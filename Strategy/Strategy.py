import backtrader as bt

class GoldenCrossStrategyBacktrader(bt.Strategy):
    params = (('ma5', 5), ('ma20', 20))
    
    def __init__(self):
        self.ma5 = bt.ind.SMA(self.data.close, period=self.params.ma5)
        self.ma20 = bt.ind.SMA(self.data.close, period=self.params.ma20)
        self.crossover = bt.ind.CrossOver(self.ma5, self.ma20)
        self.trades_log = []
    
    def next(self):
        if not self.position and self.crossover > 0:
            self.buy()
        elif self.position and self.crossover < 0:
            self.close()

    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades_log.append({
                '時間': self.data.datetime.date(0),
                '交易動作': '買進' if order.isbuy() else '賣出',
                '執行價格': order.executed.price,
                '執行當日收盤價': self.data.close[0],
                '執行當日開盤價': self.data.open[0],
                '執行前日收盤價': self.data.close[-1],
                '執行前日開盤價': self.data.open[-1],
                '目前資金': self.broker.getvalue()
            })
