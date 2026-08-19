# 🚀 คู่มือการรัน Localhost และ Deploy ขึ้น GitHub / GitHub Pages

โปรเจกต์นี้ได้รับการออกแบบให้เป็น **Zero-Dependency Frontend** คือสามารถเปิดใช้งานได้ทันทีบนคอมพิวเตอร์ หรือจะแชร์ให้ทีมงานเข้าดูผ่านลิงก์เว็บไซต์ฟรีบน **GitHub Pages** โดยไม่ต้องเสียค่าโฮสติ้งและไม่ต้องพึ่งพา OneDrive

---

## 💻 วิธีที่ 1: รันบนคอมพิวเตอร์ของคุณ (Localhost)

### แบบที่ 1: ดับเบิ้ลคลิกเปิดใช้งานทันที (ง่ายที่สุด)
1. ไปที่โฟลเดอร์โปรเจกต์ `DiaryReport`
2. ดับเบิ้ลคลิกไฟล์ `index.html`
3. เบราว์เซอร์ของคุณจะเปิดหน้าแดชบอร์ดขึ้นมาพร้อมใช้งานทันที

### แบบที่ 2: รันผ่าน Local Web Server (แนะนำสำหรับทดสอบ API)
เปิด Terminal / PowerShell ในโฟลเดอร์โปรเจกต์ แล้วพิมพ์:

```bash
# รันด้วย Python 3
python -m http.server 8000
```
จากนั้นเปิดบราวเซอร์ไปที่: `http://localhost:8000`

---

## 🌐 วิธีที่ 2: นำขึ้น GitHub และเปิดใช้ GitHub Pages (ให้ทีมงานเปิดผ่านมือถือ/คอมฯ)

การฝากโปรเจกต์ไว้ที่ GitHub จะทำให้ทีมงานทุกคนสามารถเปิดดูแดชบอร์ดผ่านลิงก์ `https://<username>.github.io/<repo-name>/` ได้ตลอดเวลา 24 ชั่วโมง

### ขั้นตอนการ Upload ขึ้น GitHub:

1. เข้าเว็บไซต์ [https://github.com/](https://github.com/) แล้วสร้าง Repository ใหม่ (เช่น ชื่อ `water-situation-dashboard`)
2. เปิด Terminal ในโฟลเดอร์โปรเจกต์นี้ แล้วรันคำสั่ง:

```bash
# 1. เริ่มต้น Git
git init

# 2. เพิ่มไฟล์ทั้งหมด
git add .

# 3. Commit ข้อมูล
git commit -m "feat: Initial water situation dashboard and LINE alert system"

# 4. เปลี่ยนชื่อ Branch หลักเป็น main
git branch -M main

# 5. เชื่อมต่อกับ GitHub Repository ของคุณ (เปลี่ยน URL ให้เป็นของคุณ)
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git

# 6. Push ไฟล์ขึ้น GitHub
git push -u origin main
```

---

## 🌍 วิธีเปิดใช้งาน GitHub Pages (เปิดเว็บฟรี)

1. เข้าไปที่หน้า Repository บน GitHub ของคุณ
2. คลิกเมนู **Settings** (แถบด้านบน)
3. เมนูด้านซ้ายเลือกหัวข้อ **Pages**
4. ในส่วน **Build and deployment**:
   - Source: เลือก **Deploy from a branch**
   - Branch: เลือก `main` / โฟลเดอร์ `/(root)`
   - กดปุ่ม **Save**
5. รอประมาณ 1-2 นาที คุณจะได้ลิงก์เว็บไซต์สาธารณะ เช่น:
   `https://your-username.github.io/water-situation-dashboard/`
   *(สามารถส่งลิงก์นี้ให้ทีมงานเปิดดูผ่านมือถือหรือคอมพิวเตอร์ได้เลย)*

---

## ⏰ วิธีตั้งค่า GitHub Actions สำหรับแจ้งเตือน LINE อัตโนมัติทุกวัน

ในโปรเจกต์มีไฟล์ `.github/workflows/water_alert.yml` อยู่แล้ว ระบบสามารถรันเช็กระดับน้ำและส่ง LINE อัตโนมัติทุกวันตอน 07:00 น. และ 18:00 น. โดยทำตามขั้นตอนนี้:

1. ในหน้า GitHub Repository ไปที่ **Settings** -> **Secrets and variables** -> **Actions**
2. คลิกปุ่ม **New repository secret**
3. สร้าง Secret 2 ตัวดังนี้:
   - Name: `LINE_CHANNEL_ACCESS_TOKEN`
     - Secret: *ใส่ Channel Access Token ที่ได้จาก LINE Developers*
   - Name: `LINE_USER_ID`
     - Secret: *ใส่ User ID ของคุณ หรือใส่คำว่า `broadcast`*
4. ไปที่แท็บ **Actions** บน GitHub -> จะเห็น Workflow ชื่อ **Daily Water Situation LINE Alert**
5. คุณสามารถกดปุ่ม **Run workflow** เพื่อทดสอบยิงได้ทันที หรือปล่อยให้ระบบทำงานตามเวลาแบบอัตโนมัติฟรี!
