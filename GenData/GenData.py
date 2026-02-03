""" 使用 python 抓取 0050 台灣股票 2025 ~2026 """
#%%
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, Float, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import select
from datetime import datetime
import os

class Base(DeclarativeBase):
    pass

def get_stock_data_model(table_name: str):
    """動態建立 ORM 模型類別"""
    class StockData(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        
        Date: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
        Close: Mapped[float] = mapped_column(Float)
        High: Mapped[float] = mapped_column(Float)
        Low: Mapped[float] = mapped_column(Float)
        Open: Mapped[float] = mapped_column(Float)
        Volume: Mapped[int] = mapped_column(Integer)
        
        def __repr__(self):
            return f"<StockData(Date={self.Date}, Close={self.Close})>"
    return StockData

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
    
    # 確保目錄存在
    os.makedirs(os.path.dirname(db), exist_ok=True)
    
    # 建立資料庫連線引擎
    engine = create_engine(f"sqlite:///{db}")
    
    # 將 index 轉為欄位並確保為 datetime 格式
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 篩選並排序欄位 (符合 ORM 定義)
    df = df[['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]
    
    # 定義欄位型態映射
    dtype_mapping = {
        'Date': DateTime,
        'Close': Float,
        'High': Float,
        'Low': Float,
        'Open': Float,
        'Volume': Integer
    }
    
    df.to_sql(table, engine, if_exists='replace', index=False, dtype=dtype_mapping)
    print(f"資料已儲存至 {db} 的 {table} 資料表")

def checkData(db, table):
    """檢查 sql lite 資料庫資料是否成功匯入
    Args:
        db (str): sql lite 資料庫路徑
        table (str): 資料表名稱
    """
    engine = create_engine(f"sqlite:///{db}")
    StockData = get_stock_data_model(table)
    
    with Session(engine) as session:
        stmt = select(StockData).limit(1)
        result = session.scalars(stmt).first()
        print(f"資料表 {table} 第一筆資料 (ORM):")
        print(result)

if __name__ == '__main__':
    # 設定參數
    symbol = '^TWII' # 大盤指數代碼
    symbol_name = 'TWII' # 用於檔名
    start_date = '1950-01-01' # 起始日期
    end_date = '2026-12-31' # 結束日期
    table = 'yfince'+'_'+symbol_name+'_'+start_date[0:4]+'_'+end_date[0:4] # 資料表名稱
    db = 'data/daily/stock_data1.db' # 資料庫路徑
    # 執行存取資料與檢查
    saveData(db = db, table = table, symbol=symbol, start_date=start_date, end_date=end_date)
    checkData(db = db, table = table)

# %%
