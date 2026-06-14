"""
export_docx.py — Convertit 06_report.md en document Word (.docx) professionnel.
"""

import os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE_DIR = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
IN_MD    = os.path.join(BASE_DIR, "06_report.md")
OUT_DOCX = os.path.join(BASE_DIR, "06_report.docx")

# ── Couleurs ───────────────────────────────────────────────────────────────────
BLUE  = RGBColor(0x1A, 0x73, 0xE8)
GREEN = RGBColor(0x34, 0xA8, 0x53)
DARK  = RGBColor(0x20, 0x21, 0x24)
GRAY  = RGBColor(0x5F, 0x63, 0x68)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

def hex_to_rgb_str(hex_color):
    h = hex_color.lstrip('#')
    return h.upper()

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color.lstrip('#').upper())
    tcPr.append(shd)

def add_run_formatted(para, text):
    """Ajoute du texte avec **bold**, *italic*, `code` inline."""
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = para.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('*') and part.endswith('*'):
            run = para.add_run(part[1:-1])
            run.italic = True
        elif part.startswith('`') and part.endswith('`'):
            run = para.add_run(part[1:-1])
            run.font.name = 'Courier New'
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0xC6, 0x28, 0x28)
        elif part:
            para.add_run(part)

# ── Document ───────────────────────────────────────────────────────────────────
doc = Document()

# Marges
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── Page de garde ──────────────────────────────────────────────────────────────
# Titre principal
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("CYCLISTIC BIKE-SHARE")
run.font.size  = Pt(28)
run.font.bold  = True
run.font.color.rgb = BLUE

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
run2 = p2.add_run("Case Study — Analyse des données 2019–2020")
run2.font.size  = Pt(14)
run2.font.color.rgb = GRAY

doc.add_paragraph()

# KPI table
kpis = [
    ("3 885 439", "Trajets analysés"),
    ("64,6%",     "Membres"),
    ("35,4%",     "Casual riders"),
    ("37,1 min",  "Durée moy. Casual"),
    ("14,6 min",  "Durée moy. Membre"),
]
kpi_tbl = doc.add_table(rows=2, cols=5)
kpi_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for col_idx, (val, lbl) in enumerate(kpis):
    cell_val = kpi_tbl.cell(0, col_idx)
    cell_lbl = kpi_tbl.cell(1, col_idx)
    set_cell_bg(cell_val, "#E8F0FE")
    set_cell_bg(cell_lbl, "#E8F0FE")
    pv = cell_val.paragraphs[0]
    pv.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rv = pv.add_run(val)
    rv.font.bold  = True
    rv.font.size  = Pt(14)
    rv.font.color.rgb = BLUE
    pl = cell_lbl.paragraphs[0]
    pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rl = pl.add_run(lbl)
    rl.font.size  = Pt(8)
    rl.font.color.rgb = GRAY

doc.add_paragraph()

# Infos
info_tbl = doc.add_table(rows=5, cols=2)
infos = [
    ("Question Business", "Comment les membres et casual riders utilisent-ils les vélos différemment ?"),
    ("Analyste",          "Junior Data Analyst — Cyclistic Marketing Analytics Team"),
    ("Date",              "Juin 2026"),
    ("Données",           "3 885 439 trajets | Janvier 2019 – Décembre 2020"),
    ("Outils",            "Python · SQL · Matplotlib · Seaborn · Plotly · Tableau"),
]
for i, (lbl, val) in enumerate(infos):
    c0, c1 = info_tbl.cell(i, 0), info_tbl.cell(i, 1)
    p0 = c0.paragraphs[0]
    r0 = p0.add_run(lbl)
    r0.bold = True
    r0.font.color.rgb = BLUE
    r0.font.size = Pt(10)
    p1 = c1.paragraphs[0]
    r1 = p1.add_run(val)
    r1.font.size = Pt(10)

doc.add_page_break()

# ── Contenu du rapport ─────────────────────────────────────────────────────────
with open(IN_MD, encoding='utf-8') as f:
    lines = f.readlines()

in_table   = False
table_rows = []
in_code    = False
code_lines = []

for line in lines:
    line = line.rstrip('\n')

    # Code block
    if line.startswith('```'):
        if not in_code:
            in_code = True
            code_lines = []
        else:
            in_code = False
            p = doc.add_paragraph()
            for cl in code_lines:
                run = p.add_run(cl + '\n')
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0xC6, 0x28, 0x28)
            p.paragraph_format.left_indent = Cm(1)
        continue
    if in_code:
        code_lines.append(line)
        continue

    # Table
    if '|' in line and line.strip().startswith('|'):
        if not in_table:
            in_table = True
            table_rows = []
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not all(set(c) <= set('-: ') for c in cells):
            table_rows.append(cells)
        continue
    elif in_table:
        in_table = False
        if table_rows:
            ncols = max(len(r) for r in table_rows)
            tbl = doc.add_table(rows=len(table_rows), cols=ncols)
            tbl.style = 'Table Grid'
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            for ri, row in enumerate(table_rows):
                for ci, cell_text in enumerate(row):
                    if ci >= ncols: break
                    cell = tbl.cell(ri, ci)
                    p = cell.paragraphs[0]
                    if ri == 0:
                        set_cell_bg(cell, "#1A73E8")
                        r = p.add_run(cell_text)
                        r.bold = True
                        r.font.color.rgb = WHITE
                        r.font.size = Pt(9)
                    else:
                        if ri % 2 == 0:
                            set_cell_bg(cell, "#F1F3F4")
                        r = p.add_run(cell_text)
                        r.font.size = Pt(9)
            doc.add_paragraph()

    # Titres
    if line.startswith('# ') and not line.startswith('## '):
        h = doc.add_heading(line[2:], level=1)
        h.runs[0].font.color.rgb = BLUE
        h.runs[0].font.size = Pt(16)
    elif line.startswith('## '):
        h = doc.add_heading(line[3:], level=2)
        h.runs[0].font.color.rgb = DARK
        h.runs[0].font.size = Pt(13)
    elif line.startswith('### '):
        h = doc.add_heading(line[4:], level=3)
        h.runs[0].font.color.rgb = GRAY
        h.runs[0].font.size = Pt(11)
    elif line.startswith('> '):
        p = doc.add_paragraph(style='Quote')
        add_run_formatted(p, line[2:])
        p.runs[0].font.italic = True if p.runs else False
    elif line.startswith('- ') or line.startswith('* '):
        p = doc.add_paragraph(style='List Bullet')
        add_run_formatted(p, line[2:])
        p.paragraph_format.left_indent = Cm(0.5)
    elif re.match(r'^\d+\. ', line):
        num, rest = line.split('. ', 1)
        p = doc.add_paragraph(style='List Number')
        add_run_formatted(p, rest)
    elif line.strip() in ('---', '***', '___'):
        doc.add_paragraph('─' * 60)
    elif line.strip() == '':
        doc.add_paragraph()
    else:
        p = doc.add_paragraph()
        add_run_formatted(p, line)
        p.paragraph_format.space_after = Pt(4)

doc.save(OUT_DOCX)
print(f"DOCX genere : {OUT_DOCX}")
print(f"Taille : {os.path.getsize(OUT_DOCX)//1024} KB")
