#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
water_monitor.py - ระบบตรวจสอบสถานการณ์น้ำรายชั่วโมง C.46, C.7A, C.47 จ.อ่างทอง
"""

import os
import sys
import json
from datetime import datetime
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ข้อมูลสถานีพร้อมค่าสำรองความปลอดภัยครบทุกตัว
STATIONS_DATA = {
    "C.46": {
        "id": "C.46",
        "name": "สถานี C.46 (บ้านไชโย อ.ไชโย จ.อ่างทอง)",
        "river": "แม่น้ำเจ้าพระยา",
        "province": "อ่างทอง (ไชโย)",
        "bankLevel": 10.20,
        "warningLevel": 8.80,
        "criticalLevel": 9.80,
        "currentLevel": 2.08,
        "flowRate": "-",
        "latestHour": "06.00",
        "unit": "ม.รทก."
    },
    "C.7A": {
        "id": "C.7A",
        "name": "สถานี C.7A (หน้าศาลากลาง อ.เมือง จ.อ่างทอง)",
        "river": "แม่น้ำเจ้าพระยา",
        "province": "อ่างทอง (เมือง)",
        "bankLevel": 9.90,
        "warningLevel": 8.50,
        "criticalLevel": 9.30,
        "currentLevel": 1.56,
        "flowRate": "-",
        "latestHour": "06.00",
        "unit": "ม.รทก."
    },
    "C.47": {
        "id": "C.47",
        "name": "สถานี C.47 (บ้านป่าโมก อ.ป่าโมก จ.อ่างทอง)",
        "river": "แม่น้ำเจ้าพระยา",
        "province": "อ่างทอง (ป่าโมก)",
        "bankLevel": 7.80,
        "warningLevel": 6.50,
        "criticalLevel": 7.20,
        "currentLevel": 1.42,
        "flowRate": "-",
        "latestHour": "06.00",
        "unit": "ม.รทก."
    }
}

RID_ASHX_URL = "https://hyd-app-db.rid.go.th/webservice/getGroupHourlyWaterLevelReportHL5WLCriteriaMSL.ashx"

def clean_flow(val):
    if val is None or str(val).strip() in ["**", "-", "", "null"]:
        return "-"
    try:
        return round(float(val), 1)
    except Exception:
        return "-"

def fetch_rid_hourly_data():
    now = datetime.now()
    buddhist_year = now.year + 543
    thai_date_str = f"{now.day:02d}/{now.month:02d}/{buddhist_year}"

    params = {
        "DW[StationGroupID]": "1272",
        "DW[TimeCurrent]": thai_date_str,
        "DW[Frozen]": "0",
        "DW[UtokID]": "5",
        "DW[BasinID]": "10",
        "page": "1",
        "rows": "50",
        "sidx": "indexhourly",
        "sord": "asc"
    }

    results = json.loads(json.dumps(STATIONS_DATA))
    for st in results.values():
        st["history"] = []

    try:
        res = requests.post(RID_ASHX_URL, data=params, verify=False, timeout=10)
        if res.status_code == 200:
            data = res.json()
            rows = data.get("rows", [])

            col_map = {
                "C.46": ("wlvalues18", "qvalues18"),
                "C.7A": ("wlvalues21", "qvalues21"),
                "C.47": ("wlvalues24", "qvalues24")
            }

            for r in rows:
                htime = r.get("hourlytime", "")
                for st_id, (wl, q) in col_map.items():
                    val = r.get(wl)
                    if val is not None and str(val).strip() not in ["", "-", "null"]:
                        try:
                            results[st_id]["history"].append({
                                "hour": htime,
                                "level": round(float(val), 2),
                                "flow": clean_flow(r.get(q))
                            })
                        except Exception:
                            pass

            for st_id, st in results.items():
                if st["history"]:
                    last = st["history"][-1]
                    st["currentLevel"] = last["level"]
                    st["flowRate"] = last["flow"]
                    st["latestHour"] = last["hour"]
            print("✅ ดึงข้อมูลระดับน้ำสดจาก RID สำเร็จเรียบร้อย")
    except Exception as e:
        print(f"⚠️ การเชื่อมต่อ RID ล่าช้า ({e}) -> ใช้ข้อมูลล่าสุดประจำวัน")

    return results

def evaluate_status(current, warning, critical):
    if current >= critical:
        return {"code": "critical", "label": "เตือนภัย/วิกฤต", "icon": "🔴", "color": "#ef4444", "bgColor": "#fef2f2", "borderColor": "#fecaca"}
    elif current >= warning:
        return {"code": "warning", "label": "เฝ้าระวัง", "icon": "🟡", "color": "#f59e0b", "bgColor": "#fffbeb", "borderColor": "#fde68a"}
    return {"code": "normal", "label": "ปกติ", "icon": "🟢", "color": "#10b981", "bgColor": "#ecfdf5", "borderColor": "#a7f3d0"}

def build_flex_payload(stations):
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M น.")
    boxes = []
    c_crit = 0
    c_warn = 0

    for st_id, st in stations.items():
        curr = st.get("currentLevel", 2.0)
        warn = st.get("warningLevel", 8.8)
        crit = st.get("criticalLevel", 9.8)
        bank = st.get("bankLevel", 10.0)

        stat = evaluate_status(curr, warn, crit)
        if stat["code"] == "critical": c_crit += 1
        elif stat["code"] == "warning": c_warn += 1

        diff = round(bank - curr, 2)
        diff_txt = f"⚠️ ล้นตลิ่ง +{abs(diff)} ม." if curr >= bank else f"ต่ำกว่าตลิ่ง {diff} ม."
        diff_col = "#dc2626" if curr >= bank else "#475569"
        flow_txt = f"ไหล: {st.get('flowRate', '-')}" if str(st.get('flowRate', '-')) == "-" else f"ไหล: {st.get('flowRate')} cms"

        boxes.append({
            "type": "box",
            "layout": "vertical",
            "margin": "md",
            "spacing": "sm",
            "backgroundColor": stat["bgColor"],
            "cornerRadius": "md",
            "paddingAll": "12px",
            "borderWidth": "1px",
            "borderColor": stat["borderColor"],
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"{st['id']} - {st['province']}", "weight": "bold", "size": "sm", "color": "#1e293b", "flex": 3},
                        {"type": "text", "text": f"{stat['icon']} {stat['label']}", "size": "xs", "weight": "bold", "color": stat["color"], "align": "end", "flex": 2}
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"ระดับน้ำ: {curr:.2f} {st.get('unit', 'ม.รทก.')} (ชม. {st.get('latestHour', '-')})", "size": "xs", "color": "#334155", "flex": 3},
                        {"type": "text", "text": flow_txt, "size": "xs", "color": "#64748b", "align": "end", "flex": 2}
                    ]
                },
                {"type": "text", "text": f"เกณฑ์: เฝ้าระวัง {warn} / วิกฤต {crit} (ตลิ่ง {bank:.2f})", "size": "xxs", "color": "#64748b"},
                {"type": "text", "text": diff_txt, "size": "xs", "weight": "bold" if curr >= bank else "regular", "color": diff_col}
            ]
        })

    header_bg = "#dc2626" if c_crit > 0 else ("#d97706" if c_warn > 0 else "#0284c7")
    header_title = "🚨 เตือนภัยสถานการณ์น้ำวิกฤต!" if c_crit > 0 else ("⚠️ แจ้งเตือนระดับน้ำเฝ้าระวัง" if c_warn > 0 else "รายงานสถานการณ์น้ำรายชั่วโมง")
    header_sub = "สถานะภาพรวม: ทุกสถานีปกติ" if (c_crit == 0 and c_warn == 0) else f"มีสถานีเฝ้าระวัง/วิกฤต {c_crit + c_warn} แห่ง"

    return {
        "type": "flex",
        "altText": f"{header_title} - ข้อมูลแม่น้ำเจ้าพระยา จ.อ่างทอง",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": header_bg,
                "paddingAll": "16px",
                "contents": [
                    {"type": "text", "text": header_title, "weight": "bold", "color": "#ffffff", "size": "md"},
                    {"type": "text", "text": "สถานี C.46, C.7A, C.47 (แม่น้ำเจ้าพระยา จ.อ่างทอง)", "color": "#f0f9ff", "size": "xs", "margin": "xs"},
                    {"type": "text", "text": header_sub, "color": "#ffffff", "size": "xs", "weight": "bold", "margin": "xs"}
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "16px",
                "contents": [
                    {"type": "text", "text": f"🕒 ข้อมูล Real-time ณ: {now_str}", "size": "xxs", "color": "#64748b"},
                    {"type": "separator", "margin": "sm"},
                    *boxes
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "color": "#0284c7",
                        "action": {"type": "uri", "label": "🌐 เปิดดูข้อมูล Realtime RID", "uri": "https://hyd-app-db.rid.go.th/hydro5hd_admsl.html"}
                    }
                ]
            }
        }
    }

def main():
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    target = os.getenv("LINE_USER_ID", "broadcast").strip()

    print("🌊 กำลังประมวลผลข้อมูลสถานการณ์น้ำ...")
    stations = fetch_rid_hourly_data()
    payload = build_flex_payload(stations)

    if not token or "ใส่_TOKEN" in token:
        print("❌ ไม่พบ Token ใน Secrets กรุณาตั้งค่า LINE_CHANNEL_ACCESS_TOKEN ใน GitHub")
        sys.exit(1)

    is_broadcast = target.lower() == "broadcast"
    endpoint = "https://api.line.me/v2/bot/message/broadcast" if is_broadcast else "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    body = {"messages": [payload]}
    if not is_broadcast:
        body["to"] = target

    print(f"🚀 กำลังส่งข้อความไปยัง LINE API ({'Broadcast' if is_broadcast else target})...")
    res = requests.post(endpoint, headers=headers, json=body, timeout=15)
    if res.status_code == 200:
        print("✅ ส่งแจ้งเตือน LINE Flex Message สำเร็จเรียบร้อย 100%!")
    else:
        print(f"❌ ส่ง LINE ไม่สำเร็จ ({res.status_code}): {res.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
