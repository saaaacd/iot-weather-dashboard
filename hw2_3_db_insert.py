import json
import sqlite3
import os
import sys

def create_database_and_table(db_name):
    """
    連接資料庫並建立所需的 TemperatureForecasts 資料表。
    如果資料表已存在則會先清除避免重複插入。
    """
    print(f"正在連接 SQLite3 資料庫: {db_name}")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 建立資料表，欄位對應 Homework 要求與範例圖
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TemperatureForecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT NOT NULL,
            dataDate TEXT NOT NULL,
            MaxT INTEGER NOT NULL,
            MinT INTEGER NOT NULL
        )
    ''')
    
    # 為了作業重複執行方便，先清空舊資料（如果不清空，每次執行資料會越疊越多）
    cursor.execute('DELETE FROM TemperatureForecasts')
    
    conn.commit()
    return conn, cursor

def insert_data_to_db(conn, cursor, json_file):
    """
    從 JSON 讀取資料並將每一筆氣溫紀錄匯入資料庫。
    """
    if not os.path.exists(json_file):
        print(f"錯誤：找不到 {json_file}，請先執行 HW2-2。")
        sys.exit(1)
        
    # 讀取 HW2-2 萃取出來的氣溫資料
    with open(json_file, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
        
    print("開始將氣溫資料寫入資料庫...")
    
    # 逐筆解析字典物件並插入資料庫
    for region_data in extracted_data:
        regionName = region_data["Location"]
        for temp_record in region_data["Temperatures"]:
            dataDate = temp_record["Date"]
            max_t = int(temp_record["Max_Temp_C"])
            min_t = int(temp_record["Min_Temp_C"])
            
            # 使用 ? 作為參數綁定，防止 SQL Injection
            cursor.execute('''
                INSERT INTO TemperatureForecasts (regionName, dataDate, MaxT, MinT)
                VALUES (?, ?, ?, ?)
            ''', (regionName, dataDate, max_t, min_t))
            
    # 儲存變更
    conn.commit()
    print("資料寫入完成！\n")

def verify_and_query_data(cursor):
    """
    執行 SQL 查詢來驗證資料是否正確存入，符合作業的查詢驗證要求。
    """
    print("=== 資料庫查詢驗證 ===")
    
    # 查詢要求 1：列出所有地區名稱
    print("1. 查詢所有地區名稱：")
    # 使用 DISTINCT 來確保列出的地區名稱不重複
    cursor.execute('SELECT DISTINCT regionName FROM TemperatureForecasts')
    regions = cursor.fetchall()
    
    # 將查詢結果 tuple 中抽出文字並印出
    region_names = [row[0] for row in regions]
    print(f"共找到 {len(region_names)} 個地區：", ", ".join(region_names))
    
    print("\n--------------------------")
    
    # 查詢要求 2：列出中部地區的氣溫資料
    print("2. 查詢「中部地區」的天氣預報資料：")
    cursor.execute('''
        SELECT id, regionName, dataDate, MaxT, MinT 
        FROM TemperatureForecasts 
        WHERE regionName = '中部地區'
    ''')
    central_weather = cursor.fetchall()
    
    # 參考提供的範例圖排版印出查詢結果
    print(f"{'id':<5} | {'regionName':<10} | {'dataDate':<12} | {'MaxT':<5} | {'MinT':<5}")
    print("-" * 50)
    for row in central_weather:
        # row: (id, regionName, dataDate, MaxT, MinT)
        print(f"{row[0]:<5} | {row[1]:<10} | {row[2]:<12} | {row[3]:<5} | {row[4]:<5}")
        
    print("======================\n")

if __name__ == "__main__":
    DB_NAME = "data.db"
    JSON_INPUT_FILE = "extracted_temperatures.json"
    
    try:
        # Step 1: 建立資料庫連線與表格
        conn, cursor = create_database_and_table(DB_NAME)
        
        # Step 2: 執行資料插入
        insert_data_to_db(conn, cursor, JSON_INPUT_FILE)
        
        # Step 3: 從資料庫查詢檢驗儲存結果
        verify_and_query_data(cursor)
        
    except sqlite3.Error as e:
        print(f"資料庫操作發生錯誤: {e}")
    finally:
        # Step 4: 清理並關閉連線
        print(f"關閉資料庫連線。資料已儲存至 {DB_NAME}")
        if conn:
            conn.close()
