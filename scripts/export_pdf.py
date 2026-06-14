"""
export_pdf.py — Convertit 06_report.md en PDF professionnel avec reportlab.
"""

import os, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

BASE_DIR = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
IN_MD    = os.path.join(BASE_DIR, "06_report.md")
OUT_PDF  = os.path.join(BASE_DIR, "06_report.pdf")

# ── Couleurs Cyclistic ─────────────────────────────────────────────────────────
BLUE     = HexColor("#1A73E8")
GREEN    = HexColor("#34A853")
DARK     = HexColor("#202124")
GRAY     = HexColor("#5F6368")
LGRAY    = HexColor("#F1F3F4")
LGRAY2   = HexColor("#E8EAED")

# ── Styles ─────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def style(name, **kw):
    s = ParagraphStyle(name, **kw)
    return s

S_TITLE  = style("Title2",  fontSize=24, textColor=white,       alignment=TA_LEFT,
                  fontName="Helvetica-Bold", leading=30)
S_SUBTITLE = style("Sub",   fontSize=11, textColor=HexColor("#BDC1C6"), alignment=TA_LEFT,
                    fontName="Helvetica", leading=16)
S_H1     = style("H1",      fontSize=16, textColor=BLUE,         spaceBefore=18,
                  spaceAfter=6,  fontName="Helvetica-Bold", leading=20)
S_H2     = style("H2",      fontSize=13, textColor=DARK,         spaceBefore=14,
                  spaceAfter=4,  fontName="Helvetica-Bold", leading=17)
S_H3     = style("H3",      fontSize=11, textColor=GRAY,         spaceBefore=10,
                  spaceAfter=3,  fontName="Helvetica-Bold", leading=15)
S_BODY   = style("Body2",   fontSize=10, textColor=DARK,         spaceBefore=3,
                  spaceAfter=3,  fontName="Helvetica",      leading=15)
S_BULLET = style("Bullet2", fontSize=10, textColor=DARK,         spaceBefore=2,
                  spaceAfter=2,  fontName="Helvetica",      leading=14,
                  leftIndent=16, bulletIndent=4)
S_CODE   = style("Code2",   fontSize=9,  textColor=HexColor("#C62828"), spaceBefore=2,
                  spaceAfter=2,  fontName="Courier",         leading=13,
                  leftIndent=12, backColor=LGRAY)
S_QUOTE  = style("Quote2",  fontSize=10, textColor=GRAY,         spaceBefore=4,
                  spaceAfter=4,  fontName="Helvetica-Oblique", leading=15,
                  leftIndent=20)
S_SMALL  = style("Small2",  fontSize=8,  textColor=GRAY,         alignment=TA_CENTER,
                  fontName="Helvetica", leading=10)

# ── Parser markdown simplifié ──────────────────────────────────────────────────
def parse_inline(text):
    """Convertit **bold**, *italic*, `code` en balises ReportLab."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`',       r'<font name="Courier" color="#C62828">\1</font>', text)
    # Echapper les & non XMLifiés
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;)', '&amp;', text)
    return text

def md_to_flowables(md_text):
    story = []
    lines = md_text.split('\n')
    i = 0
    table_rows = []
    in_table = False

    while i < len(lines):
        line = lines[i]

        # Table markdown
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if not all(set(c) <= set('-: ') for c in cells):
                table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            in_table = False
            if table_rows:
                story.append(Spacer(1, 6))
                col_w = (A4[0] - 4*cm) / max(len(r) for r in table_rows)
                col_widths = [col_w] * len(table_rows[0])
                data = []
                for ri, row in enumerate(table_rows):
                    cells_p = [Paragraph(parse_inline(c),
                                          style(f"TC{ri}",
                                                fontSize=9 if ri > 0 else 9,
                                                fontName="Helvetica-Bold" if ri == 0 else "Helvetica",
                                                textColor=white if ri == 0 else DARK,
                                                leading=12, spaceBefore=1, spaceAfter=1))
                               for c in row]
                    data.append(cells_p)
                t = Table(data, colWidths=col_widths, repeatRows=1)
                ts = TableStyle([
                    ('BACKGROUND',  (0,0), (-1,0),  BLUE),
                    ('BACKGROUND',  (0,1), (-1,-1), LGRAY),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, LGRAY]),
                    ('GRID',        (0,0), (-1,-1), 0.5, LGRAY2),
                    ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING',  (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING',(0,0),(-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                ])
                t.setStyle(ts)
                story.append(t)
                story.append(Spacer(1, 6))

        # Titres
        if line.startswith('# ') and not line.startswith('## '):
            story.append(Spacer(1, 8))
            story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
            story.append(Spacer(1, 4))
            story.append(Paragraph(parse_inline(line[2:]), S_H1))
        elif line.startswith('## '):
            story.append(Paragraph(parse_inline(line[3:]), S_H2))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LGRAY2))
        elif line.startswith('### '):
            story.append(Paragraph(parse_inline(line[4:]), S_H3))
        # Blockquote
        elif line.startswith('> '):
            story.append(Paragraph(parse_inline(line[2:]), S_QUOTE))
        # Bullet
        elif line.startswith('- ') or line.startswith('* '):
            story.append(Paragraph('• ' + parse_inline(line[2:]), S_BULLET))
        elif re.match(r'^\d+\. ', line):
            num, rest = line.split('. ', 1)
            story.append(Paragraph(f'{num}. ' + parse_inline(rest), S_BULLET))
        # Ligne vide
        elif line.strip() == '':
            story.append(Spacer(1, 4))
        # Séparateur ---
        elif line.strip() in ('---', '***', '___'):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LGRAY2))
            story.append(Spacer(1, 4))
        # Code block
        elif line.startswith('```'):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            story.append(Paragraph('<br/>'.join(code_lines), S_CODE))
        # Paragraphe normal
        elif line.strip():
            story.append(Paragraph(parse_inline(line), S_BODY))

        i += 1

    return story

# ── Génération du PDF ──────────────────────────────────────────────────────────
def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Header
    canvas.setFillColor(BLUE)
    canvas.rect(0, h-1.5*cm, w, 1.5*cm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(1*cm, h-1*cm, "Cyclistic Bike-Share — Case Study")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(w-1*cm, h-1*cm, "Google Data Analytics Certificate")
    # Footer
    canvas.setFillColor(LGRAY)
    canvas.rect(0, 0, w, 0.8*cm, fill=1, stroke=0)
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(w/2, 0.3*cm, f"Page {doc.page}")
    canvas.restoreState()

print("Lecture du rapport...")
with open(IN_MD, encoding='utf-8') as f:
    md_text = f.read()

# Page de garde
doc = SimpleDocTemplate(OUT_PDF, pagesize=A4,
                         leftMargin=2*cm, rightMargin=2*cm,
                         topMargin=2.5*cm, bottomMargin=1.5*cm)

story = []

# ── Cover page ─────────────────────────────────────────────────────────────────
from reportlab.platypus import KeepTogether

cover_data = [[Paragraph("", S_TITLE)]]
cover_bg = Table([[""]], colWidths=[A4[0]-2*cm], rowHeights=[5*cm])
cover_bg.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), BLUE),
    ('TOPPADDING', (0,0), (-1,-1), 30),
]))
story.append(cover_bg)
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("Cyclistic Bike-Share", style("CT",
    fontSize=28, fontName="Helvetica-Bold", textColor=BLUE, leading=34)))
story.append(Paragraph("Case Study — Analyse des données 2019–2020",
    style("CS", fontSize=14, fontName="Helvetica", textColor=GRAY, leading=18)))
story.append(Spacer(1, 0.5*cm))

info = [
    ["Question Business :", "Comment les membres et casual riders utilisent-ils les vélos différemment ?"],
    ["Analyste :",          "Junior Data Analyst — Cyclistic Marketing Team"],
    ["Date :",              "Juin 2026"],
    ["Données :",           "3 885 439 trajets | Jan 2019 – Déc 2020"],
    ["Outils :",            "Python · SQL · Matplotlib · Plotly · Tableau"],
]
info_table = Table(info, colWidths=[4*cm, 12*cm])
info_table.setStyle(TableStyle([
    ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',    (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE',    (0,0), (-1,-1), 10),
    ('TEXTCOLOR',   (0,0), (0,-1), BLUE),
    ('TEXTCOLOR',   (1,0), (1,-1), DARK),
    ('TOPPADDING',  (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ('LINEBELOW',   (0,-1), (-1,-1), 0.5, LGRAY2),
]))
story.append(info_table)
story.append(Spacer(1, 1*cm))

# KPI boxes
kpis = [
    ["3 885 439", "Trajets analysés"],
    ["64,6%",     "Membres"],
    ["35,4%",     "Casual riders"],
    ["37,1 min",  "Durée moy. Casual"],
    ["14,6 min",  "Durée moy. Membre"],
]
kpi_cells = []
for val, lbl in kpis:
    kpi_cells.append(
        Paragraph(f'<b><font color="#1A73E8" size="14">{val}</font></b><br/>'
                  f'<font color="#5F6368" size="8">{lbl}</font>',
                  style("KPI", alignment=TA_CENTER, leading=18))
    )
kpi_table = Table([kpi_cells], colWidths=[(A4[0]-4*cm)/5]*5)
kpi_table.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,-1), LGRAY),
    ('BOX',           (0,0), (-1,-1), 1, LGRAY2),
    ('INNERGRID',     (0,0), (-1,-1), 0.5, LGRAY2),
    ('TOPPADDING',    (0,0), (-1,-1), 10),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
]))
story.append(kpi_table)
story.append(PageBreak())

# ── Contenu du rapport ─────────────────────────────────────────────────────────
story += md_to_flowables(md_text)

# ── Build ──────────────────────────────────────────────────────────────────────
print("Generation du PDF...")
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"PDF genere : {OUT_PDF}")
size = os.path.getsize(OUT_PDF)/1024
print(f"Taille : {size:.0f} KB")
