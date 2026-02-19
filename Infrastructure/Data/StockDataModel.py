from sqlalchemy import Float, Integer, DateTime, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from datetime import datetime
import pandas as pd
import yfinance as yf
import os

class Base(DeclarativeBase):
    pass

def get_stock_data_model(table_name: str):
    """動態建立 ORM 模型類別 Model """
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

def save_stock_data(db_path: str, table_name: str, symbol: str, start_date: str, end_date: str):
    """
    抓取 yahoo finance 股票資料並存入 SQLite 資料庫

    參數:
    db_path (str): 資料庫路徑
    table_name (str): 資料表名稱
    symbol (str): 股票代碼 (例如: '^TWII')
    start_date (str): 起始日期 (格式: 'YYYY-MM-DD')
    end_date (str): 結束日期 (格式: 'YYYY-MM-DD')
    """
    # 抓取資料
    df = yf.download(symbol, start=start_date, end=end_date)
    
    # 處理欄位名稱 (去除 MultiIndex)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    # 確保目錄存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 建立資料庫連線引擎
    engine = create_engine(f"sqlite:///{db_path}")
    
    # 處理資料
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    # 確保欄位存在，避免 yfinance 格式變動錯誤
    required_cols = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    df = df[[c for c in required_cols if c in df.columns]]
    
    dtype_mapping = {'Date': DateTime, 'Close': Float, 'High': Float, 'Low': Float, 'Open': Float, 'Volume': Integer}
    
    df.to_sql(table_name, engine, if_exists='replace', index=False, dtype=dtype_mapping)
    print(f"資料已儲存至 {db_path} 的 {table_name} 資料表")

def verify_stock_data(db_path: str, table_name: str):
    """
    驗證資料庫資料是否成功匯入

    參數:
    db_path (str): 資料庫路徑
    table_name (str): 資料表名稱
    """
    if not os.path.exists(db_path):
        print(f"錯誤: 資料庫檔案不存在 {db_path}")
        return

    engine = create_engine(f"sqlite:///{db_path}")
    StockData = get_stock_data_model(table_name)
    
    with Session(engine) as session:
        stmt = select(StockData).limit(1)
        result = session.scalars(stmt).first()
        print(f"資料表 {table_name} 第一筆資料 (ORM): {result}")