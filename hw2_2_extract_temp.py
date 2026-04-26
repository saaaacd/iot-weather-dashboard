import json
import sys
import os

def extract_temperature_data(input_file):
    """
    從完整的天氣預報 JSON 檔案中，分析並提取各地區的最高與最低氣溫資料。
    
    Args:
        input_file (str): 準備讀取的原始 JSON 檔案路徑。
    """
    if not os.path.exists(input_file):
        print(f"找不到檔案 {input_file}，請先執行 HW2-1 的程式產生資料檔案。")
        sys.exit(1)
        
    try:
        # 1. 讀取原始 JSON 檔案
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        print("成功讀取原始資料，開始分析與提取氣溫資訊...\n")
        
        # 2. 定位到氣象資料的陣列位置
        # JSON 結構路徑: cwaopendata -> resources -> resource -> data -> agrWeatherForecasts -> weatherForecasts -> location
        locations = data["cwaopendata"]["resources"]["resource"]["data"]["agrWeatherForecasts"]["weatherForecasts"]["location"]
        
        # 準備一個清單用來存放提煉過後的資料
        extracted_data = []

        # 3. 尋訪每一個地區並提取所需的欄位
        for loc in locations:
            location_name = loc.get("locationName")
            
            # 從 weatherElements 中精準提取最高溫 (MaxT) 與最低溫 (MinT) 的每日資料陣列
            max_t_daily = loc["weatherElements"]["MaxT"]["daily"]
            min_t_daily = loc["weatherElements"]["MinT"]["daily"]
            
            # 我們將這個地區的天氣按照日期組合起來
            daily_temperatures = []
            
            for i in range(len(max_t_daily)):
                date = max_t_daily[i]["dataDate"]
                max_temp = max_t_daily[i]["temperature"]
                min_temp = min_t_daily[i]["temperature"]
                
                daily_temperatures.append({
                    "Date": date,
                    "Max_Temp_C": max_temp,
                    "Min_Temp_C": min_temp
                })
                
            # 將地區與排好的溫度整理為一個新的結構
            extracted_data.append({
                "Location": location_name,
                "Temperatures": daily_temperatures
            })

        # 4. 使用 json.dumps 觀察並儲存提取後的全新精簡資料
        formatted_extracted_data = json.dumps(extracted_data, indent=4, ensure_ascii=False)
        
        print("=== 提取後的氣溫資料預覽 ===")
        print(formatted_extracted_data)
        print("============================\n")
        
        # 將提煉出的精華資料儲存到新檔案，方便助教/後續功能查看
        output_file = "extracted_temperatures.json"
        with open(output_file, "w", encoding="utf-8") as out_file:
            out_file.write(formatted_extracted_data)
            
        print(f"氣溫提取完成！精簡後的資料已儲存至：{output_file}")
        
    except json.JSONDecodeError:
        print("無法解析 JSON 格式，檔案可能已損壞。")
    except KeyError as e:
        print(f"分析資料失敗！找不到預期的 JSON 鍵值：{e}。這代表官方資料結構可能有變更。")
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")

if __name__ == "__main__":
    # 使用 HW2-1 儲存的檔案做為輸入來源
    INPUT_FILE = "weather_forecast_data.json"
    extract_temperature_data(INPUT_FILE)
