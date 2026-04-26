import sqlite3
import pandas as pd
import streamlit as st

def load_all_regions(db_name):
    """
    從資料庫中取得所有不重複的地區名稱，用作下拉式選單的選項。
    """
    conn = sqlite3.connect(db_name)
    query = "SELECT DISTINCT regionName FROM TemperatureForecasts"
    df_regions = pd.read_sql_query(query, conn)
    conn.close()
    return df_regions['regionName'].tolist()

def load_temperature_data_by_region(db_name, region_name):
    """
    根據使用者選擇的地區，從關聯式資料庫取出對應的溫度預報資料。
    """
    conn = sqlite3.connect(db_name)
    query = '''
        SELECT dataDate, MinT, MaxT 
        FROM TemperatureForecasts 
        WHERE regionName = ?
    '''
    df_weather = pd.read_sql_query(query, conn, params=(region_name,))
    conn.close()
    return df_weather

def main():
    # 1. 設定 Web App 標題、圖示與版面寬度
    st.set_page_config(page_title="氣溫預報 Web App", page_icon="🌤️", layout="centered")
    
    # 2. 注入自訂 CSS 來美化全域字體與漸層標題
    st.markdown("""
    <style>
    .gradient-text {
        background: linear-gradient(90deg, #1CB5E0 0%, #000851 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8em;
        font-weight: 800;
        margin-bottom: 0px;
    }
    /* 針對黑灰主題特別調配的漸層，如果在 dark mode 也會很漂亮 */
    @media (prefers-color-scheme: dark) {
        .gradient-text {
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # 美化的漸層大標題與引言
    st.markdown('<p class="gradient-text">🌤️ 台灣氣溫預報儀表板</p>', unsafe_allow_html=True)
    st.markdown("透過自動化擷取，為您動態視覺化呈現台灣各大分區的一週氣象趨勢。")
    st.divider() # 加入分隔線裝飾
    
    DB_NAME = "data.db"
    
    try:
        regions = load_all_regions(DB_NAME)
        if not regions:
            st.error("資料庫中沒有地區資料，請先檢查 HW2-3 資料庫是否有正確建立！")
            return
            
        # 3. 實作「下拉選單功能」(對應作業評分要求) 加入 Emoji 點綴
        selected_region = st.selectbox("📌 選擇您關注的地區 (Select a Region)", regions)
        
        df_region_data = load_temperature_data_by_region(DB_NAME, selected_region)
        df_chart_data = df_region_data.set_index('dataDate')
        
        # --- 美化亮點：計算一週極值並用 Metric 指標顯示 ---
        max_of_week = df_region_data['MaxT'].max()
        min_of_week = df_region_data['MinT'].min()
        
        # 使用排版分出三個區塊，建立像是天氣 APP 頂端的 Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="一週最高溫", value=f"{max_of_week} °C", delta="炎熱注意" if max_of_week >= 30 else "")
        with col2:
            st.metric(label="一週最低溫", value=f"{min_of_week} °C", delta="保暖注意" if min_of_week <= 20 else "", delta_color="inverse")
        with col3:
            st.metric(label="監測天數", value=f"{len(df_region_data)} 天", delta="1-Week")
            
        st.divider()

        # 4. 美化的雙線折線圖 (對應作業評分要求)
        st.markdown(f"### 📈 Temperature Trends for {selected_region}")
        st.caption("你可以在左側邊欄展開來自己改變你喜歡的線條顏色喔！")
        
        # 開放讓使用者自訂折線圖顏色 (透過側邊欄)
        st.sidebar.markdown("### 🎨 自訂折線圖顏色")
        min_color = st.sidebar.color_picker("選擇最低溫 (MinT) 的顏色", "#1E88E5")
        max_color = st.sidebar.color_picker("選擇最高溫 (MaxT) 的顏色", "#D81B60")
        st.sidebar.markdown("---")
        st.sidebar.caption("調整上方的顏色，右邊的折線圖會即時變化！")
        
        # 利用 Streamlit 的 color 參數設定使用者自訂的顏色
        try:
            st.line_chart(df_chart_data, color=[min_color, max_color]) 
        except TypeError:
            # 相容無法指定顏色的舊版 Streamlit
            st.line_chart(df_chart_data)
            
        st.divider()
        
        # 5. 美化的資料表格 (對應作業評分要求)
        st.markdown(f"### 📋 Temperature Data for {selected_region}")
        st.caption("詳細的每日觀測數值報表")
        
        # 使用 column_config 幫表格的預設欄位加上中文、Emoji 與單位，看起來超級專業
        st.dataframe(
            df_region_data, 
            use_container_width=True,
            column_config={
                "dataDate": st.column_config.TextColumn("📅 日期 (Date)"),
                "MinT": st.column_config.NumberColumn("❄️ 最低溫 (°C)", format="%d °C"),
                "MaxT": st.column_config.NumberColumn("🔥 最高溫 (°C)", format="%d °C")
            }
        )
        
    except sqlite3.Error as e:
        st.error(f"資料庫連線錯誤，請確認 data.db 檔案與結構是否正確: {e}")
    except Exception as e:
        st.error(f"發生不可預期的錯誤: {e}")

if __name__ == "__main__":
    main()
