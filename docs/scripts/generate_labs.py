#!/usr/bin/env python3
"""
Generate individual Lab Sheet PDFs (LAB00..LAB06, 1 file = 1 topic) into exercises/labs/.
Each lab includes objectives, outcomes, copy-paste ready code/configs matching
workshop/, expected terminal output, questions, exercises, and full-width real screenshots.
"""

import html
import subprocess
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = DOCS_DIR.parent
LABS_DIR = ROOT_DIR / "exercises" / "labs"
HTML_DIR = DOCS_DIR / "labs_html"
LABS_DIR.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(exist_ok=True)
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

LABS = [
    {
        "slug": "LAB00-Environment_Setup",
        "title": "Lab 00: Environment Setup &amp; Toolchain Preparation (เตรียมเครื่องครบทุก Lab)",
        "objectives": [
            "ติดตั้งและตั้งค่าเครื่องมือที่ใช้ตั้งแต่ Lab 01 ถึง Lab 06 ไว้ล่วงหน้าในจุดเดียว (Git, VS Code, <code>uv</code>, MSYS2 <code>gcc/g++</code> และ Local Toolchain ผ่าน <code>uv sync</code>)",
            "Fork โปรเจกต์, Clone ไว้ที่ Desktop, ตั้งค่า Git <code>--local</code> (รวม <code>git lg</code>), เปิด <code>workshop</code> เป็น Workspace หลัก และตรวจความพร้อมด้วย <code>scripts/check_env.py</code>",
        ],
        "outcomes": [
            "สามารถเรียกใช้งานคำสั่ง <code>git</code>, <code>git lg</code>, <code>uv</code>, <code>uv run pre-commit</code>, <code>uv run pio</code>, <code>uv run esptool</code> และ <code>g++</code> จาก Terminal ใน <code>workshop</code> ได้จริง",
            "รัน <code>uv run scripts/check_env.py</code> ผ่านและ Build โปรเจกต์ใน <code>workshop</code> ล่วงหน้าได้สำเร็จ",
        ],
        "tools": [
            "ระบบปฏิบัติการ Windows 10/11 (PowerShell), macOS หรือ Linux พร้อมอินเทอร์เน็ต",
            "โปรแกรม Git, Visual Studio Code (VS Code), MSYS2 (<code>C:\\msys64\\ucrt64\\bin</code>) และบัญชี GitHub ส่วนตัว",
            "<code>PATH</code> = รายชื่อโฟลเดอร์ที่ Terminal ใช้ค้นหาคำสั่ง",
            "<code>uv</code> = ตัวจัดการ Python แบบ Local ต่อโปรเจกต์ (ติดตั้งแพ็กเกจไว้ใน <code>workshop/.venv</code> ไม่ปนกับเครื่องภายนอก)",
            "<code>origin</code> = Repo Fork ของคุณเองบน GitHub (ใช้เป็น Remote หลักตลอดเวิร์กชอป)",
            "สคริปต์ตรวจความพร้อม (รันจากโฟลเดอร์ <code>workshop</code>): <code>uv run scripts/check_env.py</code>",
        ],
        "experiments": [
            ("L-01", "ตรวจสอบ Git, VS Code และติดตั้ง Extension <strong>PlatformIO IDE</strong>"),
            ("L-02", "ติดตั้ง <code>uv</code> และตั้งค่า <code>PATH</code> ของ MSYS2 <code>gcc/g++</code>"),
            ("L-03", "Fork โปรเจกต์, เปิดใช้งาน Actions, Clone ไว้ที่ Desktop, ตั้งค่า <code>--local</code> (รวม <code>git lg</code>) และรัน <code>uv sync</code>"),
            ("L-04", "รัน <code>check_env.py</code> เพื่อตรวจสอบการติดตั้งก่อน แล้วจึง Pre-cache แพ็กเกจ ESP32"),
        ],
        "details": [
            {
                "heading": "L-01: ตรวจสอบ Git, VS Code และติดตั้ง Extension (PlatformIO IDE)",
                "steps": [
                    "Workshop นี้ใช้ PlatformIO 2 ส่วนคู่กัน คือ <strong>PlatformIO IDE Extension</strong> (ปุ่ม UI ใน VS Code) และ <strong>PlatformIO CLI (<code>pio</code>)</strong> (คำสั่ง Terminal และ CI)",
                    "ตรวจสอบว่าในเครื่องมี Git และ Visual Studio Code พร้อมใช้งาน (หากยังไม่มี ดาวน์โหลดได้จาก <code>https://git-scm.com/</code> และ <code>https://code.visualstudio.com/</code>)",
                    "เปิด VS Code แล้วกด <code>Ctrl+Shift+X</code> เพื่อเปิดหน้า Extensions",
                    "ค้นหา <strong>PlatformIO IDE</strong> แล้วกด <strong>Install</strong> (รอแถบ <em>Installing PlatformIO Core...</em> มุมขวาล่างจนเสร็จแล้ว Restart VS Code 1 ครั้ง)",
                ],
                "images": [
                    ("../images/anno-00-vscode-platformio.png", "หน้าติดตั้ง Extension PlatformIO IDE: [1] กดปุ่ม Install แล้วรอตัวโหลดมุมขวาล่างจนเสร็จ"),
                ],
                "code": """# 1. ตรวจสอบเวอร์ชัน Git ใน PowerShell (หากยังไม่มีให้ติดตั้งจาก https://git-scm.com/download/win)
git --version

# 2. ใน VS Code กด Ctrl+Shift+X ค้นหาและกด Install Extension:
#    - PlatformIO IDE (platformio.platformio-ide)""",
            },
            {
                "heading": "L-02: ติดตั้ง uv และติดตั้ง/ตั้งค่า PATH สำหรับ MSYS2 gcc/g++",
                "steps": [
                    "ติดตั้ง <code>uv</code> ด้วย PowerShell จากนั้น <strong>ปิด Terminal เดิมแล้วเปิด PowerShell หน้าต่างใหม่</strong> เพื่อรีเฟรช <code>PATH</code> แล้วตรวจด้วย <code>uv --version</code>",
                    "เปิดเว็บ <code>https://www.msys2.org/</code> กดปุ่ม <code>[1] msys2-x86_64-*.exe</code> เพื่อดาวน์โหลดและติดตั้ง MSYS2 ลงที่ <code>C:\\msys64</code> (หากเครื่องติดตั้งไว้แล้วให้เปิดโปรแกรม <strong>MSYS2 UCRT64</strong> จาก Start Menu)",
                    "ในหน้าต่างเทอร์มินัล <strong>MSYS2 UCRT64</strong> ให้รันคำสั่ง <code>[2] pacman -S mingw-w64-ucrt-x86_64-gcc</code> แล้วกด Enter เพื่อติดตั้ง <code>gcc/g++</code>",
                    "กลับมาที่ PowerShell ใน VS Code แล้วเพิ่มพาท <code>$env:Path = \"C:\\msys64\\ucrt64\\bin;$env:Path\"</code> เพื่อให้เรียกใช้ <code>gcc</code> และ <code>g++</code> ได้ทันทีโดยไม่ติดสิทธิ์แก้ System Environment ของเครื่องห้องแล็บ",
                ],
                "images": [
                    ("../images/anno-00-msys2-download.png", "หน้าเว็บ https://www.msys2.org/ ขั้นตอนที่ 1: [1] กดดาวน์โหลดตัวติดตั้ง msys2-x86_64-*.exe แล้วติดตั้งลงที่ C:\\msys64"),
                    ("../images/anno-00-msys2-gcc.png", "ในหน้าต่างเทอร์มินัล MSYS2 UCRT64 ขั้นตอนที่ 6: [2] รัน pacman -S mingw-w64-ucrt-x86_64-gcc เพื่อติดตั้งคอมไพเลอร์ C/C++"),
                ],
                "code": """# 1. Windows (PowerShell): ติดตั้ง uv แล้วปิด-เปิด PowerShell ใหม่เพื่อเช็กเวอร์ชัน
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version

# 2. [รันในหน้าต่างโปรแกรม MSYS2 UCRT64 หลังติดตั้ง MSYS2 เสร็จ]:
# pacman -S mingw-w64-ucrt-x86_64-gcc

# 3. [รันใน PowerShell ของ VS Code] เพิ่ม PATH ของ MSYS2 แล้วเช็ก g++ / gcc:
$env:Path = "C:\\msys64\\ucrt64\\bin;$env:Path"
g++ --version
gcc --version""",
            },
            {
                "heading": "L-03: Fork โปรเจกต์, เปิดใช้งาน Actions, Clone ไว้ที่ Desktop, ตั้งค่า --local และรัน uv sync",
                "steps": [
                    "เปิดหน้า <code>https://github.com/SavEe2429/git-practice</code> บน GitHub",
                    "กดปุ่ม <code>[1] Fork</code> เพื่อคัดลอก Repo ไปยังบัญชี GitHub ของตัวเอง",
                    "บนหน้า Fork ของตัวเอง ให้กดแท็บ <strong>Actions</strong> แล้วกดปุ่มสีเขียว <strong>I understand my workflows, go ahead and enable them</strong>",
                    "กลับมาที่แท็บ <strong>Code</strong> กด <code>[2] &lt;&gt; Code</code> เพื่อ Copy URL ของ Fork ตัวเอง",
                    "เข้าไปที่โฟลเดอร์ <code>Desktop</code> (<code>cd $HOME\\Desktop</code>) แล้ว <code>git clone</code> ลงที่ Desktop และเข้า <code>cd git-practice</code>",
                    "ตั้งค่า <code>user.name</code>, <code>user.email</code> และคำสั่งย่อ <code>git lg</code> แบบ <code>--local</code> จากนั้นเข้า <code>cd workshop</code> เปิดเป็น Workspace หลัก",
                    "รัน <code>uv sync</code> เพื่อติดตั้ง <code>pre-commit</code>, <code>platformio</code> และ <code>esptool</code> แบบ Local ลงใน <code>workshop/.venv</code>",
                ],
                "images": [
                    ("../images/anno-01-repo-fork.png", "หน้าเว็บ GitHub: [1] กดปุ่ม Fork -> [2] กด <> Code เพื่อ Copy URL ของ Fork ตัวเอง"),
                ],
                "code": """# 1. เข้าโฟลเดอร์ Desktop แล้ว Clone โปรเจกต์จาก Fork ของตัวเอง:
cd $HOME\\Desktop
git clone https://github.com/<your-username>/git-practice.git
cd git-practice

# 2. ตั้งชื่อผู้เขียนและสร้าง git alias (git lg) แบบ --local:
git config --local user.name "Your Name"
git config --local user.email "you@example.com"
git config --local alias.lg "log --oneline --all --graph --decorate"

# 3. เปิดโฟลเดอร์ workshop เป็น Workspace หลัก และติดตั้งแพ็กเกจแบบ Local (workshop/.venv):
code workshop
cd workshop
uv sync""",
            },
            {
                "heading": "L-04: ตรวจสอบการติดตั้งด้วย check_env.py ก่อน แล้ว Pre-cache แพ็กเกจ ESP32",
                "steps": [
                    "<strong>รัน <code>uv run scripts/check_env.py</code> จากในโฟลเดอร์ <code>workshop</code> ก่อนเสมอ</strong> เพื่อตรวจสอบว่าเครื่องมือและ Git identity พร้อมครบทุกตัว",
                    "<em>หมายเหตุสำหรับเครื่องห้องแล็บ:</em> หากเปิด Terminal ใหม่แล้วไม่พบ <code>g++</code> ให้รัน <code>$env:Path = \"C:\\msys64\\ucrt64\\bin;$env:Path\"</code> ก่อน",
                    "รัน <code>uv run pio run -e esp32doit-devkit-v1</code> เพื่อ Pre-cache Toolchain และแพ็กเกจ ESP32 ล่วงหน้า (รอบแรกใช้เวลา ~20–60 วินาที)",
                ],
                "code": """# 1. ตรวจสอบความพร้อมทั้งหมดก่อนเริ่ม Build (รันใน Terminal ของ workspace workshop):
$env:Path = "C:\\msys64\\ucrt64\\bin;$env:Path"
uv run scripts/check_env.py

# 2. Pre-cache แพ็กเกจ ESP32 (ใช้ pio แบบ Local ใน workshop/.venv):
uv run pio run -e esp32doit-devkit-v1""",
            },
        ],
        "expected_output": """$ uv run scripts/check_env.py
=== Pre-Workshop Environment Check ===

[OK] Git: git version 2.56.0.windows.4
[OK] Git identity: Your Name <you@example.com>
[OK] uv: uv 0.11.31
[OK] pre-commit (local): pre-commit 4.7.0 (C:\\Users\\LabRoom\\Desktop\\git-practice\\workshop\\.venv\\Scripts\\pre-commit.EXE)
[OK] PlatformIO CLI (local): PlatformIO Core, version 6.2.0 (C:\\Users\\LabRoom\\Desktop\\git-practice\\workshop\\.venv\\Scripts\\pio.EXE)
[OK] esptool (local): esptool v5.x (C:\\Users\\LabRoom\\Desktop\\git-practice\\workshop\\.venv\\Scripts\\esptool.EXE)
[OK] C/C++ Compiler (สำหรับ pio test -e native): g++.exe (Rev4, Built by MSYS2 project) 16.2.0
======================================================
พร้อมเริ่มเรียน Workshop! (ผ่านครบทุกการตรวจสอบ)""",
        "results": [
            "L-03: ผลลัพธ์ของ <code>git --version</code>, <code>uv --version</code>, <code>uv run pre-commit --version</code>, <code>uv run pio --version</code> และ <code>g++ --version</code>",
            "L-04: ผลลัพธ์จริงจาก <code>uv run scripts/check_env.py</code> และ <code>uv run pio run -e esp32doit-devkit-v1</code>",
        ],
        "questions": [
            "Q1: เหตุใดเราจึงควรรัน <code>check_env.py</code> เพื่อตรวจสอบเครื่องมือก่อนเริ่ม Build และเข้า Lab 01?",
            "Q2: หากใช้เครื่องคอมพิวเตอร์ส่วนกลางของมหาวิทยาลัย เหตุใดจึงควรใช้ <code>git config --local</code> และ Sign Out ออกจากบัญชี GitHub/VS Code เมื่อเลิกใช้งาน?",
        ],
        "exercise": {
            "code": "L-05",
            "steps": [
                "เข้าไปที่โฟลเดอร์ Workspace หลัก (<code>$HOME\\Desktop\\git-practice\\workshop</code>)",
                "รัน <code>uv run scripts/check_env.py</code> เพื่อยืนยันว่าไม่มีรายการ <code>[MISSING]</code>",
                "รัน <code>uv run pio run -e esp32doit-devkit-v1</code> ยืนยันว่า Build ผ่าน <code>[SUCCESS]</code> พร้อมเข้าเรียน Lab 01",
            ],
            "snippet": """cd $HOME\\Desktop\\git-practice\\workshop
$env:Path = "C:\\msys64\\ucrt64\\bin;$env:Path"
uv run scripts/check_env.py
uv run pio run -e esp32doit-devkit-v1""",
        },
        "screenshots": [
            ("../images/term-00-check-env.png", "ตัวอย่างผลรันจริงจาก uv run scripts/check_env.py (รายการที่ยังไม่อยู่ใน PATH จะขึ้น [WARN] พร้อมคำสั่งแก้ไข)"),
        ],
    },
    {
        "slug": "LAB01-Linear_Git_Rebase",
        "title": "Lab 01: Linear Git (Rebase), Fork Workflow &amp; Conventional Commits",
        "objectives": [
            "เข้าใจการทำงานบน Fork (<code>origin</code>) ร่วมกับ Feature Branch และการใช้คำสั่งย่อ <code>git lg</code> เพื่อดูกราฟ Commit",
            "เรียนรู้การรักษาประวัติ Commit ให้เป็นเส้นตรงด้วย <code>git rebase main</code>, การจำลองและแก้ Conflict จริง และการ Push ด้วย <code>--force-with-lease</code>",
        ],
        "outcomes": [
            "แตก Branch <code>feature/*</code> จาก <code>main</code>, เขียน Commit แบบ Conventional Commits, แก้ Rebase Conflict และ Push ด้วย <code>--force-with-lease</code> ได้",
            "ตรวจสอบประวัติด้วย <code>git lg</code> แล้วเห็นโครงสร้างเส้นตรง (Linear History)",
        ],
        "tools": [
            "เครื่องมือทั้งหมดติดตั้งและผ่านการตรวจจาก <strong>Lab 00</strong> เรียบร้อยแล้ว",
            "คำสั่งย่อดูกราฟ Git: <code>git lg</code> (ย่อมาจาก <code>git log --oneline --all --graph --decorate</code>)",
            "วิดีโอประกอบ: <code>videos/01-gitflow-branching.mp4</code>",
        ],
        "experiments": [
            ("L-01", "ตั้งค่า <code>git lg</code>, แตก <code>feature/fast-blink</code>, แก้ <code>src/main.cpp</code> (<code>200</code>), Commit และ Push ขึ้น <code>origin</code>"),
            ("L-02", "สลับกลับไปเพิ่ม Commit ใหม่บน <code>main</code> (<code>300</code>) เพื่อให้กราฟแยกเป็น 2 เส้น แล้วสั่ง <code>git rebase main</code> จนเกิด Conflict"),
            ("L-03", "อ่านและแก้ Rebase Conflict ใน <code>src/main.cpp</code>, รัน <code>git rebase --continue</code> และ Push ด้วย <code>--force-with-lease</code>"),
        ],
        "details": [
            {
                "heading": "L-01: ตั้งค่า git lg, แตก Feature Branch, แก้ src/main.cpp และ Push",
                "steps": [
                    "ตั้งค่า Git Alias <code>git lg</code> (<code>log --oneline --all --graph --decorate</code>) เพื่อใช้ดูกราฟทุก Branch แบบสั้น",
                    "แตก Branch ใหม่ชื่อ <code>feature/fast-blink</code> จาก <code>main</code> ด้วย <code>git switch -c</code>",
                    "เปิดไฟล์ <code>src/main.cpp</code> (ใน <code>workshop</code>) แล้วแก้บรรทัดที่ 15 จาก <code>clamp_interval(500)</code> เป็น <code>200</code>",
                    "รัน <code>git add .</code>, Commit แบบ Conventional Commits และ Push Branch <code>feature/fast-blink</code> ขึ้น <code>origin</code>",
                ],
                "code": """# 1. ตั้งค่า git lg (หากยังไม่ได้ตั้งใน Lab 00) และแตก branch ใหม่จาก main:
git config --local alias.lg "log --oneline --all --graph --decorate"
git switch -c feature/fast-blink main

# 2. เปิด src/main.cpp แก้บรรทัดที่ 15 เป็น: blink_interval_ms = blink_math::clamp_interval(200);
# จากนั้น Stage, Commit และ Push ขึ้น origin:
git add .
git commit -m "feat(blink): support fast blink interval"
git push -u origin feature/fast-blink
git lg -n 5""",
            },
            {
                "heading": "L-02: จำลอง Commit ใหม่บน main ให้กราฟแยก 2 เส้น แล้วสั่ง git rebase main",
                "steps": [
                    "<em>ทำไมต้องจำลอง Commit บน <code>main</code>?</em> หาก <code>main</code> ไม่มี Commit ใหม่เลย การสั่ง Rebase จะขึ้น <code>Current branch is up to date</code> เพราะกราฟเป็นเส้นตรงอยู่แล้ว",
                    "สลับกลับไปที่ <code>main</code> (<code>git switch main</code>) แล้วเปิด <code>src/main.cpp</code> แก้บรรทัดที่ 15 เดียวกันเป็น <code>clamp_interval(300)</code>",
                    "รัน <code>git add .</code>, Commit และ Push ขึ้น <code>origin main</code> จากนั้นรัน <code>git lg -n 5</code> จะเห็นกราฟแตกออกเป็น 2 เส้นแยกกัน",
                    "สลับกลับมาที่ <code>feature/fast-blink</code> แล้วสั่ง <code>git rebase main</code> เพื่อยก Commit ของเราไปต่อท้าย <code>main</code> ล่าสุด (ขั้นตอนนี้จะเกิด Conflict ทันที)",
                ],
                "code": """# 1. สลับไปที่ main แล้วแก้ src/main.cpp บรรทัดที่ 15 เป็น clamp_interval(300):
git switch main
# (แก้ src/main.cpp บรรทัดที่ 15 เป็น: blink_interval_ms = blink_math::clamp_interval(300); แล้วกด Save)
git add .
git commit -m "chore(blink): update default interval on main to 300ms"
git push origin main

# 2. ดูกราฟที่แยกเป็น 2 เส้น แล้วสลับกลับมา Rebase บน feature/fast-blink:
git lg -n 5
git switch feature/fast-blink
git rebase main""",
            },
            {
                "heading": "L-03: วิธีอ่านและแก้ Rebase Conflict ใน src/main.cpp และ Push ด้วย --force-with-lease",
                "code_font_size": 13,
                "steps": [
                    "<strong>วิธีอ่าน Conflict ใน <code>src/main.cpp</code>:</strong> ช่วงระหว่าง <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD</code> ถึง <code>=======</code> คือ<strong>โค้ดเดิมบน <code>main</code> (<code>300</code>)</strong> ส่วนช่วงระหว่าง <code>=======</code> ถึง <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code> คือ<strong>โค้ดใหม่จาก Commit ของเรา (<code>200</code>)</strong>",
                    "แก้ไฟล์โดย<strong>ลบเส้นแบ่งทั้ง 3 เส้น</strong> (<code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code>, <code>=======</code>, <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code>) และโค้ดเดิมออก เหลือเฉพาะโค้ดใหม่ที่ต้องการแล้วกด Save",
                    "รัน <code>git add .</code> แล้วตามด้วย <code>git rebase --continue</code> (เมื่อแท็บข้อความ Commit เด้งขึ้นมาใน VS Code ให้กด Save แล้วปิดแท็บ)",
                    "รัน <code>git lg -n 5</code> เพื่อตรวจว่ากราฟเรียงเป็นเส้นตรงเส้นเดียวแล้ว จากนั้นอัปเดต Branch บน GitHub ด้วย <code>git push --force-with-lease -u origin feature/fast-blink</code>",
                ],
                "code": """# 1. ตัวอย่างหน้าตา Conflict จริงใน src/main.cpp:
<<<<<<< HEAD                                          // <-- เริ่มส่วนโค้ดเดิมบน main
  blink_interval_ms = blink_math::clamp_interval(300);  // โค้ดเดิม (จาก main ล่าสุด)
=======                                               // <-- เส้นคั่นระหว่างโค้ดเดิมกับโค้ดใหม่
  blink_interval_ms = blink_math::clamp_interval(200);  // โค้ดใหม่ (จาก Commit ของเรา)
>>>>>>> feat(blink): support fast blink interval      // <-- จบส่วนโค้ดใหม่

# 2. แก้ใน src/main.cpp ให้เหลือเฉพาะโค้ดใหม่บรรทัดเดียว (ลบเส้น <<<, ===, >>> ออกให้หมด):
  blink_interval_ms = blink_math::clamp_interval(200);

# 3. บันทึกไฟล์แล้ว Stage + ทำ Rebase ต่อ (หากทำพลาดยกเลิกได้ด้วย: git rebase --abort):
git add .
git rebase --continue

# 4. ตรวจกราฟเส้นตรงด้วย git lg แล้ว Push หลัง Rebase ด้วย --force-with-lease:
git lg -n 5
git push --force-with-lease -u origin feature/fast-blink""",
            },
        ],
        "expected_output": """$ git lg -n 4
* 9a4c21e (HEAD -> feature/fast-blink, origin/feature/fast-blink) feat(blink): support fast blink interval
* 4d12b8c (origin/main, main) chore(blink): update default interval on main to 300ms
* 00f0566 docs(scripts): add README for docs/scripts build helpers""",
        "results": [
            "L-03: ผลลัพธ์จาก <code>git lg -n 5</code> หลังแก้ Conflict และทำ Rebase สำเร็จ (กราฟเรียงเป็นเส้นตรงเส้นเดียวหรือไม่)",
        ],
        "questions": [
            "Q1: การทำงานบน Fork ของตัวเอง (<code>origin</code>) ร่วมกับ Feature Branch มีข้อดีทางวิศวกรรมอย่างไรเมื่อเทียบกับการ Push เข้า <code>main</code> โดยตรง?",
            "Q2: การใช้ <code>git rebase</code> แตกต่างจาก <code>git merge</code> อย่างไรในหน้าตาของ <code>git log --graph</code>?",
            "Q3: เหตุใดหลัง <code>git rebase</code> แล้วจึงต้องใช้ <code>git push --force-with-lease</code> แทน <code>git pull</code> หรือ <code>git push --force</code>?",
        ],
        "exercise": {
            "code": "L-04",
            "steps": [
                "ตรวจสอบด้วย <code>git lg -n 5</code> ว่าอยู่บน Branch <code>feature/fast-blink</code> ที่มี Commit ต่อปลาย <code>main</code> แบบเส้นตรง",
                "รัน <code>uv run scripts/verify.py --module 1</code> จากในโฟลเดอร์ <code>workshop</code> เพื่อตรวจผล Lab 01",
            ],
            "snippet": """# ตรวจผล Module 1 (รันจากในโฟลเดอร์ workshop):
git lg -n 5
uv run scripts/verify.py --module 1""",
        },
        "screenshots": [
            ("../images/term-01-git-log.png", "ตัวอย่างผลลัพธ์จาก git lg: ประวัติ Commit เรียงเป็นเส้นตรง"),
        ],
    },
    {
        "slug": "LAB02-Issue_Forms_PR_Protection",
        "title": "Lab 02: YAML Issue Forms, Pull Request (Rebase) &amp; Branch Protection",
        "objectives": [
            "เรียนรู้การสร้างแบบฟอร์มแจ้งปัญหาและขอฟีเจอร์ด้วยไฟล์ YAML (<code>.github/ISSUE_TEMPLATE/*.yml</code>) และการใช้ PR Template",
            "เรียนรู้การเปิด Pull Request ผ่านหน้าเว็บ GitHub, ทำ Rebase and Merge และตั้ง Branch Protection บน <code>main</code>",
        ],
        "outcomes": [
            "แทนที่ Skeleton ใน <code>bug_report.yml</code>, <code>feature_request.yml</code> และ <code>config.yml</code> แล้วใช้งานฟอร์มบน GitHub ได้จริง",
            "เปิด Pull Request เข้า <code>main</code> บนหน้าเว็บ GitHub, ตรวจ Checks และ Merge แบบ Rebase พร้อมลบ Branch อัตโนมัติได้",
            "ตั้งค่า Branch Protection / Rulesets เพื่อบังคับ PR และ Linear History บน <code>main</code> รวมถึง Logout ออกจากเครื่องส่วนกลางได้ครบ",
        ],
        "tools": [
            "หน้าเว็บ GitHub (สำหรับเปิด Issue, เปิด Pull Request และตั้งค่า Branch Protection)",
            "ไฟล์ปลายทาง: <code>.github/ISSUE_TEMPLATE/*.yml</code> (มีโครง <code># TODO</code> อยู่แล้ว)",
            "ไฟล์ PR Template: <code>.github/pull_request_template.md</code> (มีให้ใน Repo แล้ว)",
            "วิดีโอประกอบ: <code>videos/02-pull-request-review.mp4</code>",
        ],
        "experiments": [
            ("L-01", "แทนที่ไฟล์ Issue Forms (<code>bug_report.yml</code>, <code>feature_request.yml</code>, <code>config.yml</code>) แล้ว Commit &amp; Push ขึ้น <code>feature/fast-blink</code>"),
            ("L-02", "ทดลองกดเปิด Issue จริงบนหน้าเว็บ GitHub (แท็บ <strong>Issues -&gt; New issue</strong>)"),
            ("L-03", "เปิดและ Merge Pull Request แบบ <strong>Rebase and merge</strong> บนหน้าเว็บ GitHub + ตั้ง Branch Protection + ซิงก์ <code>main</code>"),
        ],
        "details": [
            {
                "heading": "L-01 (ส่วนที่ 1/4): bug_report.yml — ลบ # TODO เดิมทั้งหมด แล้ววางส่วนหัวฟอร์ม",
                "steps": [
                    "เปิดไฟล์ <code>.github/ISSUE_TEMPLATE/bug_report.yml</code>",
                    "กด <strong>Ctrl+A ลบเนื้อหา <code># TODO</code> เดิมออกทั้งหมด</strong> ก่อนวางโค้ดส่วนที่ 1/4",
                    "จากนั้นนำส่วนที่ 2/4 ไปวางต่อท้ายไฟล์เดียวกันทันที",
                ],
                "code": """# [Ctrl+A ลบเนื้อหาเดิมทั้งหมดใน .github/ISSUE_TEMPLATE/bug_report.yml แล้ววาง]
name: Bug Report (แจ้งบั๊ก Firmware)
description: รายงานปัญหาที่พบในโปรเจกต์ ESP32 DOIT DevKit v1
title: "[Bug]: "
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        กรุณากรอกข้อมูลให้ครบถ้วนเพื่อให้ทีมจำลองปัญหาและแก้ไขได้เร็วขึ้นครับ

  - type: input
    id: version
    attributes:
      label: เวอร์ชันเฟิร์มแวร์ / Tag หรือ Commit
      description: ระบุ Tag (เช่น v1.0.0) หรือเลข Commit ที่พบปัญหา
      placeholder: v1.0.0
    validations:
      required: true

  - type: dropdown
    id: environment
    attributes:
      label: สภาพแวดล้อมที่พบปัญหา
      options:
        - DOIT ESP32 DevKit v1 (Hardware จริง)
        - PlatformIO Native Test ([env:native])
        - GitHub Actions CI
    validations:
      required: true""",
            },
            {
                "heading": "L-01 (ส่วนที่ 2/4): bug_report.yml — ต่อท้าย description และ checklist",
                "steps": [
                    "นำโค้ดด้านล่างนี้ไป<strong>ต่อท้าย</strong>ไฟล์ <code>.github/ISSUE_TEMPLATE/bug_report.yml</code> ให้ครบทั้ง 4 fields",
                ],
                "code": """  - type: textarea
    id: description
    attributes:
      label: อาการที่พบ & ขั้นตอนการทำซ้ำ (Steps to Reproduce)
      placeholder: |
        1. รันคำสั่ง...
        2. ผลลัพธ์ที่เกิดขึ้น...
        3. ผลลัพธ์ที่คาดหวัง...
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: ยืนยันเบื้องต้น
      options:
        - label: ทดสอบบน branch main หรือ release ล่าสุดแล้ว
          required: true""",
            },
            {
                "heading": "L-01 (ส่วนที่ 3/4): feature_request.yml &amp; config.yml — ลบ # TODO เดิมแล้ววางแทน",
                "steps": [
                    "เปิด <code>.github/ISSUE_TEMPLATE/feature_request.yml</code> แล้วกด <strong>Ctrl+A ลบโครงเดิมออกทั้งหมด</strong> ก่อนวางบล็อกแรก",
                    "เปิด <code>.github/ISSUE_TEMPLATE/config.yml</code> แล้วกด <strong>Ctrl+A ลบโครงเดิมออกทั้งหมด</strong> ก่อนวางบล็อกที่สอง",
                    "ส่วนไฟล์ <code>.github/pull_request_template.md</code> มีให้ครบใน Repo แล้วไม่ต้องสร้างใหม่",
                ],
                "code": """# === ไฟล์ที่ 1: .github/ISSUE_TEMPLATE/feature_request.yml (Ctrl+A แล้ววางทับ) ===
name: Feature Request (ขอฟีเจอร์ใหม่)
description: เสนอฟีเจอร์ใหม่หรือการปรับปรุงสำหรับโปรเจกต์ ESP32
title: "[Feat]: "
labels: ["enhancement"]

body:
  # ช่องกรอกปัญหาหรือความต้องการ
  - type: textarea
    id: problem
    attributes:
      label: ปัญหาหรือความต้องการ (Why)
      placeholder: เช่น ต้องการปรับความถี่ไฟกระพริบตามค่า Input
    validations: { required: true }

  - type: textarea
    id: solution
    attributes:
      label: แนวทางที่เสนอ (How)
      placeholder: เพิ่มฟังก์ชันใน lib/blink_math/ และเขียน Unit Test รองรับ
    validations: { required: true }

  - type: dropdown
    id: target_branch
    attributes:
      label: Branch เป้าหมาย (Linear History + Rebase)
      options: [main (PR + Rebase and merge), release/v* (เฉพาะแก้บั๊กก่อนปล่อยเวอร์ชัน)]
      default: 0""",
            },
            {
                "heading": "L-01 (ส่วนที่ 3/4 ต่อ): config.yml — วางทับเนื้อหาเดิมทั้งหมด",
                "steps": [
                    "วางบล็อก YAML ด้านล่างลงใน <code>.github/ISSUE_TEMPLATE/config.yml</code> (เฉพาะเนื้อหา YAML เท่านั้น)",
                ],
                "code": """# [Ctrl+A ลบเนื้อหาเดิมทั้งหมดใน .github/ISSUE_TEMPLATE/config.yml แล้ววางทับ]
blank_issues_enabled: false
contact_links:
  - name: คู่มือ Workshop (Docs)
    url: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms
    about: เอกสารอ้างอิงไวยากรณ์ YAML สำหรับ GitHub Issue Forms""",
            },
            {
                "heading": "L-01 (ส่วนที่ 4/4): ตรวจ YAML แล้ว Commit &amp; Push ขึ้น Branch feature/fast-blink",
                "steps": [
                    "รันคำสั่งตรวจไวยากรณ์ YAML เพื่อเช็กว่าพิมพ์ย่อหน้าไม่ผิด",
                    "เนื่องจากตอนนี้เราอยู่บน Branch <code>feature/fast-blink</code> ต่อจาก Lab 01 ให้ Stage ไฟล์ Issue Template แล้ว Commit บน Branch นี้ก่อน",
                    "Push ขึ้น <code>origin</code> ด้วยคำสั่ง <code>git push -u origin feature/fast-blink</code> เพื่อเตรียมเปิด Pull Request เข้า <code>main</code>",
                ],
                "images": [
                    ("../images/gh-02-issue-templates.png", "ตรวจสอบให้แน่ใจว่าทั้ง 3 ไฟล์ใน .github/ISSUE_TEMPLATE/ ถูกแก้ไขและ Commit เรียบร้อยแล้ว"),
                ],
                "code": """# ตรวจ YAML แล้ว Commit & Push ขึ้น branch feature/fast-blink (รันจาก workshop):
uv run --with pyyaml python -c "import yaml,glob; [yaml.safe_load(open(f,encoding='utf-8')) for f in glob.glob('../.github/**/*.yml',recursive=True)]; print('YAML OK')"
git add ../.github/ISSUE_TEMPLATE/
git commit -m "docs(github): add YAML issue forms and chooser config"
git push -u origin feature/fast-blink""",
            },
            {
                "heading": "L-02: กดเปิด Issue จริงบนหน้าเว็บ GitHub (สังเกตหมายเลข #Issue)",
                "steps": [
                    "เข้าหน้า Fork ของตัวเองบนเว็บ GitHub",
                    "<code>[1]</code> คลิกแท็บ <strong>Issues</strong>",
                    "<code>[2]</code> กดปุ่มเขียว <strong>New issue</strong>",
                    "เลือกฟอร์ม Feature Request หรือ Bug Report แล้วกรอกข้อมูลจนได้เลข Issue (เช่น <code>#1</code> หรือ <code>#2</code>)",
                    "จำเลข Issue นี้ไว้เพื่อนำไปพิมพ์ <code>Closes #&lt;เลข&gt;</code> ในขั้นตอนเปิด PR",
                ],
                "images": [
                    ("../images/anno-02-issues.png", "กดตามลำดับ: [1] คลิกแท็บ Issues -> [2] กดปุ่ม New issue เพื่อเลือก YAML Form"),
                    ("../images/anno-02-issue-detail.png", "ตัวอย่างหน้า Issue บน GitHub: [1] ดูเลข Issue (เช่น #2) และ [2] ดูป้าย Labels อัตโนมัติ"),
                ],
            },
            {
                "heading": "L-03: เปิด PR บนหน้าเว็บ GitHub แบบ Rebase and merge + ตั้ง Branch Protection",
                "steps": [
                    "บนเว็บ GitHub: <code>[1]</code> เข้าแท็บ <strong>Pull requests</strong> แล้วกด <code>[2] New pull request</code>",
                    "ในหน้า Compare: เลือก <code>[1] base: main &lt;- compare: feature/fast-blink</code> (เปลี่ยนช่องขวาจาก main เป็น <code>feature/fast-blink</code>)",
                    "พิมพ์ <code>Closes #&lt;เลข&gt;</code> ในกล่องข้อความแล้วกด <code>[2] Create pull request</code>",
                    "กดลูกศรข้างปุ่ม Merge เลือก <strong>Rebase and merge</strong> และกด <strong>Delete branch</strong> หลัง Merge เสร็จ จากนั้นกลับมาดึงโค้ดลง <code>main</code> ในเครื่อง",
                    "<strong>ตั้ง Branch Protection บนเว็บ GitHub:</strong> เข้า Repo -> <strong>Settings -> Branches -> Add classic branch protection rule</strong> -> ใส่ pattern <code>main</code> แล้วติ๊ก <strong>Require a pull request before merging</strong> และ <strong>Require linear history</strong>",
                ],
                "images": [
                    ("../images/anno-02-pulls.png", "บนหน้า Fork: [1] คลิกแท็บ Pull requests -> [2] กดปุ่ม New pull request"),
                    ("../images/anno-02-compare.png", "หน้า Compare: [1] เลือก base: main <- compare: feature/fast-blink -> ใส่ Closes #<เลข> -> [2] กด Create pull request"),
                ],
                "code": """# หลังกด Rebase and merge และ Delete branch บนหน้าเว็บ GitHub เสร็จแล้ว
# ให้สลับกลับมาที่ main ในเครื่องและดึงโค้ดล่าสุดลงมา:
git switch main
git pull origin main
git lg -n 5""",
            },
        ],
        "expected_output": """# บนหน้าเว็บ GitHub หลัง Merge PR ด้วย Rebase and merge:
✓ Merged commits into main from feature/fast-blink
✓ Issue #1 closed automatically (via "Closes #1")
✓ Branch feature/fast-blink deleted""",
        "results": [
            "L-02: เลข Issue และ Labels ที่แสดงบนหน้าเว็บ GitHub",
            "L-03: สถานะของ Pull Request หลังกด <strong>Rebase and merge</strong> บนหน้าเว็บ GitHub และผลหลังตั้ง Branch Protection",
        ],
        "questions": [
            "Q1: การใช้ Issue Form แบบ <code>.yml</code> ดีกว่าการปล่อยให้กรอก Issue แบบข้อความเปล่าอย่างไร?",
            "Q2: ตัวเลือก <strong>Require linear history</strong> ใน Branch Protection ช่วยป้องกันอะไร?",
            "Q3: ทำไมหลัง Merge PR เข้า <code>main</code> แล้วจึงควรลบ Branch ย่อยทิ้งทันที?",
        ],
        "exercise": {
            "code": "L-04",
            "steps": [
                "เปิด Issue 1 รายการด้วยฟอร์ม <code>feature_request.yml</code> บนหน้าเว็บ GitHub",
                "เปิด PR เข้า <code>main</code> บนหน้าเว็บ GitHub พร้อมใส่ <code>Closes #&lt;เลข&gt;</code> เพื่อปิด Issue แล้วกด <strong>Rebase and merge</strong>",
                "รัน <code>uv run scripts/verify.py --module 2</code> จากใน <code>workshop</code> เพื่อตรวจผล (หากใช้เครื่องห้องแล็บอย่าลืม Sign Out จากเว็บ GitHub เมื่อเลิกเรียน)",
            ],
            "snippet": """# ในรายละเอียด PR บนหน้าเว็บ GitHub ให้ใส่: Closes #<เลข>
git switch main
git pull origin main
uv run scripts/verify.py --module 2""",
        },
        "screenshots": [
            ("../images/anno-02-pr-detail.png", "ผลลัพธ์หลังเปิด PR และ Merge สำเร็จ: [1] ตรวจแท็บ Checks ผ่านครบ -> [2] สถานะเปลี่ยนเป็น Merged"),
        ],
    },
    {
        "slug": "LAB03-Pre_commit_Hooks",
        "title": "Lab 03: Pre-commit Hooks (Quality Gate ก่อน Commit)",
        "objectives": [
            "เรียนรู้การติดตั้งและใช้งาน Pre-commit Hooks เพื่อตรวจคุณภาพโค้ดในเครื่องก่อนเข้า Git History",
            "เข้าใจการทำงานของ <code>clang-format</code> (จัดฟอร์แมต C/C++) และ <code>conventional-pre-commit</code> (ตรวจ Commit Message)",
        ],
        "outcomes": [
            "แทนที่ Skeleton <code>.pre-commit-config.yaml</code> และติดตั้ง Git Hooks ทั้ง <code>pre-commit</code> และ <code>commit-msg</code> ได้",
            "แก้ไขปัญหาเมื่อ Hook บล็อกไฟล์ที่จัดฟอร์แมตผิดหรือข้อความ Commit ไม่ตรงมาตรฐานได้",
        ],
        "tools": [
            "<code>pre-commit</code> CLI (ติดตั้งไว้แล้วจาก <strong>Lab 00</strong>)",
            "ไฟล์ปลายทาง: <code>.pre-commit-config.yaml</code> (แทนที่โครง <code>repos: []</code>)",
            "ไฟล์กติกาฟอร์แมต: <code>.clang-format</code> (มีให้ใน Repo แล้ว ไม่ต้องสร้างใหม่)",
            "วิดีโอประกอบ: <code>videos/03-pre-commit-hooks.mp4</code>",
        ],
        "experiments": [
            ("L-01", "แทนที่ <code>.pre-commit-config.yaml</code>, Stage ไฟล์ด้วย <code>git add</code> และติดตั้ง Hook 2 Stage"),
            ("L-02", "ทดสอบ Break-Fix แยก 2 ขั้น: ขั้น A ให้ Hook จัดฟอร์แมตไฟล์ และขั้น B ทดสอบ Commit Message ผิดรูปแบบ"),
        ],
        "details": [
            {
                "heading": "L-01 (ส่วนที่ 1/4): .pre-commit-config.yaml — ลบ repos: [] เดิมออก แล้ววาง Hook พื้นฐาน",
                "steps": [
                    "เปิดไฟล์ <code>.pre-commit-config.yaml</code>",
                    "กด <strong>Ctrl+A ลบ <code>repos: []</code> และ <code># TODO</code> เดิมออกทั้งหมด</strong>",
                    "วางส่วนที่ 1/4 ลงไป แล้วนำส่วนที่ 2/4 และ 3/4 มาต่อท้ายในไฟล์เดียวกัน",
                ],
                "code": """# [Ctrl+A ลบเนื้อหาเดิมใน .pre-commit-config.yaml แล้ววางส่วนที่ 1-3 ต่อกัน]
repos:
  # ตรวจช่องว่างท้ายบรรทัด, บรรทัดปิดไฟล์, YAML และขนาดไฟล์
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']""",
            },
            {
                "heading": "L-01 (ส่วนที่ 2/4): .pre-commit-config.yaml — ต่อท้าย Hook จัด Format C/C++ (clang-format)",
                "steps": [
                    "วางต่อท้ายลงใน <code>repos:</code> ของ <code>.pre-commit-config.yaml</code>",
                    "Hook นี้จะอ้างอิงกติกาจากไฟล์ <code>.clang-format</code> ที่มีใน Repo แล้ว (Google Style, IndentWidth: 2, ColumnLimit: 100)",
                ],
                "code": """  # จัดรูปแบบโค้ด C/C++ อัตโนมัติตามไฟล์ .clang-format
  - repo: https://github.com/pre-commit/mirrors-clang-format
    rev: v23.1.5
    hooks:
      - id: clang-format
        types_or: [c++, c]""",
            },
            {
                "heading": "L-01 (ส่วนที่ 3/4): .pre-commit-config.yaml — ต่อท้าย Hook ตรวจ Commit Message",
                "steps": [
                    "วางต่อท้ายลงใน <code>repos:</code> เพื่อตรวจหัวข้อ Commit ใน Stage <code>commit-msg</code>",
                    "<em>หมายเหตุ:</em> คำสั่ง <code>pre-commit run --all-files</code> จะรันเฉพาะ Hook ตรวจไฟล์ ส่วน <code>conventional-pre-commit</code> จะทำงานตอนสั่ง <code>git commit</code>",
                ],
                "code": """  # ตรวจรูปแบบหัวข้อ Commit ให้ตรงตาม Conventional Commits
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.5.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, test, ci, chore, build]""",
            },
            {
                "heading": "L-01 (ส่วนที่ 4/4): Stage ไฟล์ config และติดตั้ง Git Hook ทั้ง 2 Stage",
                "steps": [
                    "<strong>สำคัญ:</strong> ไฟล์ <code>.pre-commit-config.yaml</code> ต้องวางไว้ที่ <strong>Root ของ Git Repo</strong> (ข้างๆ <code>.git/</code>) เพื่อให้ <code>git commit</code> อ่านได้ ส่วนตัวคำสั่งเรียกใช้แบบ Local จาก <code>workshop/.venv</code> ด้วย <code>uv run pre-commit ...</code>",
                    "รัน <code>git add ../.pre-commit-config.yaml</code> จากในโฟลเดอร์ <code>workshop</code> ก่อนติดตั้ง Hook เสมอ",
                    "ติดตั้ง Hook ทั้ง 2 Stage ด้วย <code>uv run pre-commit install</code> และ <code>uv run pre-commit install --hook-type commit-msg</code>",
                    "รัน <code>uv run pre-commit run --all-files</code> (รอบแรกจะโหลด Environment ของ Hook สักครู่)",
                    "รัน <code>git add ../.pre-commit-config.yaml</code> และ <code>git add .</code> อีกรอบเผื่อ <code>end-of-file-fixer</code> เติมบรรทัดว่างท้ายไฟล์ให้ แล้วจึง Commit",
                ],
                "code": """# 1. Stage ไฟล์ config ที่ root ก่อนเสมอ + ผูก Hook ทั้ง 2 stage เข้า .git/hooks/:
git add ../.pre-commit-config.yaml
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# 2. รันตรวจทุกไฟล์ (รอบแรกจะโหลด env ของ 3 hook repositories สักครู่):
uv run pre-commit run --all-files

# 3. Stage ไฟล์ที่ end-of-file-fixer อาจปรับปรุงให้เรียบร้อย แล้ว Commit:
git add ../.pre-commit-config.yaml
git add .
git commit -m "chore(hooks): configure pre-commit and clang-format" """,
            },
            {
                "heading": "L-02 (ขั้น A): ทดสอบ Format Hook — เปิดหน้าโค้ดดู clang-format แก้ช่องว่างอัตโนมัติ",
                "steps": [
                    "เปิดไฟล์ <code>src/main.cpp</code> (ใน <code>workshop</code>) ค้างไว้ใน VS Code แล้วเพิ่มบรรทัดที่<strong>เว้นช่องว่างเกินจงใจ</strong>ท้ายฟังก์ชัน <code>setup()</code> ตามตัวอย่างในกล่องโค้ดด้านล่าง แล้วกด Save",
                    "เปิดหน้าโค้ด <code>src/main.cpp</code> คู่กับ Terminal ไว้ แล้วรันคำสั่ง <code>uv run pre-commit run --all-files</code>",
                    "สังเกตใน Terminal จะขึ้น <code>clang-format...Failed</code> (<code>files were modified by this hook</code>) <strong>และดูที่หน้าโค้ด <code>src/main.cpp</code> จะเห็นว่าตัว Hook แก้ช่องว่างให้ถูก Format เป็น <code>int precommit_test = 1;</code> อัตโนมัติทันที</strong>",
                    "เมื่อ Hook แก้โค้ดให้ถูก Format เสร็จแล้ว ให้รัน <code>git add .</code> ใหม่เพื่อ Stage ไฟล์ที่ถูกจัดรูปแบบแล้ว",
                ],
                "code": """// 1. เปิด src/main.cpp ค้างไว้ แล้วเพิ่มบรรทัดที่เว้นวรรคเกินจงใจท้ายฟังก์ชัน setup():
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  blink_interval_ms = blink_math::clamp_interval(200);  // fast blink preset
  int   precommit_test =  1;   // <-- เว้นช่องว่างเกินจงใจ (กด Save แล้วเปิดหน้าโค้ดดูไว้)
}

# 2. รัน pre-commit ใน Terminal (จะขึ้น Failed แต่จะแก้ไฟล์ src/main.cpp ให้ถูก format อัตโนมัติ):
uv run pre-commit run --all-files

# 3. พอเห็นหน้าโค้ดถูกแก้เป็น `int precommit_test = 1;` แล้ว ให้ Stage ไฟล์ใหม่ด้วย git add .:
git add .""",
            },
            {
                "heading": "L-02 (ขั้น B): ทดสอบ Commit-Msg Hook บล็อกข้อความผิดกฎ และ Commit ให้ผ่าน",
                "steps": [
                    "หลังจากรัน <code>git add .</code> แล้ว ให้ลองสั่ง Commit ด้วยข้อความที่ผิดรูปแบบ Conventional Commits (<code>git commit -m \"bad commit message\"</code>)",
                    "สังเกตว่า <code>conventional-pre-commit</code> จะขึ้น <code>Failed</code> และบล็อกไม่ให้ Commit ทันที",
                    "แก้ข้อความ Commit ให้ตรงตามรูปแบบ Conventional Commits (<code>style: ...</code>) แล้วสั่ง Commit ใหม่จนสำเร็จ",
                ],
                "code": """# 1. ลองตั้งชื่อ Commit ผิดกฎ (จะถูก conventional-pre-commit บล็อกทันที):
git commit -m "bad commit message"

# 2. แก้ข้อความเป็น Conventional Commit แล้ว Commit ให้สำเร็จ:
git commit -m "style: format main.cpp with clang-format" """,
            },
        ],
        "expected_output": """$ pre-commit run --all-files
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
clang-format.............................................................Passed

$ git commit -m "bad commit message"
...
Conventional Commit......................................................Failed
- hook id: conventional-pre-commit
- exit code: 1
[Bad commit message] >> bad commit message""",
        "results": [
            "L-01: ผลลัพธ์จากการรัน <code>uv run pre-commit run --all-files</code>",
            "L-02: ข้อความแจ้งเตือนทั้งตอน <code>clang-format Failed</code> (ขั้น A) และ <code>Conventional Commit Failed</code> (ขั้น B)",
        ],
        "questions": [
            "Q1: เหตุใดเมื่อ <code>clang-format</code> ขึ้น Failed ในครั้งแรก เราจึงต้องรัน <code>git add</code> ใหม่อีกครั้งก่อน Commit?",
            "Q2: การใช้ Pre-commit ในเครื่องช่วยลดภาระของ GitHub Actions CI ได้อย่างไร?",
        ],
        "exercise": {
            "code": "L-03",
            "steps": [
                "ตรวจสอบ Hook ทั้งหมดในเครื่องด้วย <code>uv run pre-commit run --all-files</code>",
                "รัน <code>uv run scripts/verify.py --module 3</code> จากในโฟลเดอร์ <code>workshop</code> เพื่อยืนยันผล Lab 03",
            ],
            "snippet": """uv run pre-commit run --all-files
uv run scripts/verify.py --module 3""",
        },
        "screenshots": [
            ("../images/term-02-pre-commit.png", "ผลลัพธ์จริงของการรัน pre-commit run --all-files ผ่านทุก Hook"),
        ],
    },
    {
        "slug": "LAB04-PlatformIO_Unit_Testing",
        "title": "Lab 04: PlatformIO Unit Testing (Native Unity &amp; ESP32 Structure)",
        "objectives": [
            "เรียนรู้การแยก Pure C++ Logic (<code>lib/blink_math/</code>) ออกจากโค้ดฮาร์ดแวร์ (<code>Arduino.h</code>) เพื่อให้ทดสอบได้เร็ว",
            "เรียนรู้การเขียน Unit Test ด้วย Unity Framework และรันบน <code>[env:native]</code> รวมถึงโครงสร้าง Test สำหรับบอร์ด ESP32 จริง",
        ],
        "outcomes": [
            "แทนที่ Skeleton ใน <code>platformio.ini</code> เพื่อรองรับทั้ง <code>[env:esp32doit-devkit-v1]</code> และ <code>[env:native]</code> ได้",
            "แทนที่ Skeleton <code>test_main.cpp</code> ด้วย 4 Test Cases และรัน <code>pio test -e native</code> (หรือเข้าใจวิธีแก้ปัญหา Windows/CI fallback) ได้",
        ],
        "tools": [
            "PlatformIO CLI (<code>pio</code>) และ <code>gcc/g++</code> จาก <strong>Lab 00</strong>",
            "หากเครื่องไม่มี <code>gcc</code>: รัน <code>pio run</code> ตรวจ Build แล้วไปดูผล <code>[env:native]</code> บน Cloud CI ใน Lab 05 ได้",
            "ไฟล์ปลายทาง: <code>workshop/platformio.ini</code> และ <code>workshop/test/test_native/test_main.cpp</code>",
            "ไฟล์ศึกษาเพิ่มเติม: <code>workshop/test/test_esp32/test_hardware.cpp</code>",
            "วิดีโอประกอบ: <code>videos/04-platformio-unit-testing.mp4</code>",
        ],
        "experiments": [
            ("L-01", "แทนที่ <code>workshop/platformio.ini</code> เพื่อเพิ่ม <code>[env:native]</code> คู่กับ <code>[env:esp32doit-devkit-v1]</code>"),
            ("L-02", "แทนที่ <code>workshop/test/test_native/test_main.cpp</code> ด้วย Unit Tests ครบ 4 ฟังก์ชันของ <code>blink_math</code>"),
            ("L-03", "รัน <code>pio test -e native -v</code> เทียบกับ <code>pio run -e esp32doit-devkit-v1</code> แล้ว Commit/Push"),
        ],
        "details": [
            {
                "heading": "L-01: workshop/platformio.ini — Ctrl+A ลบเนื้อหาเดิมทั้งหมด แล้ววาง Dual Environment",
                "steps": [
                    "เปิดไฟล์ <code>workshop/platformio.ini</code>",
                    "กด <strong>Ctrl+A ลบเนื้อหา Starter เดิม (<code>; TODO</code>) ออกทั้งหมด</strong>",
                    "วางบล็อกโค้ดด้านล่างแทน (ห้ามวางต่อท้าย มิฉะนั้นจะ Error <code>section 'env:esp32doit-devkit-v1' already exists</code>)",
                ],
                "code": """; [Ctrl+A ลบเนื้อหาเดิมทั้งหมดใน workshop/platformio.ini แล้ววางแทน]
; สภาพแวดล้อมสำหรับบอร์ดจริง DOIT ESP32 DevKit v1
[env:esp32doit-devkit-v1]
platform = espressif32
board = esp32doit-devkit-v1
framework = arduino
monitor_speed = 115200
test_filter = test_esp32

; สภาพแวดล้อมสำหรับรัน Unit Test บนเครื่องคอมพิวเตอร์ (ไม่ต้องต่อบอร์ด)
[env:native]
platform = native
test_build_src = no
test_filter = test_native""",
            },
            {
                "heading": "L-02 (ส่วนที่ 1/2): test_main.cpp — ลบไฟล์เดิมทั้งหมด แล้ววาง Header & 4 Test Cases",
                "steps": [
                    "เปิดไฟล์ <code>workshop/test/test_native/test_main.cpp</code>",
                    "กด <strong>Ctrl+A ลบโค้ดเดิมทั้งหมด</strong> (รวม <code>test_starter_example</code> และ <code>main()</code> เดิม มิฉะนั้นจะมี <code>main()</code> ซ้ำ)",
                    "วางส่วนที่ 1/2 ลงไปก่อน แล้วตามด้วยส่วนที่ 2/2 ทันที",
                ],
                "code": """// [Ctrl+A ลบเนื้อหาเดิมทั้งหมดใน workshop/test/test_native/test_main.cpp แล้ววางส่วนที่ 1+2]
#include <unity.h>
#include "blink_math.h"

// ฟังก์ชันเตรียมและล้างค่าก่อน/หลังรันแต่ละ Test Case
void setUp(void) {}
void tearDown(void) {}

// ทดสอบการบวกเลขจำนวนเต็ม
void test_add_numbers_positive(void) {
  TEST_ASSERT_EQUAL_INT(5, blink_math::add_numbers(2, 3));
  TEST_ASSERT_EQUAL_INT(0, blink_math::add_numbers(-4, 4));
}

// ทดสอบการจำกัดช่วงเวลากระพริบให้อยู่ในช่วง 100-5000 ms
void test_clamp_interval_bounds(void) {
  TEST_ASSERT_EQUAL_INT(100, blink_math::clamp_interval(20));
  TEST_ASSERT_EQUAL_INT(500, blink_math::clamp_interval(500));
  TEST_ASSERT_EQUAL_INT(5000, blink_math::clamp_interval(9999));
}

// ทดสอบการสลับสถานะ LED (0 <-> 1)
void test_next_led_state_toggles(void) {
  TEST_ASSERT_EQUAL_UINT8(1, blink_math::next_led_state(0));
  TEST_ASSERT_EQUAL_UINT8(0, blink_math::next_led_state(1));
}

// ทดสอบการคำนวณคาบเวลารวมของ 1 รอบการกระพริบ
void test_calculate_cycle_ms(void) {
  TEST_ASSERT_EQUAL_INT(1000, blink_math::calculate_cycle_ms(400, 600));
  TEST_ASSERT_EQUAL_INT(100, blink_math::calculate_cycle_ms(10, 10));
}""",
            },
            {
                "heading": "L-02 (ส่วนที่ 2/2): test_main.cpp — ต่อท้ายฟังก์ชัน main() สั่งรัน Test Runner",
                "steps": [
                    "วางต่อท้ายลงในไฟล์ <code>workshop/test/test_native/test_main.cpp</code>",
                    "เปิด Suite ด้วย <code>UNITY_BEGIN()</code>, เรียก <code>RUN_TEST(...)</code> ครบทั้ง 4 ฟังก์ชัน แล้วคืนค่า Exit Code ด้วย <code>UNITY_END()</code>",
                ],
                "code": """int main(int argc, char** argv) {
  UNITY_BEGIN();
  RUN_TEST(test_add_numbers_positive);
  RUN_TEST(test_clamp_interval_bounds);
  RUN_TEST(test_next_led_state_toggles);
  RUN_TEST(test_calculate_cycle_ms);
  return UNITY_END();
}""",
            },
            {
                "heading": "L-03 (ขั้นที่ 1/2): รัน Test &amp; Build บนเครื่อง",
                "steps": [
                    "ศึกษาไฟล์ <code>test/test_esp32/test_hardware.cpp</code> ที่มีให้ใน <code>workshop</code>",
                    "หากเปิด Terminal หน้าต่างใหม่ ให้เพิ่ม PATH ของ MSYS2 (<code>$env:Path = \"C:\\msys64\\ucrt64\\bin;$env:Path\"</code>) ก่อนรัน Native Test",
                    "รัน <code>uv run pio test -e native -v</code> จากในโฟลเดอร์ Workspace <code>workshop</code>",
                    "รัน <code>uv run pio run -e esp32doit-devkit-v1</code> เพื่อคอมไพล์เฟิร์มแวร์ (ไม่ต้องเสียบบอร์ดจริง)",
                ],
                "code": """# 1. ตั้ง PATH ของ MSYS2 (หากเปิด Terminal ใหม่) แล้วรัน Native Unit Test:
$env:Path = "C:\\msys64\\ucrt64\\bin;$env:Path"
uv run pio test -e native -v

# 2. Build เฟิร์มแวร์ .bin สำหรับบอร์ด ESP32:
uv run pio run -e esp32doit-devkit-v1""",
            },
            {
                "heading": "L-03 (ขั้นที่ 2/2): บันทึกการเปลี่ยนแปลงขึ้น Git (เพื่อทดสอบบน CI ใน Lab 05)",
                "steps": [
                    "รัน <code>git add .</code> เพื่อ Stage ไฟล์ <code>platformio.ini</code> และ <code>test/test_native/test_main.cpp</code>",
                    "Commit ด้วยข้อความ Conventional Commits และ Push ขึ้น Fork",
                ],
                "code": """# Stage, Commit (pre-commit จะจัด clang-format ให้อัตโนมัติ) และ Push:
git add .
git commit -m "test(native): add [env:native] and blink_math unity tests"
git push origin HEAD""",
            },
        ],
        "expected_output": """(esp32-git-workshop) PS C:\\Users\\LabRoom\\Desktop\\git-practice\\workshop> uv run pio test -e native -v
Collected 2 tests (test_esp32, test_native)

Processing test_native in native environment
----------------------------------------------------------------------------------------------------
Building...
Testing...
test\\test_native\\test_main.cpp:35:test_add_numbers_positive:PASS
test\\test_native\\test_main.cpp:36:test_clamp_interval_bounds:PASS
test\\test_native\\test_main.cpp:37:test_next_led_state_toggles:PASS
test\\test_native\\test_main.cpp:38:test_calculate_cycle_ms:PASS

-----------------------
4 Tests 0 Failures 0 Ignored
OK
---------------------------------- native:test_native [PASSED] Took 2.08 seconds ----------------------------------

============================================= SUMMARY =============================================
Environment    Test         Status    Duration
-------------  -----------  --------  ------------
native         test_native  PASSED    00:00:02.083
============================ 4 test cases: 4 succeeded in 00:00:02.083 ============================""",
        "results": [
            "L-03 (Unit Test): จำนวน Test Cases ที่รันผ่านบน <code>[env:native]</code> (หรือบันทึก <code>[WARN]</code> กรณีเครื่องไม่มี <code>gcc</code>)",
            "L-03 (Firmware Build): ขนาด RAM และ Flash ที่ใช้จากการ Build <code>esp32doit-devkit-v1</code>",
        ],
        "questions": [
            "Q1: ทำไมเราต้องแยกฟังก์ชันคำนวณไว้ใน <code>lib/blink_math/</code> โดยไม่ใส่ <code>#include &lt;Arduino.h&gt;</code>?",
            "Q2: การตั้งค่า <code>test_build_src = no</code> ใน <code>[env:native]</code> มีไว้เพื่ออะไร?",
        ],
        "exercise": {
            "code": "L-04",
            "steps": [
                "ตรวจสอบว่ามี Test Cases ใน <code>test/test_native/test_main.cpp</code> ครบทั้ง 4 ฟังก์ชันของ <code>blink_math</code>",
                "รัน <code>uv run pio test -e native -v</code> และ <code>uv run scripts/verify.py --module 4</code> จากใน <code>workshop</code>",
            ],
            "snippet": """uv run pio test -e native -v
uv run scripts/verify.py --module 4""",
        },
        "screenshots": [
            ("../images/term-03-pio-build.png", "ผลลัพธ์จริงของการ Build เฟิร์มแวร์สำหรับ esp32doit-devkit-v1"),
        ],
    },
    {
        "slug": "LAB05-GitHub_Actions_CI_YAML",
        "title": "Lab 05: GitHub Actions Continuous Integration (CI) &amp; YAML Deep-Dive",
        "objectives": [
            "เข้าใจโครงสร้างไฟล์ YAML (<code>.github/workflows/ci.yml</code>), คีย์เวิร์ดหลัก และแหล่งค้นหา Actions จาก GitHub Marketplace",
            "ออกแบบ CI Pipeline 3 ขั้นตอน (<code>lint</code> -> <code>unit-test</code> -> <code>build-esp32</code>) โดยใช้ <code>uv</code> และ Caching",
        ],
        "outcomes": [
            "อธิบายความหมายของ <code>on</code>, <code>defaults.run.working-directory</code>, <code>jobs</code>, <code>needs</code>, <code>uses</code>, <code>with</code>, <code>run</code>, <code>if</code> ได้",
            "แทนที่ Skeleton <code>ci.yml</code>, ตรวจสอบผลการรัน CI บนแท็บ GitHub Actions และแก้ไขเมื่อทำ Break-Fix CI แดงได้",
        ],
        "tools": [
            "GitHub Actions &amp; GitHub Marketplace (<code>https://github.com/marketplace?type=actions</code>)",
            "ไฟล์ปลายทาง: <code>.github/workflows/ci.yml</code> (มีโครง <code>starter-placeholder</code> อยู่แล้ว ต้องลบทิ้งทั้งหมด)",
            "วิดีโอประกอบ: <code>videos/05-github-actions-ci.mp4</code>",
        ],
        "experiments": [
            ("L-01", "เปิด Actions บน Fork, ศึกษาตารางคีย์ YAML และแทนที่ <code>.github/workflows/ci.yml</code> (ลบ <code>starter-placeholder</code>)"),
            ("L-02", "Push PR เข้า <code>main</code>, ดูผลบนแท็บ Actions และทดสอบ Break-Fix จนกลับมาเขียว + ทดสอบ Artifact บน <code>release/v1.0.0</code>"),
        ],
        "details": [
            {
                "heading": "L-01 (ตารางอ้างอิง): ความหมายของ YAML Keys ใน GitHub Actions",
                "steps": [
                    "ทำความเข้าใจความหมายของคีย์หลักทั้งหมดใน <code>ci.yml</code> ก่อนลงมือวางโค้ด",
                    "<em>ข้อควรรู้:</em> <code>defaults.run.working-directory</code> ใช้เฉพาะกับคำสั่ง <code>run:</code> เท่านั้น ไม่ได้ครอบคลุม <code>uses:</code> เช่น <code>upload-artifact</code> จึงยังต้องเขียน path เต็ม <code>workshop/.pio/...</code>",
                ],
                "code": """# คีย์หลัก -> หน้าที่และความหมาย
# on:                  -> กำหนดเหตุการณ์ทริกเกอร์ ('release/**' ต้องใส่ quote กัน * กลายเป็น YAML alias)
# defaults.run:        -> ตั้งโฟลเดอร์เริ่มต้นให้ทุก step ที่เป็น `run:` (workshop)
# jobs / runs-on:      -> แยกกลุ่มงาน (เช่น lint, unit-test) บน VM Linux (ubuntu-latest)
# needs:               -> รอให้ Job ก่อนหน้าผ่านก่อน จึงค่อยเริ่ม Job ถัดไป
# uses: / with:        -> เรียก Action สำเร็จรูปจาก Marketplace (เช่น checkout@v7) พร้อมส่งพารามิเตอร์
# run:                 -> รันคำสั่ง Shell ใน Runner VM (setup-uv จะเพิ่ม ~/.local/bin เข้า PATH ให้ pio)
# if: / ${{ ... }}     -> เงื่อนไข + Expression เช่น startsWith(github.ref, ...), hashFiles('...')""",
            },
            {
                "heading": "L-01 (ส่วนที่ 1/4): ci.yml — Ctrl+A ลบ starter-placeholder เดิมออก แล้ววาง Trigger & Defaults",
                "steps": [
                    "เปิดไฟล์ <code>.github/workflows/ci.yml</code>",
                    "กด <strong>Ctrl+A ลบเนื้อหาเดิมทั้งหมด</strong> (รวม <code>on: workflow_dispatch:</code> และ job <code>starter-placeholder:</code> มิฉะนั้น <code>verify.py</code> จะ FAIL)",
                    "วางส่วนที่ 1/4 ถึง 4/4 ต่อกันในไฟล์เดียวกัน",
                ],
                "code": """# [Ctrl+A ลบ starter-placeholder เดิมใน .github/workflows/ci.yml แล้ววางส่วนที่ 1-4 ต่อกัน]
name: CI - Lint, Test & Build

on:
  push:
    branches: [main, 'release/**']
  pull_request:
    branches: [main]

defaults:
  run:
    working-directory: workshop""",
            },
            {
                "heading": "L-01 (ส่วนที่ 2/4): ci.yml — ต่อท้าย Job 1 (lint: ตรวจ Format & YAML ด้วย Pre-commit)",
                "steps": [
                    "ขอ Cloud Linux VM (<code>ubuntu-latest</code>)",
                    "ดึงโค้ดด้วย <code>checkout@v7</code>, ตั้งค่า Python/uv ด้วย <code>setup-uv@v10.3.3</code> และรัน <code>pre-commit/action@v3.0.1</code>",
                ],
                "code": """jobs:
  # Job 1: ตรวจรูปแบบโค้ดและ YAML ด้วย Pre-commit
  lint:
    name: Code Format & Lint Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Setup uv and Python
        uses: astral-sh/setup-uv@v10.3.3
        with:
          python-version: '3.12'
          enable-cache: false

      - name: Run pre-commit hooks
        uses: pre-commit/action@v3.0.1""",
            },
            {
                "heading": "L-01 (ส่วนที่ 3/4): ci.yml — ต่อท้าย Job 2 (unit-test: รัน Unity Test หลัง lint ผ่าน)",
                "steps": [
                    "ใช้ <code>needs: lint</code> เพื่อรอ Job แรกผ่านก่อน",
                    "Cache โฟลเดอร์ <code>~/.platformio/.cache</code> ผูก Key กับ <code>workshop/platformio.ini</code> แล้วรัน <code>pio test -e native -v</code>",
                ],
                "code": """  # Job 2: รัน Native Unit Test หลังจาก Job lint ผ่าน
  unit-test:
    name: Native Unit Tests (Unity)
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Setup uv and Python
        uses: astral-sh/setup-uv@v10.3.3
        with:
          python-version: '3.12'
          enable-cache: false

      - name: Cache PlatformIO native packages
        uses: actions/cache@v6
        with:
          path: ~/.platformio/.cache
          key: ${{ runner.os }}-pio-native-${{ hashFiles('workshop/platformio.ini') }}

      - name: Install PlatformIO CLI
        run: uv tool install platformio

      - name: Run native unit tests
        run: pio test -e native -v""",
            },
            {
                "heading": "L-01 (ส่วนที่ 4/4): ci.yml — ต่อท้าย Job 3 (build-esp32: คอมไพล์ .bin & Upload Artifact)",
                "steps": [
                    "รอ <code>needs: unit-test</code> แล้วคอมไพล์เฟิร์มแวร์จริง <code>esp32doit-devkit-v1</code>",
                    "หากเป็น Branch <code>release/**</code> ให้แนบไฟล์ <code>.bin</code> เก็บไว้ด้วย <code>upload-artifact@v7</code>",
                ],
                "code": """  # Job 3: คอมไพล์เฟิร์มแวร์ ESP32 หลังจาก Job unit-test ผ่าน
  build-esp32:
    name: Build Firmware (esp32doit-devkit-v1)
    runs-on: ubuntu-latest
    needs: unit-test
    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Setup uv and Python
        uses: astral-sh/setup-uv@v10.3.3
        with:
          python-version: '3.12'
          enable-cache: false

      - name: Cache PlatformIO ESP32 toolchain
        uses: actions/cache@v6
        with:
          path: ~/.platformio
          key: ${{ runner.os }}-pio-esp32-${{ hashFiles('workshop/platformio.ini') }}

      - name: Install PlatformIO CLI
        run: uv tool install platformio

      - name: Build ESP32 firmware
        run: pio run -e esp32doit-devkit-v1

      - name: Upload release candidate binaries
        if: startsWith(github.ref, 'refs/heads/release/')
        uses: actions/upload-artifact@v7
        with:
          name: rc-firmware-${{ github.sha }}
          path: |
            workshop/.pio/build/esp32doit-devkit-v1/firmware.bin
            workshop/.pio/build/esp32doit-devkit-v1/bootloader.bin
            workshop/.pio/build/esp32doit-devkit-v1/partitions.bin
          retention-days: 7""",
            },
            {
                "heading": "L-02: Push CI ขึ้น Fork, ดูผล 3 Jobs บนแท็บ Actions และทดสอบ Break-Fix",
                "steps": [
                    "ตรวจ YAML ด้วย <code>pre-commit run check-yaml --all-files</code> จากนั้น Commit และ Push บน Branch <code>ci/add-workflow</code>",
                    "เปิด Pull Request เข้า <code>main</code> บน Fork ของตัวเอง",
                    "เข้าแท็บ <strong>Actions</strong> บนหน้าเว็บ GitHub -> <code>[1]</code> เลือก Workflow <strong>CI - Lint, Test &amp; Build</strong> -> <code>[2]</code> คลิกชื่อ Run เพื่อดูกราฟ 3 Jobs",
                    "<strong>Break &amp; Fix:</strong> ลองแก้ <code>test_add_numbers_positive</code> ใน <code>test_main.cpp</code> ให้ Assert ผิด (<code>99</code>) แล้ว Push ซ้ำดู CI แดง -> อ่าน Log -> แก้กลับเป็น <code>5</code> จนเขียวแล้ว Rebase &amp; Merge เข้า <code>main</code>",
                ],
                "images": [
                    ("../images/anno-05-actions-list.png", "บนแท็บ Actions: [1] เลือก Workflow CI - Lint, Test & Build -> [2] คลิกชื่อ Run เพื่อดูรายละเอียด 3 Jobs"),
                ],
                "code": """# 1. ตรวจ YAML + Commit & Push ขึ้น Branch เพื่อเปิด PR เข้า main (รันจาก workshop):
uv run pre-commit run check-yaml --all-files
git switch -c ci/add-workflow main
git add ../.github/workflows/ci.yml
git commit -m "ci: add lint, native test and esp32 build workflow"
git push -u origin ci/add-workflow

# 2. (Break-Fix) แก้ test_add_numbers_positive เป็น 99 แล้ว Push -> ดู CI แดงบนแท็บ Actions -> แก้กลับเป็น 5!""",
            },
        ],
        "expected_output": """# บนหน้าเว็บ GitHub -> แท็บ Actions -> เลือก Workflow "CI - Lint, Test & Build":
✓ Code Format & Lint Check          (passed)
✓ Native Unit Tests (Unity)         (passed)
✓ Build Firmware (esp32doit-devkit-v1) (passed)

# และบนหน้า Pull Request:
All checks have passed (3/3 successful checks)""",
        "results": [
            "L-01: เวลาที่ใช้ในแต่ละ Job (<code>lint</code>, <code>unit-test</code>, <code>build-esp32</code>) บน GitHub Actions",
            "L-02: อาการที่เกิดขึ้นบนหน้า Pull Request เมื่อ Unit Test ใน CI ไม่ผ่าน และผลหลังแก้กลับให้เขียว",
        ],
        "questions": [
            "Q1: เหตุใดใน <code>ci.yml</code> จึงต้องระบุ <code>defaults: run: working-directory: workshop</code> (และเหตุใด <code>upload-artifact</code> ยังต้องเขียน path ขึ้นต้นด้วย <code>workshop/</code>)?",
            "Q2: คีย์เวิร์ด <code>needs: unit-test</code> ใน Job <code>build-esp32</code> ทำหน้าที่อะไร?",
            "Q3: การทำ <code>actions/cache@v6</code> กับโฟลเดอร์ <code>~/.platformio</code> ช่วยเรื่องอะไร?",
        ],
        "exercise": {
            "code": "L-03",
            "steps": [
                "Merge PR ที่มี <code>ci.yml</code> เข้า <code>main</code> บน Fork ของตัวเอง",
                "ตรวจดูบนหน้าเว็บ GitHub แท็บ <strong>Actions</strong> ว่าทั้ง 3 Jobs ผ่านสีเขียวครบ (และลอง Push branch <code>release/v1.0.0</code> เพื่อดู Artifact <code>rc-firmware-*</code>)",
                "รัน <code>uv run scripts/verify.py --module 5</code> จากใน <code>workshop</code> เพื่อตรวจไฟล์ workflow ในเครื่อง",
            ],
            "snippet": """uv run scripts/verify.py --module 5""",
        },
        "screenshots": [
            ("../images/anno-05-actions-graph.png", "ผลลัพธ์หลังคลิก Run บนเว็บ GitHub: กราฟ 3 Jobs ([1] Lint -> [2] Unit Test -> [3] Build ESP32) ผ่านสีเขียวครบ"),
        ],
    },
    {
        "slug": "LAB06-Release_Tag_and_Firmware_Bin",
        "title": "Lab 06: Automated Release (CD), Tagging, Flashing &amp; Shared-PC Cleanup",
        "objectives": [
            "เข้าใจความแตกต่างระหว่าง <code>firmware.bin</code> (สำหรับ OTA) กับ <code>merged-firmware.bin</code> (สำหรับ Flash ใหม่ไฟล์เดียวที่ <code>0x0</code>)",
            "เรียนรู้การทำงานของ <code>release.yml</code> เมื่อ Push Tag <code>v*.*.*</code>, การนำไฟล์ไป Flash ด้วย <code>esptool</code> และการล้างบัญชีออกจากเครื่องส่วนกลาง",
        ],
        "outcomes": [
            "แทนที่ Skeleton <code>release.yml</code>, ปล่อยเวอร์ชันผ่าน <code>git tag -a v1.0.0</code> และสร้าง GitHub Release อัตโนมัติได้",
            "อธิบายวิธีนำไฟล์จาก Release ไป Flash ลงบอร์ด DOIT ESP32 DevKit v1 ได้ และทำ Shared-PC Cleanup ได้ครบ 3 จุด",
        ],
        "tools": [
            "เครื่องมือ <code>esptool</code> (ติดตั้งไว้แล้วจาก <strong>Lab 00</strong>) หรือเว็บ <code>https://espressif.github.io/esptool-js/</code>",
            "ไฟล์ปลายทาง: <code>.github/workflows/release.yml</code> (มีโครง <code>starter-placeholder</code> อยู่แล้ว ต้องลบทิ้งทั้งหมด)",
            "วิดีโอประกอบ: <code>videos/06-github-actions-release.mp4</code>",
        ],
        "experiments": [
            ("L-01", "แทนที่ <code>.github/workflows/release.yml</code> (ลบ <code>starter-placeholder</code>), Merge เข้า <code>main</code> และติด Tag <code>v1.0.0</code>"),
            ("L-02", "ตรวจสอบไฟล์ Asset ในหน้า GitHub Releases และคำสั่ง Flash ด้วย <code>esptool</code>"),
            ("L-03", "ปฏิบัติตาม Checklist ออกจากบัญชีครบทั้ง 3 จุดก่อนลุกจากเครื่องคอมพิวเตอร์มหาวิทยาลัย"),
        ],
        "details": [
            {
                "heading": "L-01 (ส่วนที่ 1/3): release.yml — Ctrl+A ลบ starter-placeholder เดิม แล้ววาง Trigger Tag & Permissions",
                "steps": [
                    "เปิดไฟล์ <code>.github/workflows/release.yml</code>",
                    "กด <strong>Ctrl+A ลบเนื้อหาเดิมทั้งหมด</strong> (รวม <code>workflow_dispatch:</code> และ <code>starter-placeholder:</code>)",
                    "วางส่วนที่ 1/3, 2/3 และ 3/3 ต่อกันในไฟล์เดียวกัน",
                ],
                "code": """# [Ctrl+A ลบ starter-placeholder เดิมใน .github/workflows/release.yml แล้ววางส่วนที่ 1-3]
name: Release Firmware (CD)

on:
  push:
    tags: ['v*.*.*']

permissions:
  contents: write

defaults:
  run:
    working-directory: workshop""",
            },
            {
                "heading": "L-01 (ส่วนที่ 2/3): release.yml — ต่อท้าย Job release (Setup, Test & Build Firmware)",
                "steps": [
                    "ติดตั้ง <code>platformio</code> และ <code>esptool</code> ด้วย <code>uv tool install</code>",
                    "รัน <code>pio test -e native</code> ซ้ำอีกครั้งก่อนสั่ง Compile ไฟล์ <code>.bin</code>",
                ],
                "code": """jobs:
  # Job สำหรับทดสอบและคอมไพล์เฟิร์มแวร์เมื่อมี Tag เวอร์ชัน
  release:
    name: Build & Publish ESP32 Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Setup uv and Python
        uses: astral-sh/setup-uv@v10.3.3
        with:
          python-version: '3.12'
          enable-cache: false

      - name: Cache PlatformIO ESP32 toolchain
        uses: actions/cache@v6
        with:
          path: ~/.platformio
          key: ${{ runner.os }}-pio-esp32-${{ hashFiles('workshop/platformio.ini') }}

      - name: Install PlatformIO and esptool
        run: |
          uv tool install platformio
          uv tool install esptool

      - name: Run native unit tests
        run: pio test -e native

      - name: Build ESP32 firmware
        run: pio run -e esp32doit-devkit-v1""",
            },
            {
                "heading": "L-01 (ส่วนที่ 3/3): release.yml — ต่อท้ายด้วย esptool merge-bin & action-gh-release",
                "steps": [
                    "<strong>ระวังการย่อหน้า YAML:</strong> 2 step ด้านล่างต้องเว้น 6 ช่องให้ตรงกับ <code>- uses:</code> ด้านบน",
                    "คำสั่ง <code>merge-bin</code> ใช้ <code>shell: bash</code> บน GitHub Runner จึงใช้ <code>\\</code> ต่อบรรทัดได้ (แต่ใน PowerShell บนเครื่องห้ามใช้ <code>\\</code> ต่อบรรทัด)",
                    "ส่วน <code>files:</code> ของ <code>action-gh-release</code> ยังต้องเขียน path เต็มขึ้นต้นด้วย <code>workshop/dist/...</code>",
                ],
                "code": """      - name: Prepare Release Binaries
        shell: bash
        run: |
          mkdir -p dist
          BUILD_DIR=".pio/build/esp32doit-devkit-v1"
          cp "${BUILD_DIR}/firmware.bin" "dist/esp32doit-${GITHUB_REF_NAME}-firmware.bin"
          esptool --chip esp32 merge-bin \\
            -o "dist/esp32doit-${GITHUB_REF_NAME}-merged-firmware.bin" \\
            --flash-mode dio --flash-freq 40m --flash-size 4MB \\
            0x1000 "${BUILD_DIR}/bootloader.bin" \\
            0x8000 "${BUILD_DIR}/partitions.bin" \\
            0x10000 "${BUILD_DIR}/firmware.bin"

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v3
        with:
          generate_release_notes: true
          files: |
            workshop/dist/esp32doit-${{ github.ref_name }}-firmware.bin
            workshop/dist/esp32doit-${{ github.ref_name }}-merged-firmware.bin""",
            },
            {
                "heading": "L-02: นำ release.yml เข้า main, ติด Tag v1.0.0, โหลด .bin และ Flash ที่ 0x0",
                "steps": [
                    "Commit และเปิด PR นำ <code>release.yml</code> เข้า <code>main</code> บน Fork ก่อน (เช่นผ่าน Branch <code>release/v1.0.0</code>) แล้วกด <strong>Rebase and merge</strong>",
                    "ดึง <code>main</code> ล่าสุดที่มี <code>release.yml</code> ลงเครื่อง",
                    "ติด Tag <code>v1.0.0</code> และ Push Tag ขึ้น <code>origin</code> (หากติด Tag ผิดพลาด ลบแล้วทำใหม่ได้ด้วย <code>git tag -d v1.0.0</code> และ <code>git push origin :refs/tags/v1.0.0</code>)",
                    "เปิดหน้า <strong>Releases</strong> บนเว็บ GitHub -> <code>[1]</code> เปิดดู Assets -> <code>[2]</code> ดาวน์โหลดไฟล์ <code>*-merged-firmware.bin</code> เพื่อนำไป Flash ที่ Address <code>0x0</code>",
                ],
                "images": [
                    ("../images/anno-06-releases.png", "ตัวอย่างหน้า GitHub Release (จากเวอร์ชัน v0.1.0 — ในงานของคุณจะแสดง v1.0.0): [1] เปิดดู Assets -> [2] คลิกโหลดไฟล์ *-merged-firmware.bin"),
                ],
                "code": """# 1. Commit + PR release.yml เข้า main บน Fork ก่อน (เช่นผ่าน release/v1.0.0, รันจาก workshop):
git switch -c release/v1.0.0 main
git add ../.github/workflows/release.yml
git commit -m "ci(cd): add release workflow for v*.*.* tags"
git push -u origin release/v1.0.0
# -> เปิด PR เข้า main แล้วกด Rebase and merge

# 2. ดึง main ล่าสุดที่มี release.yml แล้วติด Tag v1.0.0 และ Push:
git switch main
git pull origin main
git tag -a v1.0.0 -m "release: v1.0.0"
git push origin v1.0.0

# 3. Flash ผ่าน Terminal ด้วย esptool จาก workshop/.venv (เปลี่ยน COM3 เป็นพอร์ตของบอร์ด):
uv run esptool --chip esp32 --port COM3 --baud 460800 write-flash 0x0 esp32doit-v1.0.0-merged-firmware.bin
# หรือใช้เว็บ https://espressif.github.io/esptool-js/ -> Connect -> 0x0 -> เลือก merged-firmware.bin""",
            },
            {
                "heading": "L-03: Shared-PC Logout Checklist (ทำครบ 3 จุดก่อนลุกจากเครื่องมหาวิทยาลัย)",
                "steps": [
                    "<strong>จุดที่ 1 — VS Code:</strong> คลิกไอคอน <strong>Accounts</strong> (รูปคนมุมซ้ายล่าง) -> เลือกบัญชี GitHub -> กด <strong>Sign Out</strong>",
                    "<strong>จุดที่ 2 — Windows Credential Manager:</strong> ลบ Token ของ Git ออกจากเครื่อง (<code>cmdkey /list</code> และ <code>cmdkey /delete:git:https://github.com</code> หรือลบผ่าน Control Panel)",
                    "<strong>จุดที่ 3 — Browser &amp; Workspace:</strong> กด <strong>Sign out</strong> บนเว็บ <code>github.com</code> แล้วลบโฟลเดอร์ <code>$HOME\\Desktop\\git-practice</code> และไฟล์ <code>.bin</code> ใน Downloads ออก",
                ],
                "code": """# [1] VS Code: คลิกไอคอน Accounts (มุมซ้ายล่าง) -> <username> (GitHub) -> Sign Out

# [2] Windows Credential Manager: ตรวจและลบ Token ของ Git ในเครื่อง Windows
cmdkey /list
# cmdkey /delete:git:https://github.com  (หรือลบผ่าน Control Panel -> Credential Manager)

# [3] Browser & Workspace: กด Sign out บน github.com แล้วลบโฟลเดอร์งานบน Desktop
cd $HOME\\Desktop
Remove-Item -Recurse -Force $HOME\\Desktop\\git-practice""",
            },
        ],
        "expected_output": """# บนหน้าเว็บ GitHub -> แท็บ Releases:
v1.0.0 (Latest)
Assets:
  - esp32doit-v1.0.0-firmware.bin
  - esp32doit-v1.0.0-merged-firmware.bin

$ uv run scripts/verify.py --all
...
Summary: 19 PASS | 0 FAIL | 0 WARN
# (หมายเหตุ: หากไม่ได้ใช้ gh หรือเครื่องไม่มี gcc จะแสดง [WARN] ในส่วนที่เกี่ยวข้องแทน [FAIL])""",
        "results": [
            "L-02 (Assets): รายชื่อไฟล์ Assets ที่ปรากฏในหน้า GitHub Release <code>v1.0.0</code>",
            "L-02 (Binary Size): ขนาดไฟล์ <code>firmware.bin</code> เทียบกับ <code>merged-firmware.bin</code> (ทำไมจึงต่างกัน ~65 KB)",
        ],
        "questions": [
            "Q1: เพราะเหตุใด GitHub Release จึงควรแนบทั้ง <code>firmware.bin</code> และ <code>merged-firmware.bin</code>?",
            "Q2: เหตุใดเราจึงควรติด Tag หลังจาก Rebase/Merge เข้า <code>main</code> เสร็จแล้ว แทนที่จะติด Tag ก่อน Rebase?",
        ],
        "exercise": {
            "code": "L-04",
            "steps": [
                "ปล่อย Release เวอร์ชัน <code>v1.0.0</code> ใน Fork ของตัวเองและตรวจหน้า <strong>Releases</strong> บนเว็บ GitHub",
                "รัน <code>uv run scripts/verify.py --all</code> จากในโฟลเดอร์ <code>workshop</code> เพื่อเก็บหลักฐานผลลัพธ์",
                "ทำตามขั้นตอน Shared-PC Cleanup (<code>L-03</code>) ครบทั้ง 3 จุดก่อนลุกจากเครื่อง",
            ],
            "snippet": """uv run scripts/verify.py --all""",
        },
        "screenshots": [
            ("../images/term-04-verify.png", "ตัวอย่างผลรัน uv run scripts/verify.py --all (จุดที่ยังไม่ได้ทำบนเครื่อง/GitHub จะขึ้น [WARN]/[FAIL])"),
        ],
    },
]

TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <title>{title}</title>
  <style>
    @page {{
      size: A4;
      margin: 18mm 14mm 16mm 14mm;
    }}
    * {{ box-sizing: border-box; }}
    em, i {{ font-style: normal; }}
    body {{
      font-family: "Sarabun", sans-serif;
      color: #111827;
      font-size: 14pt;
      line-height: 1.5;
      margin: 0;
      padding: 0;
      background: #ffffff;
    }}
    h1.lab-title {{
      text-align: center;
      font-size: 16pt;
      font-weight: 700;
      text-decoration: underline;
      margin: 6px 0 14px 0;
      color: #0f172a;
    }}
    h3.sec {{
      font-size: 16pt;
      font-weight: 700;
      margin: 21pt 0 6pt 0;
      color: #0f172a;
      break-after: avoid;
      page-break-after: avoid;
    }}
    .step-heading {{
      font-size: 16pt;
      font-weight: 700;
      margin: 21pt 0 6pt 0;
      color: #0f172a;
      break-after: avoid;
      page-break-after: avoid;
    }}
    ol, ul {{
      margin: 4px 0 8px 0;
      padding-left: 24px;
    }}
    li {{
      margin-bottom: 4px;
      font-size: 14pt;
    }}
    .step-list {{
      margin: 4px 0 8px 12px;
      padding-left: 22px;
      color: #1e293b;
    }}
    .step-list li {{
      margin-bottom: 4px;
      font-size: 14pt;
    }}
    code {{
      font-family: "Sarabun", sans-serif;
      font-size: 14pt;
      background: #f1f5f9;
      padding: 1px 4px;
      border-radius: 3px;
    }}
    .exp-row {{
      margin: 5px 0 5px 12px;
      font-size: 14pt;
    }}
    .exp-code {{
      text-decoration: underline;
      font-weight: 700;
      margin-right: 6px;
    }}
    .code-box {{
      background: #f8fad2;
      border: 1px solid #475569;
      padding: 10px 14px;
      margin: 14pt 0 14pt 12px;
      font-family: "Sarabun", sans-serif;
      font-size: 14pt;
      line-height: 1.45;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-wrap: anywhere;
      color: #0f172a;
      break-inside: avoid;
    }}
    .term-box {{
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 4px;
      padding: 10px 14px;
      margin: 14pt 0 14pt 12px;
      font-family: "Sarabun", sans-serif;
      font-size: 14pt;
      line-height: 1.45;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-wrap: anywhere;
      color: #e2e8f0;
      break-inside: avoid;
    }}
    .fill-line {{
      border-bottom: 1px solid #334155;
      height: 22px;
      margin: 4px 0 8px 12px;
    }}
    .q-block {{
      margin: 8px 0 10px 12px;
      font-size: 14pt;
      break-inside: avoid;
    }}
    .shot-grid {{
      display: grid;
      grid-template-columns: {shot_cols};
      gap: 21pt;
      margin: 21pt 0 21pt 12px;
    }}
    .shot-card {{
      border: 1px solid #cbd5e1;
      padding: 8px;
      background: #ffffff;
      text-align: center;
      break-inside: avoid;
    }}
    .shot-card img {{
      width: 100%;
      height: auto;
      display: block;
      border: 1px solid #e2e8f0;
    }}
    .shot-cap {{
      font-size: 14pt;
      color: #334155;
      margin-top: 6px;
    }}
    .page-break {{ page-break-before: always; }}
  </style>
</head>
<body>
  <h1 class="lab-title">{title}</h1>

  <h3 class="sec">วัตถุประสงค์การเรียนรู้ (Objective)</h3>
  <ol>{objectives_html}</ol>

  <h3 class="sec">ผลลัพธ์การเรียนรู้ (Learning Outcomes)</h3>
  <ol>{outcomes_html}</ol>

  <h3 class="sec">เครื่องมือและไฟล์ที่ต้องเตรียม (Tools &amp; Prerequisites)</h3>
  <ul>{tools_html}</ul>

  <h3 class="sec">การทดลอง (Experiments)</h3>
  {experiments_html}

  <div class="page-break"></div>

  <h3 class="sec" style="text-decoration: underline;">รายละเอียดการทดลองและขั้นตอนปฏิบัติ (Step-by-Step Guide &amp; Code):</h3>
  {details_html}

  <h3 class="sec">ตัวอย่างผลลัพธ์ใน Terminal (Expected Output)</h3>
  <div class="term-box">{expected_output_html}</div>

  <h3 class="sec">บันทึกผล (Results)</h3>
  {results_html}

  <h3 class="sec" style="text-decoration: underline;">แบบฝึกหัด</h3>
  <div class="exp-row">
    <span class="exp-code">{ex_code}:</span>
  </div>
  {ex_steps_html}
  <div class="code-box">{ex_snippet}</div>

  <h3 class="sec" style="text-decoration: underline;">ภาพประกอบผลลัพธ์จริง (Screenshots)</h3>
  <div class="shot-grid">
    {shots_html}
  </div>
</body>
</html>
"""


def _render_steps_html(steps: list[str]) -> str:
    items = "".join(f"<li>{s}</li>" for s in steps)
    return f'<ol class="step-list">{items}</ol>'


def build_lab(lab: dict) -> None:
    objectives_html = "".join(f"<li>{o}</li>" for o in lab["objectives"])
    outcomes_html = "".join(f"<li>{o}</li>" for o in lab["outcomes"])
    tools_html = "".join(f"<li>{t}</li>" for t in lab["tools"])
    experiments_html = "".join(
        f'<div class="exp-row"><span class="exp-code">{code}:</span> {desc}</div>'
        for code, desc in lab["experiments"]
    )
    detail_blocks = []
    for item in lab["details"]:
        heading = item["heading"]
        steps = item.get("steps", [])
        desc = item.get("desc", "")
        code = item.get("code", "")
        code_font_size = item.get("code_font_size", 14)
        imgs = item.get("images", [])
        blk = f'<div class="step-heading">{heading}</div>'
        for src, cap in imgs:
            blk += f'<div class="shot-card" style="margin:21pt 0 21pt 12px;"><img src="{src}" alt="{html.escape(cap)}"/><div class="shot-cap">{html.escape(cap)}</div></div>'
        if steps:
            blk += _render_steps_html(steps)
        elif desc:
            blk += f'<div class="exp-row">{desc}</div>'
        if code:
            style_attr = f' style="font-size: {code_font_size}pt;"' if code_font_size != 14 else ""
            blk += f'<div class="code-box"{style_attr}>{html.escape(code)}</div>'
        detail_blocks.append(blk)
    details_html = "".join(detail_blocks)
    expected_output_html = html.escape(lab["expected_output"])
    results_html = "".join(
        f'<div class="q-block">{r}<div class="fill-line"></div><div class="fill-line"></div></div>'
        for r in lab["results"]
    )
    ex_steps = lab["exercise"].get("steps") or ([lab["exercise"]["desc"]] if lab["exercise"].get("desc") else [])
    ex_steps_html = _render_steps_html(ex_steps)
    shot_cols = "1fr"
    shots_html = "".join(
        f'<div class="shot-card"><img src="{src}" alt="{html.escape(cap)}"/><div class="shot-cap">{html.escape(cap)}</div></div>'
        for src, cap in lab["screenshots"]
    )

    rendered = TEMPLATE.format(
        title=lab["title"],
        objectives_html=objectives_html,
        outcomes_html=outcomes_html,
        tools_html=tools_html,
        experiments_html=experiments_html,
        details_html=details_html,
        expected_output_html=expected_output_html,
        results_html=results_html,
        ex_code=lab["exercise"]["code"],
        ex_steps_html=ex_steps_html,
        ex_snippet=html.escape(lab["exercise"]["snippet"]),
        shot_cols=shot_cols,
        shots_html=shots_html,
    )

    html_path = HTML_DIR / f"{lab['slug']}.html"
    pdf_path = LABS_DIR / f"{lab['slug']}.pdf"
    html_path.write_text(rendered, encoding="utf-8")

    subprocess.run(
        [
            EDGE_EXE,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            f"file:///{str(html_path).replace(chr(92), '/')}",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Generated: exercises/labs/{pdf_path.name} ({pdf_path.stat().st_size} bytes)")


def main() -> None:
    for lab in LABS:
        build_lab(lab)


if __name__ == "__main__":
    main()
