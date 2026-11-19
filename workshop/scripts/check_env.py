#!/usr/bin/env python3
"""
Pre-Workshop Environment Check
รันเช็กความพร้อมเครื่องก่อนเริ่มเรียน Workshop (Git, uv, pre-commit, PlatformIO, esptool, gcc, Windows TEMP)
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parent if (PROJECT_DIR.parent / ".git").exists() else PROJECT_DIR


def check_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        out = (p.stdout or p.stderr).strip().splitlines()
        return p.returncode == 0, (out[0] if out else "")
    except Exception as exc:
        return False, str(exc)


def find_local_tool(name: str) -> str:
    for candidate in (
        PROJECT_DIR / ".venv" / "Scripts" / f"{name}.exe",
        PROJECT_DIR / ".venv" / "bin" / name,
    ):
        if candidate.exists():
            return str(candidate)
    return shutil.which(name) or ""


def find_pio_fallback() -> str:
    home = Path.home()
    for c in [
        home / ".platformio" / "penv" / "Scripts" / "pio.exe",
        home / ".platformio" / "penv" / "bin" / "pio",
    ]:
        if c.exists():
            return str(c)
    return ""


def find_esptool() -> str:
    for name in ("esptool", "esptool.py"):
        found = find_local_tool(name)
        if found:
            return found
    return ""


def main() -> int:
    print("=== Pre-Workshop Environment Check ===\n")
    fails = 0
    warns = 0

    if not (PROJECT_DIR / "platformio.ini").exists():
        print("[WARN] ไม่พบ platformio.ini ในโฟลเดอร์ workshop (กรุณาเปิดโฟลเดอร์ workshop เป็น workspace หลัก)")
        warns += 1

    # 1. Git & Identity
    ok, ver = check_cmd(["git", "--version"])
    print(f"[{'OK' if ok else 'MISSING'}] Git: {ver or 'ไม่พบ git'}")
    if not ok:
        print("   -> แก้ไข (Windows): ดาวน์โหลดและติดตั้งจาก https://git-scm.com/download/win")
        fails += 1

    ok_name, name = check_cmd(["git", "config", "user.name"], cwd=REPO_ROOT)
    ok_mail, mail = check_cmd(["git", "config", "user.email"], cwd=REPO_ROOT)
    if ok_name and ok_mail and name and mail:
        print(f"[OK] Git identity: {name} <{mail}>")
    else:
        print("[MISSING] Git identity (user.name / user.email)")
        print('   -> เครื่องมหาลัย (แนะนำ): git config --local user.name "Your Name"; git config --local user.email "you@example.com"')
        print('   -> เครื่องส่วนตัว:        git config --global user.name "Your Name"; git config --global user.email "you@example.com"')
        fails += 1

    # 2. uv
    ok, ver = check_cmd(["uv", "--version"])
    print(f"[{'OK' if ok else 'MISSING'}] uv: {ver or 'ไม่พบ uv (จำเป็นสำหรับ uv sync และ uv run)'}")
    if not ok:
        print("   -> แก้ไข: ดูวิธีติดตั้งที่ https://docs.astral.sh/uv/getting-started/installation/")
        fails += 1

    # 3. pre-commit (Local .venv)
    pre_commit_exe = find_local_tool("pre-commit")
    ok, ver = check_cmd([pre_commit_exe, "--version"]) if pre_commit_exe else (False, "")
    print(f"[{'OK' if ok else 'MISSING'}] pre-commit (local): {ver or 'ยังไม่พบใน workshop/.venv'}")
    if not ok:
        print("   -> แก้ไข (รันใน workshop/): uv sync")
        fails += 1

    # 4. PlatformIO CLI (Local .venv หรือ fallback)
    pio_local = find_local_tool("pio")
    if pio_local:
        ok, ver = check_cmd([pio_local, "--version"])
        print(f"[OK] PlatformIO CLI (local): {ver} ({pio_local})")
    else:
        pio_fb = find_pio_fallback()
        if pio_fb:
            ok, ver = check_cmd([pio_fb, "--version"])
            print(f"[WARN] PlatformIO CLI: พบที่ {pio_fb} ({ver}) แต่ยังไม่พบใน workshop/.venv")
            print("   -> แก้ไข (รันใน workshop/): uv sync")
            warns += 1
        else:
            print("[MISSING] PlatformIO CLI (pio)")
            print("   -> แก้ไข (รันใน workshop/): uv sync")
            fails += 1

    # 5. esptool (Local .venv ใช้ใน Lab 06)
    esptool_exe = find_esptool()
    if esptool_exe:
        ok, ver = check_cmd([esptool_exe, "version"])
        print(f"[OK] esptool (local): {ver or 'พร้อมใช้งาน'} ({esptool_exe})")
    else:
        print("[WARN] esptool: ยังไม่พบใน workshop/.venv (ต้องใช้ใน Lab 06)")
        print("   -> แก้ไข (รันใน workshop/): uv sync")
        warns += 1

    # 6. gcc / g++ สำหรับ pio test -e native ใน Lab 04
    gcc = shutil.which("g++") or shutil.which("gcc")
    if gcc:
        ok, ver = check_cmd([gcc, "--version"])
        print(f"[OK] C/C++ Compiler (สำหรับ pio test -e native): {ver}")
    else:
        print("[WARN] ไม่พบ gcc/g++ ใน PATH (ต้องใช้รัน `uv run pio test -e native -v` ใน Lab 04)")
        print('   -> แก้ไขใน PowerShell (MSYS2): $env:Path = "C:\\msys64\\ucrt64\\bin;$env:Path"  (แล้วเช็ก `g++ --version`)')
        warns += 1

    print("\n" + "=" * 54)
    if fails == 0 and warns == 0:
        print("พร้อมเข้าเรียน Workshop ครบ 100% แล้ว!")
        return 0
    if fails == 0:
        print(f"พร้อมบางส่วน (พบ {warns} คำเตือน [WARN] — อ่านรายละเอียดด้านบนก่อนเริ่ม Lab 04 / Lab 06)")
        return 0
    print(f"พบ {fails} รายการที่ต้องติดตั้งก่อนเริ่มเรียน (และ {warns} คำเตือน)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
