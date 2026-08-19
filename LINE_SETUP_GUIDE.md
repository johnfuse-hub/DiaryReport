# 📖 คู่มือการตั้งค่า LINE Developers & LINE Messaging API

เอกสารนี้จัดทำขึ้นเพื่อให้ทีมงานสามารถสร้าง Bot และนำ **Channel Access Token** มาใช้ทดสอบระบบแจ้งเตือนสถานการณ์น้ำได้แบบเข้าใจง่ายทุกขั้นตอน

---

## 📌 ขั้นตอนที่ 1: เข้าสู่ LINE Developers Console

1. เข้าเว็บไซต์ [https://developers.line.biz/](https://developers.line.biz/)
2. คลิกปุ่ม **Log in** (มุมขวาบน) โดยใช้บัญชี LINE ส่วนตัวของคุณ
3. หากเป็นการเข้าใช้งานครั้งแรก ระบบจะให้กรอกชื่อ Developer Name และยอมรับเงื่อนไข

---

## 📌 ขั้นตอนที่ 2: สร้าง Provider และ Messaging API Channel

1. คลิกปุ่ม **Create a new provider**
   - ใส่ชื่อ Provider Name เช่น `Water-Monitoring-Team`
2. ภายใต้ Provider ที่สร้างขึ้น คลิกเลือก **Create a Messaging API channel**
3. กรอกข้อมูลของ Channel:
   - **Channel name**: เช่น `รายงานสถานการณ์น้ำ C.46-C.7A`
   - **Channel description**: เช่น `บอทแจ้งเตือนระดับน้ำและเตือนภัยลุ่มน้ำน่าน`
   - **Category**: เลือกหมวดหมู่ เช่น *Public Utilities*
   - **Subcategory**: เช่น *Water supply*
   - **Email address**: อีเมลของคุณ
4. ติ๊กยอมรับข้อตกลงแล้วกด **Create**

---

## 📌 ขั้นตอนที่ 3: รับ Channel Access Token (Long-lived)

1. เข้าไปที่ Channel ที่สร้างไว้ -> คลิกแท็บ **Messaging API**
2. เลื่อนลงไปล่างสุดที่หัวข้อ **Channel access token**
3. คลิกปุ่ม **Issue**
4. จะได้ข้อความ Token ขนาดยาว -> **คัดลอก (Copy) เก็บไว้**
   *(นำ Token นี้ไปใส่ในช่อง Channel Access Token ในหน้าแดชบอร์ด หรือในไฟล์ Python)*

---

## 📌 ขั้นตอนที่ 4: การเพิ่มเพื่อนบอทและหา User ID

### วิธีที่ 1: แอดเพื่อนบอท
1. ในแท็บ **Messaging API** ให้สแกน **QR Code** ด้วยมือถือของคุณ เพื่อเพิ่มบอทเป็นเพื่อน
2. ปิด Auto-reply Message (ข้อความตอบกลับอัตโนมัติ):
   - เข้าแท็บ **Messaging API** -> เลื่อนไปที่ **Auto-reply messages** -> คลิก **Edit**
   - ในหน้า LINE Official Account Manager ให้ปิด **Auto-response** เป็น `Disabled` และเปิด **Webhooks** เป็น `Enabled`

### วิธีที่ 2: หา User ID ของคุณ
1. ในหน้า LINE Developers Console คลิกไปที่แท็บ **Basic settings**
2. เลื่อนลงมาล่างสุดที่หัวข้อ **Your user ID** (จะขึ้นต้นด้วยตัว `U...` เช่น `U91a234567890abcdef...`)
3. คัดลอก User ID นี้มาใส่ในหน้าเว็บแดชบอร์ด หรือไฟล์สคริปต์

> 💡 **ทริคสำหรับการส่งข้อความ:**
> - หากต้องการส่งให้ตนเองคนเดียว: ใส่ `Your user ID`
> - หากต้องการส่งให้ทุกคนที่เป็นเพื่อนกับบอท: ใส่คำว่า `broadcast` ในช่อง User ID ได้ทันที!

---

## 📌 ขั้นตอนที่ 5: ทดสอบส่งข้อความ

### ทดสอบผ่านหน้าเว็บแดชบอร์ด
1. เปิดไฟล์ `index.html` บนบราวเซอร์
2. เลื่อนลงไปที่ส่วน **ห้องทดลอง LINE Messaging API**
3. วาง **Channel Access Token** และ **User ID** (หรือพิมพ์ `broadcast`)
4. ปรับระดับน้ำในแดชบอร์ดให้ขึ้นสถานะ 🔴 วิกฤต หรือ 🟡 เฝ้าระวัง
5. คลิกปุ่ม **🚀 ส่งข้อความทดสอบเข้า LINE**

### ทดสอบผ่าน Python
เปิด Terminal หรือ Command Prompt ในโฟลเดอร์โปรเจกต์:
```bash
# 1. ติดตั้งไลบรารี
pip install -r python/requirements.txt

# 2. รันสคริปต์ทดสอบ
python python/water_monitor.py --scenario critical
```

---

## 🛠️ เครื่องมือช่วยออกแบบ LINE Flex Message

หากต้องการปรับแต่งหน้าตาการ์ด Flex Message เพิ่มเติม สามารถนำ JSON Payload จากหน้าเว็บไปลองเล่นในเครื่องมือทางการของ LINE ได้ที่:
🔗 [LINE Flex Message Simulator](https://developers.line.biz/flex-simulator/)
