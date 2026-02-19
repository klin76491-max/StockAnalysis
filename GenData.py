""" 使用 python 抓取 0050 台灣股票 2025 ~2026 """
#%%
import Infrastructure.Data.StockDataModel as model

if __name__ == '__main__':
    # 設定參數
    symbol = '^TWII' # yahoo fiance 股票參數
    symbol_name = 'TWII' # 用於檔名存檔
    start_date = '1950-01-01' # 起始日期
    end_date = '2026-12-31' # 結束日期
    table = 'DataYfince'+'_'+symbol_name+'_'+start_date[0:4]+'_'+end_date[0:4] # 資料表名稱
    db = 'DB/StockData.db' # 資料庫路徑
    
    # 執行存取資料與檢查
    model.save_stock_data(db_path=db, table_name=table, symbol=symbol, start_date=start_date, end_date=end_date)
    model.verify_stock_data(db_path=db, table_name=table)

# %%
