# ESP32 Git, Pre-commit, Testing & CI/CD Workshop (Starter)

โปรเจกต์เริ่มต้นและ Workspace หลักสำหรับผู้เรียนบนบอร์ด **DOIT ESP32 DevKit v1** (`esp32doit-devkit-v1`)

## โครงสร้างโปรเจกต์
- `lib/blink_math/` — Pure C++ logic (แยกจาก `Arduino.h` เพื่อให้รัน Unit Test บนเครื่องและ CI ได้)
- `src/main.cpp` — โค้ดหลักสำหรับบอร์ด ESP32 (Blink LED + Serial)
- `test/` — โฟลเดอร์สำหรับเขียน Unity Unit Tests (ใน Module 4)
- `scripts/` — สคริปต์สำหรับผู้เรียน (`check_env.py` และ `verify.py`)
- `platformio.ini` — ไฟล์ตั้งค่า PlatformIO

## คำสั่งที่ใช้บ่อย (รันจากโฟลเดอร์ `workshop/`)
```powershell
uv sync
uv run scripts/check_env.py
uv run pio run -e esp32doit-devkit-v1
uv run pio test -e native -v
uv run scripts/verify.py --all
```

> ดูใบงานปฏิบัติการได้ที่ `../exercises/labs/` (สรุปสารบัญ `../docs/README.md`) และแบบฝึกหัดได้ที่ `../exercises/exercises.md`
