# Docs Build Scripts (`docs/scripts/`)

สคริปต์ชุดนี้ใช้สำหรับ **สร้างและอัปเดตเอกสารประกอบการสอน** (`LAB00`–`LAB06` ทั้งไฟล์ `.html`, `.pdf`, `.docx` และภาพ Callout) โดยแยกจาก `workshop/.venv` ที่ใช้สำหรับเครื่องมือของนักศึกษา (`pre-commit`, `platformio`, `esptool`)

> **หมายเหตุ:** ให้รันคำสั่งทั้งหมดในหน้านี้จาก **โฟลเดอร์ Root ของ Repo** (`git_practice/`)

---

## รายการสคริปต์

| ไฟล์ | หน้าที่ | Input / Output | แพ็กเกจที่ใช้ |
| :--- | :--- | :--- | :--- |
| `annotate_screenshots.py` | วาดกรอบหมายเลขสีแดง (`[1]`, `[2]`, ...) ลงบนภาพหน้าจอ | อ่านภาพจาก `docs/images/` → สร้าง `docs/images/anno-*.png` | `pillow` (`PIL`) |
| `generate_labs.py` | แหล่งข้อมูลกลางของ Lab (`LABS`) และสร้างไฟล์ HTML + PDF | อ่านภาพจาก `docs/images/` → สร้าง `docs/labs_html/*.html` และ `exercises/labs/*.pdf` | Python stdlib + Microsoft Edge (`msedge.exe` สำหรับพิมพ์ PDF) |
| `generate_docx.py` | แปลงข้อมูล `LABS` จาก `generate_labs.py` เป็นไฟล์ Word (`.docx`) | ดึง `LABS` จาก `generate_labs.py` + ภาพจาก `docs/images/` → สร้าง `exercises/labs/*.docx` | `python-docx` |

---

## วิธีรัน (เรียงตามลำดับเมื่อแก้ภาพหรือเนื้อหา)

### 1. สร้างภาพ Callout ใหม่ (เมื่อแก้ภาพหรือพิกัดกรอบใน `annotate_screenshots.py`)
```powershell
uv run --with pillow python docs/scripts/annotate_screenshots.py
```

### 2. สร้างไฟล์ Lab HTML และ PDF (`LAB00`–`LAB06`)
```powershell
python docs/scripts/generate_labs.py
```
- สร้าง `.html` ที่ `docs/labs_html/` และพิมพ์เป็น `.pdf` ที่ `exercises/labs/` ผ่าน Microsoft Edge (`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`)

### 3. สร้างไฟล์ Lab Word (`.docx`)
```powershell
uv run --with python-docx python docs/scripts/generate_docx.py
```
- **สำคัญ:** ปิดไฟล์ `exercises/labs/*.docx` ที่เปิดอยู่ใน Microsoft Word ก่อนรันทุกครั้ง เพื่อป้องกัน error `PermissionError: [Errno 13] Permission denied`
- ใช้ `uv run --with python-docx` เพราะ `workshop/.venv` ไม่ได้ติดตั้ง `python-docx` ไว้ (กันปะปนกับสภาพแวดล้อมของนักศึกษา)

### 4. ตรวจคุณภาพเอกสาร (Audit) หลังแก้ไข
```powershell
python .agents/skills/technical-workshop-authoring/scripts/run.py --workspace . --json
```
- ตรวจว่ามีภาพที่หายไป หรือ Code block ยาวเกินเกณฑ์ (`max_code_lines_threshold: 25`) หรือไม่ (`"status": "SUCCESS"`)
