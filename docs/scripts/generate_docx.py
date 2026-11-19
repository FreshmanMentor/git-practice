#!/usr/bin/env python3
"""
Generate editable Microsoft Word (.docx) Lab Sheets (LAB00..LAB06) into exercises/labs/
matching LAB00..LAB06.pdf, using Sarabun (16pt bold headings, 14pt body, Sarabun entire doc),
1 blank line above every heading, 1 blank line above/below every image, and 1 item per line.
"""

import html
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_labs import DOCS_DIR, LABS, LABS_DIR  # noqa: E402

INLINE_TAG_RE = re.compile(r"(<strong>.*?</strong>|<em>.*?</em>)", re.DOTALL)
CODE_RE = re.compile(r"(<code>.*?</code>)", re.DOTALL)

FONT_THAI = "Sarabun"
FONT_MONO = "Sarabun"
HEADING_SIZE = 16.0
BODY_SIZE = 14.0


def set_run_font(run, font_name: str, size_pt: float, bold: bool = False, italic: bool = False, color=None) -> None:
    run.bold = bold
    run.italic = italic
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    if color is not None:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), font_name)


def _emit_code_aware(paragraph, fragment: str, base_size: float, color, bold: bool, italic: bool) -> None:
    for sub in CODE_RE.split(fragment):
        if not sub:
            continue
        if sub.startswith("<code>") and sub.endswith("</code>"):
            run = paragraph.add_run(html.unescape(sub[6:-7]))
            set_run_font(run, FONT_MONO, base_size, bold=bold, italic=italic, color=RGBColor(0x00, 0x00, 0x00))
        else:
            run = paragraph.add_run(html.unescape(sub))
            set_run_font(run, FONT_THAI, base_size, bold=bold, italic=italic, color=color)


def add_rich_runs(paragraph, html_text: str, base_size: float = BODY_SIZE, base_color=None) -> None:
    color = base_color or RGBColor(0x11, 0x18, 0x27)
    for part in INLINE_TAG_RE.split(html_text):
        if not part:
            continue
        if part.startswith("<strong>") and part.endswith("</strong>"):
            _emit_code_aware(paragraph, part[8:-9], base_size, color, bold=True, italic=False)
        elif part.startswith("<em>") and part.endswith("</em>"):
            _emit_code_aware(paragraph, part[4:-5], base_size, color, bold=False, italic=True)
        else:
            _emit_code_aware(paragraph, part, base_size, color, bold=False, italic=False)


def set_cell_shading(cell, fill_hex: str) -> None:
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_borders(cell, color: str = "475569", sz: str = "6") -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tcPr.append(borders)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_row_min_height(row, height_twips: int) -> None:
    trPr = row._tr.get_or_add_trPr()
    trHeight = OxmlElement("w:trHeight")
    trHeight.set(qn("w:val"), str(height_twips))
    trHeight.set(qn("w:hRule"), "atLeast")
    trPr.append(trHeight)


def add_section_heading(doc: Document, text: str) -> None:
    _ensure_blank_lines(doc, 1)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, FONT_THAI, HEADING_SIZE, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))


def _trailing_blank_paragraphs(doc: Document) -> int:
    count = 0
    for el in reversed(doc.element.body):
        if el.tag.endswith("}p"):
            text = "".join(el.itertext()).strip()
            if text or el.xpath(".//*[local-name()='drawing']"):
                break
            count += 1
        else:
            break
    return count


def _ensure_blank_lines(doc: Document, count: int = 1) -> None:
    missing = max(0, count - _trailing_blank_paragraphs(doc))
    for _ in range(missing):
        sp = doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(0)
        r = sp.add_run("")
        set_run_font(r, FONT_THAI, BODY_SIZE)


def add_code_box(doc: Document, code_text: str, dark: bool = False) -> None:
    """Insert generous blank spacing before and after every code block."""
    _ensure_blank_lines(doc, 1)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.9)
    set_cell_shading(cell, "0F172A" if dark else "F8FAD2")
    set_cell_borders(cell, color="334155" if dark else "475569", sz="6")
    set_cell_margins(cell, top=110, bottom=110, left=140, right=140)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.2
    run = p.add_run(code_text)
    set_run_font(
        run,
        FONT_MONO,
        BODY_SIZE,
        color=RGBColor(0xE2, 0xE8, 0xF0) if dark else RGBColor(0x0F, 0x17, 0x2A),
    )
    _ensure_blank_lines(doc, 1)


def add_picture_block(doc: Document, img_path: Path, caption: str, width_inches: float = 6.5) -> None:
    """Insert blank spacing before and after every screenshot."""
    _ensure_blank_lines(doc, 1)

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(0)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    p_img.add_run().add_picture(str(img_path), width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(2)
    rc = p_cap.add_run(caption)
    set_run_font(rc, FONT_THAI, BODY_SIZE, italic=True, color=RGBColor(0x33, 0x41, 0x55))

    _ensure_blank_lines(doc, 1)


def add_paste_box(doc: Document, placeholder: str, min_height_inches: float = 0.85) -> None:
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_row_min_height(tbl.rows[0], int(min_height_inches * 1440))
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.9)
    set_cell_shading(cell, "FFFFFF")
    set_cell_borders(cell, color="333333", sz="6")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(placeholder)
    set_run_font(run, FONT_THAI, 14.0, italic=True, color=RGBColor(0x55, 0x55, 0x55))
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(4)


def add_step_lines(doc: Document, steps: list[str]) -> None:
    for idx, step in enumerate(steps, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        add_rich_runs(p, f"{idx}. {step}", base_size=BODY_SIZE)


def build_docx(lab: dict) -> Path:
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = FONT_THAI
    normal.font.size = Pt(BODY_SIZE)
    nrPr = normal._element.get_or_add_rPr()
    nrFonts = nrPr.find(qn("w:rFonts"))
    if nrFonts is None:
        nrFonts = OxmlElement("w:rFonts")
        nrPr.insert(0, nrFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        nrFonts.set(qn(attr), FONT_THAI)

    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)

    # Header & Footer
    hdr = section.header.paragraphs[0]
    hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hdr.add_run("DOIT ESP32 DevKit v1 • PlatformIO Workshop | Git, Pre-commit, Testing & CI/CD")
    set_run_font(hrun, FONT_THAI, BODY_SIZE, color=RGBColor(0x47, 0x55, 0x69))

    ftr = section.footer.paragraphs[0]
    ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    frun = ftr.add_run(f"{lab['slug']} — Student Worksheet (.docx)")
    set_run_font(frun, FONT_THAI, BODY_SIZE, color=RGBColor(0x47, 0x55, 0x69))

    # Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(2)
    title_p.paragraph_format.space_after = Pt(10)
    trun = title_p.add_run(html.unescape(lab["title"]))
    trun.underline = True
    set_run_font(trun, FONT_THAI, HEADING_SIZE, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))

    # Student Info Table
    info_tbl = doc.add_table(rows=4, cols=2)
    info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_rows = [
        ("ชื่อ-นามสกุล (Student Name):", ""),
        ("รหัสนักศึกษา (Student ID):", ""),
        ("วันที่ปฏิบัติการ (Date):", ""),
        ("GitHub Repository URL:", "https://github.com/<your-username>/git-practice"),
    ]
    for idx, (label, default_val) in enumerate(info_rows):
        c0, c1 = info_tbl.rows[idx].cells
        c0.width = Inches(2.6)
        c1.width = Inches(4.3)
        set_cell_shading(c0, "FFFFFF")
        set_cell_shading(c1, "FFFFFF")
        set_cell_borders(c0, color="000000", sz="4")
        set_cell_borders(c1, color="000000", sz="4")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        set_run_font(r0, FONT_THAI, BODY_SIZE, bold=True, color=RGBColor(0x00, 0x00, 0x00))

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(default_val)
        set_run_font(
            r1,
            FONT_THAI,
            BODY_SIZE,
            color=RGBColor(0x44, 0x44, 0x44) if default_val else RGBColor(0x00, 0x00, 0x00),
        )

    # 1. Objectives
    add_section_heading(doc, "1. วัตถุประสงค์การเรียนรู้ (Objective)")
    add_step_lines(doc, lab["objectives"])

    # 2. Learning Outcomes
    add_section_heading(doc, "2. ผลลัพธ์การเรียนรู้ (Learning Outcomes)")
    add_step_lines(doc, lab["outcomes"])

    # 3. Tools
    add_section_heading(doc, "3. เครื่องมือและไฟล์ที่ต้องเตรียม (Tools & Prerequisites)")
    for tool in lab["tools"]:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        add_rich_runs(p, f"• {tool}", base_size=BODY_SIZE)

    # 4. Experiments
    add_section_heading(doc, "4. การทดลอง (Experiments)")
    for code, desc in lab["experiments"]:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f"{code}: ")
        r.underline = True
        set_run_font(r, FONT_THAI, BODY_SIZE, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))
        add_rich_runs(p, desc, base_size=BODY_SIZE)

    # 5. Step-by-Step Details
    add_section_heading(doc, "5. รายละเอียดการทดลองและขั้นตอนปฏิบัติ (Step-by-Step Guide & Code)")
    for item in lab["details"]:
        heading = item["heading"]
        steps = item.get("steps", [])
        desc = item.get("desc", "")
        code = item.get("code", "")
        imgs = item.get("images", [])

        _ensure_blank_lines(doc, 1)
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(html.unescape(heading))
        set_run_font(r, FONT_THAI, HEADING_SIZE, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))

        if steps:
            add_step_lines(doc, steps)
        elif desc:
            p_desc = doc.add_paragraph()
            p_desc.paragraph_format.left_indent = Inches(0.2)
            p_desc.paragraph_format.space_before = Pt(0)
            p_desc.paragraph_format.space_after = Pt(3)
            add_rich_runs(p_desc, desc, base_size=BODY_SIZE)
        if code:
            add_code_box(doc, code, dark=False)
        for rel_src, cap in imgs:
            img_path = (DOCS_DIR / "labs_html" / rel_src).resolve()
            if img_path.exists():
                add_picture_block(doc, img_path, cap, width_inches=6.5)

    # 6. Expected Output
    add_section_heading(doc, "6. ตัวอย่างผลลัพธ์ใน Terminal (Expected Output)")
    add_code_box(doc, lab["expected_output"], dark=True)

    # 7. Student Results & Screenshots
    add_section_heading(doc, "7. บันทึกผลการทดลองของนักเรียน (Results & Screenshots)")
    for res in lab["results"]:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        add_rich_runs(p, res, base_size=BODY_SIZE)
        add_paste_box(doc, "[วางผลลัพธ์ Terminal หรือข้อความคำตอบที่นี่]", min_height_inches=0.85)

    p_shot = doc.add_paragraph()
    p_shot.paragraph_format.space_after = Pt(3)
    p_shot.paragraph_format.keep_with_next = True
    r_shot = p_shot.add_run("ภาพหน้าจอหลักฐานการปฏิบัติการของนักเรียน (Student Screenshot):")
    set_run_font(r_shot, FONT_THAI, BODY_SIZE, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))
    add_paste_box(doc, "[วางภาพหน้าจอ / Paste Screenshot ผลลัพธ์ของนักเรียนที่นี่]", min_height_inches=1.6)

    # 8. Observation and Questions
    add_section_heading(doc, "8. การสังเกตและตอบคำถาม (Observation and Questions)")
    for q in lab["questions"]:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        add_rich_runs(p, q, base_size=BODY_SIZE)
        add_paste_box(doc, "[พิมพ์คำตอบของนักเรียนที่นี่]", min_height_inches=0.75)

    # 9. Exercise
    add_section_heading(doc, "9. แบบฝึกหัด (Exercise)")
    p_ex = doc.add_paragraph()
    p_ex.paragraph_format.space_after = Pt(3)
    r_ex = p_ex.add_run(f"{lab['exercise']['code']}:")
    r_ex.underline = True
    set_run_font(r_ex, FONT_THAI, BODY_SIZE, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))
    ex_steps = lab["exercise"].get("steps") or ([lab["exercise"]["desc"]] if lab["exercise"].get("desc") else [])
    add_step_lines(doc, ex_steps)
    add_code_box(doc, lab["exercise"]["snippet"], dark=False)
    add_paste_box(doc, "[วางผลลัพธ์ verify.py หรือภาพหน้าจอส่งงานที่นี่]", min_height_inches=0.9)

    # 10. Reference Screenshots
    add_section_heading(doc, "10. ภาพประกอบผลลัพธ์จริงสำหรับเทียบผล (Reference Screenshots)")
    for rel_src, cap in lab["screenshots"]:
        img_path = (DOCS_DIR / "labs_html" / rel_src).resolve()
        if img_path.exists():
            add_picture_block(doc, img_path, cap, width_inches=6.5)

    out_path = LABS_DIR / f"{lab['slug']}.docx"
    doc.save(out_path)
    print(f"Generated: exercises/labs/{out_path.name} ({out_path.stat().st_size} bytes)")
    return out_path


def main() -> None:
    for lab in LABS:
        build_docx(lab)


if __name__ == "__main__":
    main()
