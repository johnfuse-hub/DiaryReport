# 🚀 คู่มือการเปิด GitHub Repository ใหม่แบบง่ายและชัวร์ 100%

คู่มือนี้สำหรับทีมงานในการนำโปรเจกต์ **`DiaryReport`** ขึ้น GitHub เพื่อให้ทุกคนเข้าดูแดชบอร์ดออนไลน์และรับการแจ้งเตือนผ่าน LINE ได้ทันที

---

## 📌 ขั้นตอนที่ 1: สร้าง Repository บน GitHub
1. เข้าไปที่ [**github.com/new**](https://github.com/new)
2. ตั้งชื่อ Repository เช่น **`DiaryReport`**
3. เลือกเป็น **Public**
4. กดปุ่มสีเขียว **"Create repository"**

---

## 📌 ขั้นตอนที่ 2: อัปโหลดไฟล์ทั้งหมดขึ้น GitHub

### วิธีที่ง่ายที่สุด (ผ่าน GitHub Web):
1. ที่หน้า Repo กดปุ่ม **"uploading an existing file"**
2. เลือกไฟล์ทั้งหมดในโฟลเดอร์นี้ลากไปวาง แล้วกด **Commit changes**
3. **สำคัญมาก:** ตรวจดูว่ามีไฟล์ **`water_monitor.py`** และโฟลเดอร์ **`.github/workflows/water_alert.yml`** ขึ้นไปด้วย

---

## 📌 ขั้นตอนที่ 3: เปิดหน้าเว็บแดชบอร์ด (GitHub Pages)
1. ในหน้า Repo ไปที่ **Settings** -> **Pages**
2. ตรง **Branch** เลือก `main` แล้วกด **Save**
3. รอ 1 นาที จะได้ลิงก์เว็บ เช่น `https://YOUR_USERNAME.github.io/DiaryReport/`

---

## 📌 ขั้นตอนที่ 4: ตั้งค่ารหัสลับ LINE เพื่อให้บอทแจ้งเตือนอัตโนมัติ
1. ไปที่ **Settings** -> **Secrets and variables** -> **Actions**
2. กด **New repository secret** เพื่อใส่ 2 ค่านี้:
   * **Name:** `LINE_CHANNEL_ACCESS_TOKEN` | **Value:** *(วาง Channel Access Token ของคุณ)*
   * **Name:** `LINE_USER_ID` | **Value:** *(วาง User ID เช่น Ua666a6ab... หรือพิมพ์ `broadcast`)*

---

## 📌 ขั้นตอนที่ 5: ทดสอบสั่งรันแจ้งเตือน LINE
1. ไปที่แท็บ **Actions**
2. คลิก **`Scheduled Water Situation LINE Alert & Sync`** ด้านซ้าย
3. กดปุ่ม **"Run workflow"** ด้านขวา
4. ข้อความการ์ดระดับน้ำจะเด้งเข้าแอป LINE ทันที และระบบจะรันส่งให้อัตโนมัติวันละ 4 รอบ (09:30, 12:30, 15:30, 18:30 น.) ครับ! 🎉
