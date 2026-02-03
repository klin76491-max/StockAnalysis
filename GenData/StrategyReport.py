#%%
from sqlalchemy import create_engine, String, Float, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import os
from typing import Optional

class Base(DeclarativeBase):
    pass

class BacktestResult(Base):
    """
    回測結果資料模型 (Data Model)
    對應資料庫 backtest_results 資料表的欄位
    使用 SQLAlchemy ORM 定義
    """
    __tablename__ = 'backtest_results'

    # 自動生成欄位 (Primary Key)
    run_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 必填欄位
    strategy_name: Mapped[str] = mapped_column(String)          # 2. 策略名稱
    symbol: Mapped[str] = mapped_column(String)                 # 3. 標的代碼
    timeframe: Mapped[str] = mapped_column(String)              # 4. 資料週期
    start_date: Mapped[str] = mapped_column(String)             # 5. 回測開始日期
    end_date: Mapped[str] = mapped_column(String)               # 6. 回測結束日期
    initial_capital: Mapped[float] = mapped_column(Float)       # 10. 初始資金
    total_return: Mapped[float] = mapped_column(Float)          # 11. 總報酬率
    max_drawdown: Mapped[float] = mapped_column(Float)          # 13. 最大回撤
    sharpe_ratio: Mapped[float] = mapped_column(Float)          # 14. 夏普比率
    trade_count: Mapped[int] = mapped_column(Integer)           # 15. 交易次數
    win_rate: Mapped[float] = mapped_column(Float)              # 16. 勝率
    commission_rate: Mapped[float] = mapped_column(Float)       # 17. 手續費率
    slippage: Mapped[float] = mapped_column(Float)              # 18. 滑價假設
    parameter_note: Mapped[str] = mapped_column(Text)           # 19. 策略參數摘要
    
    # 可為空值的欄位 (Optional)
    first_entry_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)    # 7. 最初實際進場時間
    last_exit_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)      # 8. 最後一次平倉時間
    total_holding_times: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)# 9. 總持有時間
    annual_return: Mapped[Optional[float]] = mapped_column(Float, nullable=True)      # 12. 年化報酬率

def save_backtest_result(db_path: str, result: BacktestResult):
    """
    將回測結果儲存至 SQLite 資料庫 (使用 SQLAlchemy)。
    如果資料表不存在，會自動建立。

    Args:
        db_path (str): SQLite 資料庫檔案路徑 (例如: 'Report/backtest_results.db')
        result (BacktestResult): 包含回測數據的資料模型物件
    """
    # 確保資料庫目錄存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 建立資料庫連線引擎
    # 注意：Windows 路徑可能需要處理，這裡假設相對路徑或標準路徑
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    
    # 建立資料表 (如果不存在)
    Base.metadata.create_all(engine)
    
    # 使用 Session 儲存資料
    with Session(engine) as session:
        session.add(result)
        session.commit()
        print(f"回測結果已成功儲存至: {db_path}")

if __name__ == '__main__':
    # 建立測試資料
    test_result = BacktestResult(
        strategy_name='TestStrategy',
        symbol='AAPL',
        timeframe='daily',
        start_date='2023-01-01',
        end_date='2023-12-31',
        initial_capital=10000,
        total_return=0.05,
        max_drawdown=-0.1,
        sharpe_ratio=1,
        trade_count=10,
        win_rate=0.7,
        commission_rate=0.001,
        slippage=0.002,
        parameter_note='Test parameters',
        first_entry_date='2023-01-05',
        last_exit_date='2023-12-30',
        total_holding_times=365,
        annual_return=0.04
    )
    save_backtest_result('report/daily/backtest_results.db', test_result)
# %%