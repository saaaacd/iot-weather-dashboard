import sqlite3
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

# 台灣各大分區的大致經緯度座標字典
REGION_COORDS = {
    "北部地區": [25.0330, 121.5654],
    "中部地區": [24.1477, 120.6736],
    "南部地區": [22.9999, 120.2269],
    "東北部地區": [24.7088, 121.7511],
    "東部地區": [23.9754, 121.5979],
    "東南部地區": [22.7554, 121.1444]
}

def load_all_regions(db_name):
    """取得資料庫中所有不重複的地區名稱"""
    conn = sqlite3.connect(db_name)
    query = "SELECT DISTINCT regionName FROM TemperatureForecasts"
    df_regions = pd.read_sql_query(query, conn)
    conn.close()
    return df_regions['regionName'].tolist()

def load_all_dates(db_name):
    """取得資料庫中所有不重複的日期"""
    conn = sqlite3.connect(db_name)
    query = "SELECT DISTINCT dataDate FROM TemperatureForecasts ORDER BY dataDate ASC"
    df_dates = pd.read_sql_query(query, conn)
    conn.close()
    return df_dates['dataDate'].tolist()

def load_temperature_data_by_region(db_name, region_name):
    """取得特定地區的一週氣溫預報"""
    conn = sqlite3.connect(db_name)
    query = 'SELECT dataDate, MinT, MaxT FROM TemperatureForecasts WHERE regionName = ?'
    df_weather = pd.read_sql_query(query, conn, params=(region_name,))
    conn.close()
    return df_weather

def load_data_by_date(db_name, target_date):
    """取得特定日期下，所有地區的氣溫預報"""
    conn = sqlite3.connect(db_name)
    query = 'SELECT regionName, MinT, MaxT FROM TemperatureForecasts WHERE dataDate = ?'
    df = pd.read_sql_query(query, conn, params=(target_date,))
    conn.close()
    return df

def main():
    # 將 Layout 設為 wide 讓地圖與雙系統有更寬廣的空間
    st.set_page_config(page_title="台灣氣象綜合儀表板", page_icon="🌤️", layout="wide")
    
    # 漂亮的大標題
    st.markdown("""
        <h1 style='text-align: center; background: linear-gradient(90deg, #1CB5E0 0%, #000851 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🌤️ 台灣氣溫雙模式綜合儀表板</h1>
        <p style='text-align: center; color: gray;'>點擊下方分頁標籤，自由切換「依地區看一週趨勢」或「依日期看全台地圖」</p>
    """, unsafe_allow_html=True)
    st.divider()

    DB_NAME = "data.db"
    
    try:
        # ⭐️ 核心魔法：使用 Streamlit 的 Tabs 建立無縫切換按鈕
        tab1, tab2 = st.tabs(["📈 模式一：分區一週趨勢查詢系統", "🗺️ 模式二：全台單日動態地圖系統"])
        
        # ==========================================
        # 分頁一：保留我們精心設計的一週趨勢與自選顏色系統
        # ==========================================
        with tab1:
            regions = load_all_regions(DB_NAME)
            if not regions:
                st.error("資料庫中沒有地區資料！")
            else:
                st.markdown("### 📌 選擇關注的地區")
                selected_region = st.selectbox("請選擇 (Select a Region)", regions, key="region_select")
                
                df_region_data = load_temperature_data_by_region(DB_NAME, selected_region)
                
                # 計算極值顯示看板
                max_of_week = df_region_data['MaxT'].max()
                min_of_week = df_region_data['MinT'].min()
                
                c1, c2, c3 = st.columns(3)
                c1.metric(label="一週最高溫", value=f"{max_of_week} °C", delta="炎熱注意" if max_of_week >= 30 else "")
                c2.metric(label="一週最低溫", value=f"{min_of_week} °C", delta="保暖注意" if min_of_week <= 20 else "", delta_color="inverse")
                c3.metric(label="監測天數", value=f"{len(df_region_data)} 天")
                
                # 把側邊欄的顏色選擇器拉回來這個分頁裡面！
                st.markdown("##### 🎨 自訂折線圖顏色")
                c_min, c_max = st.columns(2)
                with c_min: min_color = st.color_picker("選擇最低溫 (MinT) 的顏色", "#1E88E5", key="color_min")
                with c_max: max_color = st.color_picker("選擇最高溫 (MaxT) 的顏色", "#D81B60", key="color_max")

                df_chart_data = df_region_data.set_index('dataDate')
                
                try:
                    st.line_chart(df_chart_data, color=[min_color, max_color]) 
                except TypeError:
                    st.line_chart(df_chart_data)
                    
                st.dataframe(
                    df_region_data, 
                    use_container_width=True,
                    column_config={
                        "dataDate": st.column_config.TextColumn("📅 日期"),
                        "MinT": st.column_config.NumberColumn("❄️ 最低溫 (°C)"),
                        "MaxT": st.column_config.NumberColumn("🔥 最高溫 (°C)")
                    }
                )

        # ==========================================
        # 分頁二：全新的 Folium 動態地圖與長條圖對比系統
        # ==========================================
        with tab2:
            available_dates = load_all_dates(DB_NAME)
            if not available_dates:
                st.error("找不到日期資料！")
            else:
                st.markdown("### 📅 選擇要查看預報的日期")
                selected_date = st.selectbox("請選擇 (Date Selector)", available_dates, key="date_select")
                
                df_daily = load_data_by_date(DB_NAME, selected_date)
                
                # 左右分割 Layout
                col_left, col_right = st.columns([1, 1], gap="large")
                
                with col_left:
                    st.markdown("#### 📍 互動式台灣氣溫地圖")
                    m = folium.Map(location=[23.7, 120.9], zoom_start=7, tiles="CartoDB positron")
                    for idx, row in df_daily.iterrows():
                        region = row['regionName']
                        if region in REGION_COORDS:
                            popup_content = f"<b>{region}</b><br>最高溫: {row['MaxT']}°C<br>最低溫: {row['MinT']}°C"
                            folium.Marker(
                                location=REGION_COORDS[region],
                                popup=folium.Popup(popup_content, max_width=200),
                                tooltip=f"點擊查看 {region}",
                                icon=folium.Icon(color="red" if row['MaxT'] >= 30 else "blue", icon="info-sign")
                            ).add_to(m)
                    
                    st_folium(m, width="100%", height=450)
                    
                with col_right:
                    st.markdown("#### 📋 各區高低溫對比長條圖")
                    df_chart = df_daily.set_index('regionName')
                    st.bar_chart(df_chart[['MinT', 'MaxT']], color=["#1E88E5", "#D81B60"])
                    
                    st.markdown("#### 📊 當日氣溫詳細表格")
                    st.dataframe(
                        df_daily,
                        use_container_width=True,
                        column_config={
                            "regionName": st.column_config.TextColumn("📌 地區"),
                            "MinT": st.column_config.NumberColumn("❄️ 最低溫 (°C)", format="%d °C"),
                            "MaxT": st.column_config.NumberColumn("🔥 最高溫 (°C)", format="%d °C")
                        }
                    )

    except sqlite3.Error as e:
        st.error(f"資料庫讀取失敗：{e}")

if __name__ == "__main__":
    main()
