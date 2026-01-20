# StockAnalysis - 股票回測分析系統

一個基於MA5/MA20黃金交叉策略的自動化股票回測平台，針對台灣加權指數進行歷史數據回測。

## 主要功能

- **GenData**: 通過yfinance API自動抓取股票數據，進行標準化處理後存儲至SQLite數據庫
- **Query**: 根據時間範圍從數據庫提取篩選後的OHLCV數據
- **Strategy**: 實現MA5/MA20黃金交叉策略，執行交易信號生成與持倉管理
- **main.py**: 整合各模組流程，輸出詳細績效指標與互動式HTML報告

## 快速開始

```bash
# 安裝依賴 (使用conda)
conda create --name stockanalysis --file package-list.txt
conda activate stockanalysis

# 執行回測
python main.py
```

## 回測結果

- 初始資金: $100,000
- 時間範圍: 2025-10-05 ~ 2027-01-01
- 輸出: backtest_result.html (互動式圖表報告)

## 績效指標

| 指標 | 說明 |
|-----|------|
| 總報酬率 | 投資回報百分比 |
| 年化報酬率 | 年均報酬率 |
| 最大回撤 | 從最高點到最低點的跌幅 |
| 勝率 | 盈利交易比例 |
| 夏普比例 | 風險調整後的報酬 |
| 獲利因子 | 總利潤與總虧損比 |

## 項目結構

```
├── GenData/          # 數據準備層
├── Query/            # 數據查詢層
├── Strategy/         # 策略執行層
├── main.py           # 主控制程序
└── backtest_result.html  # 回測報告
```

## 技術棧

- Python 3.x
- yfinance (數據下載)
- pandas (數據處理)
- sqlite3 (數據庫)
- backtesting.py (回測框架)