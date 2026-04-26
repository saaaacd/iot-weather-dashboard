# 🌤️ 台灣氣溫雙模式綜合儀表板 (IoT Weather Dashboard)

此專案為物聯網應用開發之一環，完整實作了**從政府開放資料 (Open Data) 擷取、資料重構、關聯式資料庫儲存到前端資料視覺化**的 End-to-End 開發流程。

藉由自動化腳本分析龐大的氣象預報數據，並打造一個具有 Google 質感的動態 Web App，讓使用者能直觀地查詢台灣各大分區的一週氣溫趨勢。

## 🌟 核心特色 (Features)
- 📡 **氣象署 API 串接**：自動抓取並解析 [交通部中央氣象署](https://opendata.cwa.gov.tw/) 的 F-A0010-001 資料集 (JSON 格式)。
- 🧹 **資料清洗與提煉**：雙層迴圈解析複雜樹狀結構，精準洗出每日「最高溫 (MaxT)」與「最低溫 (MinT)」。
- 🗄️ **SQLite3 持久化儲存**：全自動建立 `data.db` 資料庫與正規化表單，透過 SQL 語法進行安全的參數綁定寫入。
- 📊 **Streamlit 雙模式儀表板**：透過 Tabs 切換「依地區看一週趨勢」與「依日期看全台動態」雙系統。
- 🗺️ **Folium 互動式地理圖**：整合 `streamlit-folium`，將氣溫數據與真實經緯度結合，打上紅藍氣溫地標，點擊可顯示深入資訊的 Popup。

---

## 🛠️ 開發環境與技術棧 (Tech Stack)
- **語言**：Python 3.8+
- **後端與資料庫**：SQLite3, `requests`
- **資料處理**：`pandas`, `json`
- **前端視覺化與空間地理(GIS)**：`streamlit`, `folium`, `streamlit-folium`

---

## 🚀 如何啟動本專案 (Getting Started)

### 1. 安裝所需套件
請確保你的環境中已安裝所需框架：
```bash
pip install requests pandas streamlit folium streamlit-folium
```

### 2. 執行資料流腳本
依序執行以下腳本，將資料從 CWA API 抓取下來並寫入資料庫：
```bash
# 抓取原始資料 (會生成 weather_forecast_data.json)
python hw2_1_weather.py

# 提取最高/低溫特徵 (會生成 extracted_temperatures.json)
python hw2_2_extract_temp.py

# 寫入資料庫 (會建立 data.db 並完成驗證)
python hw2_3_db_insert.py
```

### 3. 啟動 Web 儀表板
最後，透過 Streamlit 啟動網頁伺服器：
```bash
streamlit run hw2_4_streamlit_app.py
```
啟動後瀏覽器會自動彈出 `http://localhost:8501`。

---

## 📂 資料夾結構 (Folder Structure)
```
📁 iotHW2
│
├── hw2_1_weather.py           # 向 CWA API 發送 GET 請求
├── hw2_2_extract_temp.py      # 解析 JSON 並提煉溫度特徵
├── hw2_3_db_insert.py         # 將特徵資料寫入 SQLite 關聯式資料庫
├── hw2_4_streamlit_app.py     # Streamlit 網頁應用與圖表渲染
│
├── weather_forecast_data.json # (Auto-generated) 原始 API 資料
├── extracted_temperatures.json# (Auto-generated) 清洗後的資料
└── data.db                    # (Auto-generated) SQLite 資料庫
```
