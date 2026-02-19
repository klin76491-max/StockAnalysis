import pandas as pd
import sqlite3
def GetData(db, table, from_date, to_date):
    """從 sql lite 資料庫取得資料
    Args:
        db (str): sql lite 資料庫路徑
        table (str): 資料表名稱
        start_date (str): 起始日期 'YYYY-MM-DD'
        end_date (str): 結束日期 'YYYY-MM-DD'"""
    conn = sqlite3.connect(db)
    # 讀取大盤資料 df_twii 20230102 ~ 20261231
    df_twii = pd.read_sql("SELECT * FROM "+ table +" where Date between '"+ from_date +"' and '"+ to_date +"';", 
                          conn, index_col='Date', 
                          parse_dates=['Date'])
    conn.close()
    return df_twii

def getTableList(db):
    """取得資料庫中的所有資料表名稱
    Args:
        db (str): sql lite 資料庫路徑
    Returns:
        list: 資料表名稱列表
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables