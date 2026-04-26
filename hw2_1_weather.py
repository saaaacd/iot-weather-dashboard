import requests
import json
import os
import sys

def fetch_weather_forecast(api_key):
    """
    調用 CWA (中央氣象署) API 獲取指定資料集的天氣預報資料。
    資料集 ID: F-A0010-001 (包含農漁業氣象預報，涵蓋各分區溫度等預報資訊)
    
    Args:
        api_key (str): 從氣象資料開放平臺取得的 Authorization key。
    """
    # F-A0010-001 是屬於 fileapi 類別
    dataset_id = "F-A0010-001"
    url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/{dataset_id}"
    
    # 設定要傳遞的參數 (查詢字串)
    params = {
        "Authorization": api_key,
        "format": "JSON"
    }
    
    try:
        print("正在向 CWA API 發送請求...")
        response = requests.get(url, params=params)
        
        # 檢查 HTTP 狀態碼
        if response.status_code == 200:
            print("請求成功！")
            data = response.json()
            
            # 使用 json.dumps 觀察獲得的資料，設定 indent=4 增加可讀性，並處理中文字元顯示
            formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
            
            # 因為資料可能非常龐大，我們這裡示範印出前 1000 個字元作為觀察，
            # 同時也將完整的資料寫入檔案供詳細觀察。
            print("\n=== 獲取資料預覽 (前 1000 字元) ===")
            print(formatted_data[:1000])
            print("===================================\n")
            
            # 將完整資料儲存至 JSON 檔案中，方便觀察全部內容
            output_file = "weather_forecast_data.json"
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(formatted_data)
                
            print(f"完整天氣預報資料已儲存至：{output_file}")
            
        else:
            print(f"請求失敗，HTTP 狀態碼: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"發送請求時發生錯誤: {e}")

if __name__ == "__main__":
    # 將您的 CWA API 授權碼放在這裡
    API_KEY = "CWA-58E0838C-5211-43C9-BDEF-F0A61751DC70"  # 請替換成您申請的授權碼
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("請先將程式碼中的 API_KEY 換成您自己在中央氣象署申請的授權碼！")
        sys.exit(1)
        
    fetch_weather_forecast(API_KEY)
