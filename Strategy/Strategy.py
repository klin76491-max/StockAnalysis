import backtrader as bt

class BaseLogStrategy(bt.Strategy):
    """基礎策略類別，用於處理交易記錄"""
    def __init__(self):
        self.trades_log = []

    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades_log.append({
                'Time': self.data.datetime.date(0),
                'TransactionAction': 'buy' if order.isbuy() else 'sell',
                'ExecutionPrice': order.executed.price,
                'ClosingPriceExecutionDay': self.data.close[0],
                'OpeningPriceExecutionDay': self.data.open[0],
                'ClosingPriceBeforeExecutionDay': self.data.close[-1],
                'OpeningPriceBeforeExecutionDay': self.data.open[-1],
                'CurrentFunds': self.broker.getvalue()
            })

class GoldenCrossStrategyBacktrader(BaseLogStrategy):
    '''
    MA 黃金交叉策略
    參數：ma5 (5日均線), ma20 (20日均線)
    買進：MA5 向上穿越 MA20
    賣出：MA5 向下穿越 MA20
    '''
    params = (('ma5', 5), ('ma20', 20))
    
    def __init__(self):
        super().__init__()
        self.ma5 = bt.ind.SMA(self.data.close, period=self.params.ma5)
        self.ma20 = bt.ind.SMA(self.data.close, period=self.params.ma20)
        self.crossover = bt.ind.CrossOver(self.ma5, self.ma20)
    
    def next(self):
        if not self.position and self.crossover > 0:
            self.buy()
        elif self.position and self.crossover < 0:
            self.close()

class RSIStrategyBacktrader(BaseLogStrategy):
    '''參數：預設 RSI 週期為 14，超買線為 70，超賣線為 30。
買進：當沒有持倉且 RSI 低於 30（超賣）時買進。
賣出：當持有倉位且 RSI 高於 70（超買）時平倉。
記錄：保留了與 GoldenCrossStrategyBacktrader 相同的交易記錄邏輯 (notify_order)。'''
    params = (('period', 14), ('upper', 70), ('lower', 30))
    
    def __init__(self):
        super().__init__()
        self.rsi = bt.ind.RSI(self.data.close, period=self.params.period)
    
    def next(self):
        if not self.position and self.rsi < self.params.lower:
            self.buy()
        elif self.position and self.rsi > self.params.upper:
            self.close()

class MACDStrategyBacktrader(BaseLogStrategy):
    '''參數：預設快線週期 12，慢線週期 26，訊號線週期 9。
指標：計算 MACD 線與訊號線 (Signal Line)。
買進：當 MACD 線向上穿越訊號線（黃金交叉）且無持倉時買進。
賣出：當 MACD 線向下穿越訊號線（死亡交叉）且持有倉位時平倉。
記錄：維持與前述策略一致的交易記錄格式。'''
    params = (
        ('period_me1', 12),
        ('period_me2', 26),
        ('period_signal', 9),
    )
    
    def __init__(self):
        super().__init__()
        self.macd = bt.ind.MACD(
            self.data.close,
            period_me1=self.params.period_me1,
            period_me2=self.params.period_me2,
            period_signal=self.params.period_signal
        )
        self.crossover = bt.ind.CrossOver(self.macd.macd, self.macd.signal)
    
    def next(self):
        if not self.position and self.crossover > 0:
            self.buy()
        elif self.position and self.crossover < 0:
            self.close()

class KDStrategyBacktrader(BaseLogStrategy):
    '''
    KD 隨機指標策略
    參數：period (9), period_dfast (3), period_dslow (3), upper (80), lower (20)
    買進：K值 < 20 (超賣區) 且 K值向上穿越 D值 (黃金交叉)
    賣出：K值 > 80 (超買區) 且 K值向下穿越 D值 (死亡交叉)
    '''
    params = (('period', 9), ('period_dfast', 3), ('period_dslow', 3), ('upper', 80), ('lower', 20))
    
    def __init__(self):
        super().__init__()
        self.kd = bt.ind.Stochastic(self.data, period=self.params.period, period_dfast=self.params.period_dfast, period_dslow=self.params.period_dslow)
    
    def next(self):
        if not self.position and self.kd.percK < self.params.lower and self.kd.percK > self.kd.percD:
            self.buy()
        elif self.position and self.kd.percK > self.params.upper and self.kd.percK < self.kd.percD:
            self.close()

class EMAStrategyBacktrader(BaseLogStrategy):
    '''
    EMA 指數移動平均線策略
    參數：period_short (12), period_long (26)
    買進：短週期 EMA 向上穿越 長週期 EMA
    賣出：短週期 EMA 向下穿越 長週期 EMA
    '''
    params = (('period_short', 12), ('period_long', 26))
    
    def __init__(self):
        super().__init__()
        self.ema_short = bt.ind.EMA(self.data.close, period=self.params.period_short)
        self.ema_long = bt.ind.EMA(self.data.close, period=self.params.period_long)
        self.crossover = bt.ind.CrossOver(self.ema_short, self.ema_long)
    
    def next(self):
        if not self.position and self.crossover > 0:
            self.buy()
        elif self.position and self.crossover < 0:
            self.close()

class ADXStrategyBacktrader(BaseLogStrategy):
    '''
    ADX 平均趨勢指標策略
    參數：period (14), adx_threshold (25)
    買進：+DI > -DI 且 ADX > 25 (趨勢形成)
    賣出：+DI < -DI
    '''
    params = (('period', 14), ('adx_threshold', 25))
    
    def __init__(self):
        super().__init__()
        self.adx = bt.ind.ADX(self.data, period=self.params.period)
        self.plus_di = bt.ind.PlusDI(self.data, period=self.params.period)
        self.minus_di = bt.ind.MinusDI(self.data, period=self.params.period)
    
    def next(self):
        if not self.position and self.plus_di > self.minus_di and self.adx > self.params.adx_threshold:
            self.buy()
        elif self.position and self.plus_di < self.minus_di:
            self.close()

class CCIStrategyBacktrader(BaseLogStrategy):
    '''
    CCI 順勢指標策略
    參數：period (20), upper (100), lower (-100)
    買進：CCI 向上穿越 -100 (脫離超賣區)
    賣出：CCI 向下穿越 100 (脫離超買區)
    '''
    params = (('period', 20), ('upper', 100), ('lower', -100))
    
    def __init__(self):
        super().__init__()
        self.cci = bt.ind.CCI(self.data, period=self.params.period)
    
    def next(self):
        if not self.position and self.cci > self.params.lower and self.cci[-1] < self.params.lower:
            self.buy()
        elif self.position and self.cci < self.params.upper and self.cci[-1] > self.params.upper:
            self.close()

class WilliamsRStrategyBacktrader(BaseLogStrategy):
    '''
    Williams %R 威廉指標策略
    參數：period (14), upper (-20), lower (-80)
    買進：%R < -80 (超賣)
    賣出：%R > -20 (超買)
    '''
    params = (('period', 14), ('upper', -20), ('lower', -80))
    
    def __init__(self):
        super().__init__()
        self.williams = bt.ind.WilliamsR(self.data, period=self.params.period)
    
    def next(self):
        if not self.position and self.williams < self.params.lower:
            self.buy()
        elif self.position and self.williams > self.params.upper:
            self.close()

class BollingerBandStrategyBacktrader(BaseLogStrategy):
    '''
    布林通道策略 (均值回歸)
    參數：period (20), devfactor (2.0)
    買進：收盤價跌破下通道 (預期反彈)
    賣出：收盤價突破上通道 (預期回檔)
    '''
    params = (('period', 20), ('devfactor', 2.0))
    
    def __init__(self):
        super().__init__()
        self.bb = bt.ind.BollingerBands(self.data.close, period=self.params.period, devfactor=self.params.devfactor)
    
    def next(self):
        if not self.position and self.data.close < self.bb.lines.bot:
            self.buy()
        elif self.position and self.data.close > self.bb.lines.top:
            self.close()

class ATRStrategyBacktrader(BaseLogStrategy):
    '''
    ATR 真實波幅策略 (波動率突破)
    參數：period (14), atr_mult (1.0)
    買進：收盤價 > 開盤價 + ATR * 倍數 (向上突破)
    賣出：收盤價 < 開盤價 - ATR * 倍數 (向下突破)
    '''
    params = (('period', 14), ('atr_mult', 1.0))
    
    def __init__(self):
        super().__init__()
        self.atr = bt.ind.ATR(self.data, period=self.params.period)
    
    def next(self):
        if not self.position and self.data.close > (self.data.open + self.atr * self.params.atr_mult):
            self.buy()
        elif self.position and self.data.close < (self.data.open - self.atr * self.params.atr_mult):
            self.close()

class DonchianChannelStrategyBacktrader(BaseLogStrategy):
    '''
    唐奇安通道策略 (趨勢突破)
    參數：period (20)
    買進：收盤價突破過去 N 日最高價
    賣出：收盤價跌破過去 N 日最低價
    '''
    params = (('period', 20),)
    
    def __init__(self):
        super().__init__()
        self.dc_high = bt.ind.Highest(self.data.high(-1), period=self.params.period)
        self.dc_low = bt.ind.Lowest(self.data.low(-1), period=self.params.period)
    
    def next(self):
        if not self.position and self.data.close > self.dc_high:
            self.buy()
        elif self.position and self.data.close < self.dc_low:
            self.close()

class VolumeStrategyBacktrader(BaseLogStrategy):
    '''
    成交量爆量策略
    參數：period (20), vol_mult (1.5)
    買進：收紅 K (收 > 開) 且 成交量 > 均量 * 1.5
    賣出：收黑 K (收 < 開) 且 成交量 > 均量 * 1.5
    '''
    params = (('period', 20), ('vol_mult', 1.5))
    
    def __init__(self):
        super().__init__()
        self.vol_ma = bt.ind.SMA(self.data.volume, period=self.params.period)
    
    def next(self):
        if not self.position and self.data.close > self.data.open and self.data.volume > self.vol_ma * self.params.vol_mult:
            self.buy()
        elif self.position and self.data.close < self.data.open and self.data.volume > self.vol_ma * self.params.vol_mult:
            self.close()

class VWAPStrategyBacktrader(BaseLogStrategy):
    '''
    VWAP 成交量加權平均價策略
    參數：period (20) - 這裡實作為滾動窗口 VWAP
    買進：收盤價 > VWAP
    賣出：收盤價 < VWAP
    '''
    params = (('period', 20),)
    
    def __init__(self):
        super().__init__()
        vp = self.data.close * self.data.volume
        self.vwap = bt.ind.SumN(vp, period=self.params.period) / bt.ind.SumN(self.data.volume, period=self.params.period)
    
    def next(self):
        if not self.position and self.data.close > self.vwap:
            self.buy()
        elif self.position and self.data.close < self.vwap:
            self.close()
