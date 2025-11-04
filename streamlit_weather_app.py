import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="🌤️ 날씨 아트워크", layout="wide")

st.title("🌤️ Artwork Weather App")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("OpenWeatherMap API 키", type="password")
    city = st.text_input("도시 이름 (예: Seoul,KR)", "Seoul,KR")
    units = st.selectbox("단위", ("metric", "imperial"), index=0)
    cnt_hours = st.slider("예보 기간 (시간)", 24, 120, 72, step=3)
    st.caption("무료 OpenWeatherMap API 키 필요합니다 👉 https://openweathermap.org/api")

if not api_key:
    st.warning("55ef195c90b3f878d44217319b98cded")
    st.stop()

# --- Geocoding ---
def geocode_city(city_name, api_key):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city_name, "limit": 1, "appid": api_key}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    if not data:
        return None
    return data[0]["lat"], data[0]["lon"], data[0]["name"]

geo = geocode_city(city, api_key)
if not geo:
    st.error("도시를 찾을 수 없습니다.")
    st.stop()
lat, lon, name = geo

# --- Fetch Weather ---
def fetch_weather(lat, lon, api_key, units="metric"):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": units}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

weather_data = fetch_weather(lat, lon, api_key, units)

# --- Parse Forecast ---
rows = []
for item in weather_data["list"]:
    dt = datetime.fromtimestamp(item["dt"])
    rows.append({
        "dt": dt,
        "temp": item["main"]["temp"],
        "feels_like": item["main"]["feels_like"],
        "humidity": item["main"]["humidity"],
        "weather": item["weather"][0]["main"],
        "description": item["weather"][0]["description"],
    })
df = pd.DataFrame(rows)
df_filtered = df[df["dt"] <= (df["dt"].min() + pd.Timedelta(hours=cnt_hours))]

# --- Display Current Weather ---
st.subheader(f"📍 {name} 현재 날씨")
current = weather_data["list"][0]
col1, col2 = st.columns(2)
with col1:
    st.metric("현재 온도", f"{current['main']['temp']}°{'C' if units=='metric' else 'F'}")
    st.write(f"체감온도: {current['main']['feels_like']}°")
    st.write(f"습도: {current['main']['humidity']}%")
with col2:
    icon = current["weather"][0]["icon"]
    st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png", width=100)
    st.write(f"{current['weather'][0]['main']} - {current['weather'][0]['description']}")

# --- Forecast Table ---
st.markdown("### 🌈 예보 데이터")
st.dataframe(df_filtered.set_index("dt"))

# --- Line Chart ---
st.markdown("### 📈 온도 변화 그래프")
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(df_filtered["dt"], df_filtered["temp"], marker="o", color="royalblue")
ax.set_xlabel("시간")
ax.set_ylabel(f"온도 ({'°C' if units=='metric' else '°F'})")
plt.xticks(rotation=30)
st.pyplot(fig)

# --- Map ---
st.markdown("### 🗺️ 지도")
map_df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
st.map(map_df)

# --- Download CSV ---
st.download_button(
    "📥 예보 CSV 다운로드",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"{name}_forecast.csv",
    mime="text/csv",
)

st.caption("by ChatGPT — Simple Streamlit Artwork Weather App 🌤️")
