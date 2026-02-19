import os

def ensure_directory_exists(directory_path):
    """
    檢查目錄是否存在，若不存在則建立該目錄。

    參數:
    directory_path (str): 目錄路徑
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"目錄已建立: {directory_path}")
