#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py - เซิร์ฟเวอร์ Localhost พร้อม API Bridge สำหรับส่ง LINE และดึงข้อมูล RID
แก้ปัญหา Browser ติด CORS Policy 100% ทำให้กดปุ่มส่ง LINE จากหน้าเว็บได้ทันที
"""

import os
import sys
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.parse
from datetime import datetime

# นำเข้าฟังก์ชันตรวจวัดน้ำ
sys.path.append(os.path.join(os.path.dirname(__file__), "python"))
try:
    from water_monitor import fetch_rid_hourly_data, build_flex_payload, send_line_flex, load_env_file
    load_env_file()
except Exception:
    pass

PORT = 8000

class DashboardHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # เปิด CORS สำหรับการทดสอบ
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        # 1. API สำหรับส่งข้อความเข้า LINE (ข้าม CORS ได้ 100%)
        if self.path == '/api/send-line':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req_json = json.loads(post_data.decode('utf-8'))
                token = req_json.get('token', '').strip() or os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
                target = req_json.get('target', 'broadcast').strip() or os.getenv('LINE_USER_ID', 'broadcast')
                payload = req_json.get('payload')

                if not token:
                    self.send_json_response(400, {"success": False, "message": "กรุณาระบุ LINE Channel Access Token"})
                    return

                is_broadcast = target.lower() == 'broadcast'
                endpoint = "https://api.line.me/v2/bot/message/broadcast" if is_broadcast else "https://api.line.me/v2/bot/message/push"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
                body = {"messages": [payload]} if payload else {}
                if not is_broadcast and payload:
                    body["to"] = target

                req = urllib.request.Request(endpoint, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
                try:
                    with urllib.request.urlopen(req, timeout=15) as res:
                        resp_body = res.read().decode('utf-8')
                        self.send_json_response(200, {"success": True, "message": "ส่งข้อความเข้า LINE สำเร็จเรียบร้อยแล้ว!"})
                except urllib.error.HTTPError as e:
                    err_msg = e.read().decode('utf-8')
                    self.send_json_response(e.code, {"success": False, "message": f"LINE API ตอบกลับผิดพลาด ({e.code}): {err_msg}"})
                except Exception as e:
                    self.send_json_response(500, {"success": False, "message": f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}"})

            except Exception as e:
                self.send_json_response(400, {"success": False, "message": f"ข้อมูล JSON ไม่ถูกต้อง: {e}"})
            return

        super().do_POST()

    def send_json_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, DashboardHandler)
    print("=" * 65)
    print(f"🚀 เซิร์ฟเวอร์พร้อมใช้งานแล้วที่: http://localhost:{PORT}")
    print("💡 ปลดล็อกปัญหา CORS เรียบร้อย - สามารถกดยิง LINE จากหน้าเว็บได้ทันที!")
    print("=" * 65)
    
    # เปิดเบราว์เซอร์อัตโนมัติ
    import webbrowser
    webbrowser.open(f"http://localhost:{PORT}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nหยุดการทำงานของเซิร์ฟเวอร์")

if __name__ == '__main__':
    main()
