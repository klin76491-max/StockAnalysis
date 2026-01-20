""" 使用 python 抓取 0050 台灣股票 2025 ~2026 """
#%%
import yfinance as yf
import pandas as pd
import sqlite3
def saveData(db,table, symbol, start_date, end_date):
    """抓取股票資料並存入 sql lite 資料庫
    Args:
        db (str): sql lite 資料庫路徑
        table (str): 資料表名稱
        symbol (str): 股票代碼
        start_date (str): 起始日期 'YYYY-MM-DD'
        end_date (str): 結束日期 'YYYY-MM-DD'
    """
    # 抓取資料,column name 去除 0050.TW 前綴
    df = yf.download(symbol, start=start_date, end=end_date)
    
    # 處理欄位名稱: 保留欄位原始名稱
    df.columns = [col[0] for col in list(df.columns)]
    print(df.head())
    # 儲存為 sql lite 資料庫 在 data 資料夾下
    conn = sqlite3.connect(db)
    
    # 將 index 轉為欄位並確保為 datetime 格式
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    df.to_sql(table, conn, if_exists='replace', index=False)
    conn.close()

def checkData(db, table):
    """檢查 sql lite 資料庫資料是否成功匯入
    Args:
        db (str): sql lite 資料庫路徑
        table (str): 資料表名稱
    """
    conn = sqlite3.connect(db)
    # 檢查第一行資料
    print(pd.read_sql('SELECT * FROM '+table+' LIMIT 1', conn))
    # 關閉資料庫連線
    conn.close()

if __name__ == '__main__':
    # 設定參數
    symbol = '^TWII' # 大盤指數代碼
    symbol_name = 'TWII' # 用於檔名
    start_date = '1950-01-01' # 起始日期
    end_date = '2026-12-31' # 結束日期
    table = 'yfince'+'_'+symbol_name+'_'+start_date[0:4]+'_'+end_date[0:4] # 資料表名稱
    db = 'data/daily/stock_data.db' # 資料庫路徑
    # 執行存取資料與檢查
    saveData(db = db, table = table, symbol=symbol, start_date=start_date, end_date=end_date)
    checkData(db = db, table = table)

# %%
