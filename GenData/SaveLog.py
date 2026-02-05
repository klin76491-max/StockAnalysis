from sqlalchemy import create_engine, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import os
import pandas as pd

class Base(DeclarativeBase):
    pass

class TradeLog(Base):
    """
    交易紀錄資料模型
    對應資料庫 trade_logs 資料表的欄位
    """
    __tablename__ = 'trade_logs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    backtest_uuid: Mapped[str] = mapped_column(String, index=True) # 連結 BacktestResult 的 UUID
    
    # 對應 main.py 中 trades DataFrame 的欄位
    Time: Mapped[str] = mapped_column(String)
    TransactionAction: Mapped[str] = mapped_column(String)
    ExecutionPrice: Mapped[float] = mapped_column(Float)
    ClosingPriceExecutionDay: Mapped[float] = mapped_column(Float)
    OpeningPriceExecutionDay: Mapped[float] = mapped_column(Float)
    ClosingPriceBeforeExecutionDay: Mapped[float] = mapped_column(Float)
    OpeningPriceBeforeExecutionDay: Mapped[float] = mapped_column(Float)
    CurrentFunds: Mapped[float] = mapped_column(Float)

def save_trade_logs(db_path: str, trades_df: pd.DataFrame, backtest_uuid: str):
    """
    將交易紀錄儲存至 SQLite 資料庫
    """
    if trades_df.empty:
        return

    # 確保資料庫目錄存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    
    # 建立資料表 (如果不存在)
    Base.metadata.create_all(engine)
    
    # 將 DataFrame 轉換為 ORM 物件列表
    logs = []
    for _, row in trades_df.iterrows():
        # 將 row 轉為字典並過濾掉不在模型中的欄位 (如果有額外欄位的話)
        # 這裡直接使用欄位對應
        row_data = row.to_dict()
        row_data['Time'] = str(row_data['Time']) # 確保時間轉為字串
        log = TradeLog(backtest_uuid=backtest_uuid, **row_data)
        logs.append(log)
    
    with Session(engine) as session:
        session.add_all(logs)
        session.commit()
        print(f"交易紀錄已成功儲存至: {db_path}")
