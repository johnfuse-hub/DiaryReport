"""
streamlit_app.py - แดชบอร์ดติดตามสถานการณ์น้ำและแจ้งเตือน LINE ด้วย Streamlit
เหมาะสำหรับใช้งานบน Streamlit Community Cloud + GitHub หรือรัน Localhost ด้วย `streamlit run streamlit_app.py`
"""

import os
import sys
import json
from datetime import datetime
import streamlit as st
import pandas as pd
import requests

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบติดตามสถานการณ์น้ำ จ.อ่างทอง (RID)",
    page_icon="🌊",
    layout="wide"
)

# นำเข้าฟังก์ชันจาก water_monitor
sys.path.append(os.path.join(os.path.dirname(__file__), "python"))
try:
    from water_monitor import fetch_rid_hourly_data, evaluate_status, build_flex_payload, send_line_flex, STATIONS_METADATA, load_env_file
    load_env_file()
except ImportError:
    st.error("ไม่พบคลาสหรือฟังก์ชันใน python/water_monitor.py")

st.title("🌊 ระบบติดตามสถานการณ์น้ำแม่น้ำเจ้าพระยา (จ.อ่างทอง)")
st.markdown("**สถานี:** C.46 (ไชโย), C.7A (เมืองอ่างทอง), C.47 (ป่าโมก) | ข้อมูลสดจาก [กรมชลประทาน (RID)](https://hyd-app-db.rid.go.th/hydro5hd_admsl.html)")

# แถบควบคุมด้านข้าง
with st.sidebar:
    st.header("⚙️ การตั้งค่า & แจ้งเตือน LINE")
    
    default_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    default_target = os.getenv("LINE_USER_ID", "broadcast")
    
    line_token = st.text_input("LINE Channel Access Token", value=default_token, type="password", help="ใส่ Token ที่ได้จาก LINE Developers (ระบบจะจำไว้เป็น Default)")
    line_target = st.text_input("User ID / Group ID", value=default_target, help="พิมพ์ broadcast หรือใส่ User ID ของคุณ")
    
    st.markdown("---")
    st.subheader("⏰ รอบเวลาแจ้งเตือน (วันละ 4 รอบ)")
    t1 = st.checkbox("🌅 09:30 น.", value=True)
    t2 = st.checkbox("☀️ 12:30 น.", value=True)
    t3 = st.checkbox("🌤️ 15:30 น.", value=True)
    t4 = st.checkbox("🌆 18:30 น.", value=True)
    
    st.markdown("---")
    btn_fetch = st.button("⚡ ดึงข้อมูลสดจาก RID ทันที", use_container_width=True)

# โหลดข้อมูล
if "stations_data" not in st.session_state or btn_fetch:
    with st.spinner("กำลังดึงข้อมูลสดจากเซิร์ฟเวอร์กรมชลประทาน..."):
        st.session_state.stations_data = fetch_rid_hourly_data()
        st.session_state.last_fetched = datetime.now().strftime("%d/%m/%Y %H:%M:%S น.")

stations = st.session_state.stations_data
last_time = st.session_state.get("last_fetched", "-")

st.info(f"🕒 ข้อมูลซิงค์ล่าสุดเมื่อ: **{last_time}**")

# การ์ดแสดงผล 3 สถานี
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for i, (st_id, data) in enumerate(stations.items()):
    status = evaluate_status(data["currentLevel"], data["warningLevel"], data["criticalLevel"])
    diff = round(data["bankLevel"] - data["currentLevel"], 2)
    diff_text = f"ล้นตลิ่ง +{abs(diff)} ม." if data["currentLevel"] >= data["bankLevel"] else f"ต่ำกว่าตลิ่ง {diff} ม."
    flow_text = f"{data['flowRate']} cms" if data['flowRate'] != "-" else "-"
    
    with cols[i]:
        st.subheader(f"[{st_id}] {data['province']}")
        st.markdown(f"**สถานะ:** {status['icon']} `{status['label']}`")
        st.metric(
            label=f"ระดับน้ำปัจจุบัน (ชม. {data.get('latestHour', '-')})",
            value=f"{data['currentLevel']:.2f} ม.รทก.",
            delta=f"-{diff} ม. จากตลิ่ง" if diff > 0 else f"+{abs(diff)} ม. ล้นตลิ่ง"
        )
        st.write(f"• **ระดับตลิ่ง:** {data['bankLevel']:.2f} ม.")
        st.write(f"• **เกณฑ์เฝ้าระวัง:** {data['warningLevel']:.2f} ม. | **วิกฤต:** {data['criticalLevel']:.2f} ม.")
        st.write(f"• **ปริมาณน้ำไหลผ่าน:** {flow_text}")

st.markdown("---")

# กราฟสถิติรายชั่วโมง (24 ชั่วโมง)
st.subheader("📈 กราฟระดับน้ำรายชั่วโมง (24 ชม. ล่าสุด)")
chart_data = {}
for st_id, data in stations.items():
    if data.get("history"):
        hours = [f"ชม. {h['hour']}" for h in data["history"]]
        levels = [h["level"] for h in data["history"]]
        chart_data[f"{st_id} ({data['province']})"] = levels

if chart_data:
    df_chart = pd.DataFrame(chart_data)
    st.line_chart(df_chart)

# ส่วนทดสอบส่ง LINE
st.markdown("---")
st.subheader("🚀 ทดสอบส่งข้อความแจ้งเตือนเข้า LINE")

if st.button("ส่ง LINE แจ้งเตือนเดี๋ยวนี้"):
    if not line_token:
        st.warning("⚠️ กรุณากรอก LINE Channel Access Token ในแถบด้านซ้ายก่อนส่ง")
    else:
        web_time = f"ชม.ที่ {stations.get('C.46', {}).get('latestHour', '18.00')} น."
        payload = build_flex_payload(stations, web_time, last_time)
        ok = send_line_flex(payload, line_token, line_target)
        if ok:
            st.success("✅ ส่งข้อความแจ้งเตือน Flex Message เข้า LINE เรียบร้อยแล้ว!")
        else:
            st.error("❌ ส่งไม่สำเร็จ กรุณาตรวจสอบ Token และ User ID")
