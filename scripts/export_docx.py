"""
export_docx.py — Rapport professionnel complet Cyclistic (.docx)
Structure : Page de garde → Résumé Exécutif → Table des matières
          → Sections 1–6 → Annexes A & B
"""

import os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE_DIR = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
FIG_DIR  = os.path.join(BASE_DIR, "figures")
SQL_FILE = os.path.join(BASE_DIR, "scripts", "03_queries.sql")
OUT_DOCX = os.path.join(BASE_DIR, "06_report.docx")

# ── Palette ────────────────────────────────────────────────────────────────────
BLUE   = RGBColor(0x1A, 0x73, 0xE8)
GREEN  = RGBColor(0x34, 0xA8, 0x53)
AMBER  = RGBColor(0xB0, 0x60, 0x00)
DARK   = RGBColor(0x20, 0x21, 0x24)
GRAY   = RGBColor(0x5F, 0x63, 0x68)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)

# ── Helpers XML ────────────────────────────────────────────────────────────────
def set_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color.lstrip('#').upper())
    tcPr.append(shd)

def page_number_field(paragraph):
    run = paragraph.add_run()
    for tag, text in [('w:fldChar', None), ('w:instrText', 'PAGE'), ('w:fldChar', None)]:
        el = OxmlElement(tag)
        if tag == 'w:instrText':
            el.set(qn('xml:space'), 'preserve')
            el.text = text
            run._r.append(el)
        elif text is None and tag == 'w:fldChar':
            ftype = 'begin' if not hasattr(page_number_field, '_begun') else 'end'
            page_number_field._begun = True
            el.set(qn('w:fldCharType'), ftype)
            run._r.append(el)
    # reset flag
    if hasattr(page_number_field, '_begun'):
        del page_number_field._begun

def add_page_num(para):
    """Ajoute le champ PAGE dans un paragraphe."""
    run = para.add_run()
    for ftype in ('begin',):
        fc = OxmlElement('w:fldChar')
        fc.set(qn('w:fldCharType'), ftype)
        run._r.append(fc)
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = ' PAGE '
    run._r.append(instr)
    fc2 = OxmlElement('w:fldChar')
    fc2.set(qn('w:fldCharType'), 'end')
    run._r.append(fc2)
    run.font.size = Pt(8)
    run.font.color.rgb = GRAY

def bottom_border(para, color='1A73E8'):
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single')
    bot.set(qn('w:sz'), '6')
    bot.set(qn('w:space'), '4')
    bot.set(qn('w:color'), color)
    pBdr.append(bot)
    pPr.append(pBdr)

# ── Builders ───────────────────────────────────────────────────────────────────
def body(doc, text, size=10, space_after=6, color=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.color.rgb = color or DARK
    p.paragraph_format.space_after = Pt(space_after)
    return p

def bullet(doc, text, size=10):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    r.font.size = Pt(size)

def h1(doc, num, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(4)
    r1 = p.add_run(f"{num}  ")
    r1.font.size = Pt(16); r1.font.bold = True; r1.font.color.rgb = BLUE
    r2 = p.add_run(title)
    r2.font.size = Pt(16); r2.font.bold = True; r2.font.color.rgb = DARK
    bottom_border(p)

def h2(doc, label, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)
    r = p.add_run(f"{label}  {title}")
    r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = DARK

def figure(doc, fname, caption, width=14.0):
    path = os.path.join(FIG_DIR, fname)
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Cm(width))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cp.add_run(caption)
    r.font.size = Pt(8.5); r.font.italic = True; r.font.color.rgb = GRAY
    cp.paragraph_format.space_after = Pt(10)

def table(doc, headers, rows, widths=None):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ci, h in enumerate(headers):
        cell = tbl.rows[0].cells[ci]
        set_bg(cell, '#1A73E8')
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.bold = True; r.font.color.rgb = WHITE; r.font.size = Pt(9)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.rows[ri + 1].cells[ci]
            if ri % 2 == 0:
                set_bg(cell, '#F8F9FA')
            r = cell.paragraphs[0].add_run(str(val))
            r.font.size = Pt(9)
    if widths:
        for row_obj in tbl.rows:
            for ci, cell in enumerate(row_obj.cells):
                if ci < len(widths):
                    cell.width = Cm(widths[ci])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def colored_box(doc, header_text, header_color_hex, items, item_color):
    """Box colorée avec titre + liste de (label, texte)."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.cell(0, 0)
    set_bg(cell, header_color_hex)
    p = cell.paragraphs[0]
    r = p.add_run(header_text)
    r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = item_color
    for lbl, val in items:
        pi = cell.add_paragraph()
        pi.paragraph_format.left_indent = Cm(0.4)
        pi.paragraph_format.space_after = Pt(3)
        if lbl:
            rl = pi.add_run(f"{lbl} : "); rl.font.bold = True
            rl.font.size = Pt(10); rl.font.color.rgb = DARK
        rv = pi.add_run(val); rv.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════
doc = Document()

for section in doc.sections:
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)
    # Footer : nom projet à gauche, page à droite
    fp = section.footer.paragraphs[0]
    fp.clear()
    r_left = fp.add_run("Cyclistic Bike-Share — Case Study  |  Google Data Analytics Certificate")
    r_left.font.size = Pt(8); r_left.font.color.rgb = GRAY
    fp.add_run("   ")
    add_page_num(fp)
    fp.paragraph_format.tab_stops

# ══════════════════════════════════════════════════════════════════════════════
# PAGE DE GARDE
# ══════════════════════════════════════════════════════════════════════════════
# Bandeau bleu
band = doc.add_table(rows=1, cols=1)
band.alignment = WD_TABLE_ALIGNMENT.CENTER
bc = band.cell(0, 0)
set_bg(bc, '#1A73E8')
bp = bc.paragraphs[0]
bp.alignment = WD_ALIGN_PARAGRAPH.CENTER
br = bp.add_run("CYCLISTIC BIKE-SHARE")
br.font.size = Pt(26); br.font.bold = True; br.font.color.rgb = WHITE
bs = bc.add_paragraph()
bs.alignment = WD_ALIGN_PARAGRAPH.CENTER
bsr = bs.add_run("Rapport d'Analyse  ·  Case Study Google Data Analytics")
bsr.font.size = Pt(11); bsr.font.color.rgb = RGBColor(0xC5, 0xD9, 0xFD)
doc.add_paragraph()

# Question business
qp = doc.add_paragraph()
qp.alignment = WD_ALIGN_PARAGRAPH.CENTER
qr = qp.add_run(
    "« Comment les membres annuels et les casual riders\n"
    "utilisent-ils les vélos Cyclistic différemment ? »"
)
qr.font.size = Pt(13); qr.font.italic = True; qr.font.color.rgb = DARK
doc.add_paragraph()

# KPIs
kpis = [
    ("3 885 439", "Trajets analysés"),
    ("64,6 %",    "Part Members"),
    ("35,4 %",    "Part Casual"),
    ("14,6 min",  "Durée moy. Member"),
    ("37,1 min",  "Durée moy. Casual"),
]
kt = doc.add_table(rows=2, cols=5)
kt.alignment = WD_TABLE_ALIGNMENT.CENTER
for ci, (val, lbl) in enumerate(kpis):
    bg = '#D2E3FC' if ci % 2 else '#E8F0FE'
    set_bg(kt.cell(0, ci), bg); set_bg(kt.cell(1, ci), bg)
    pv = kt.cell(0, ci).paragraphs[0]
    pv.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rv = pv.add_run(val)
    rv.font.bold = True; rv.font.size = Pt(15); rv.font.color.rgb = BLUE
    pl = kt.cell(1, ci).paragraphs[0]
    pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rl = pl.add_run(lbl)
    rl.font.size = Pt(8); rl.font.color.rgb = GRAY
doc.add_paragraph()

# Infos
infos = [
    ("Analyste",         "Junior Data Analyst — Cyclistic Marketing Analytics Team"),
    ("Destinataire",     "Lily Moreno, Director of Marketing  |  Cyclistic Executive Team"),
    ("Date",             "Juin 2026"),
    ("Période couverte", "Janvier 2019 – Décembre 2020"),
    ("Outils",           "Python · pandas · matplotlib · seaborn · Plotly · SQL · Tableau"),
    ("Certification",    "Google Data Analytics Professional Certificate — Capstone Case Study 1"),
]
it = doc.add_table(rows=len(infos), cols=2)
it.alignment = WD_TABLE_ALIGNMENT.CENTER
for ri, (lbl, val) in enumerate(infos):
    c0, c1 = it.cell(ri, 0), it.cell(ri, 1)
    if ri % 2 == 0:
        set_bg(c0, '#F8F9FA'); set_bg(c1, '#F8F9FA')
    c0.width = Cm(4)
    r0 = c0.paragraphs[0].add_run(lbl)
    r0.bold = True; r0.font.color.rgb = BLUE; r0.font.size = Pt(9)
    r1 = c1.paragraphs[0].add_run(val)
    r1.font.size = Pt(9)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ EXÉCUTIF
# ══════════════════════════════════════════════════════════════════════════════
ep = doc.add_paragraph()
ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
er = ep.add_run("RÉSUMÉ EXÉCUTIF")
er.font.size = Pt(16); er.font.bold = True; er.font.color.rgb = BLUE
bottom_border(ep, '1A73E8')
doc.add_paragraph()

body(doc,
    "Cyclistic, programme de bike-share de Chicago, compte deux profils d'utilisateurs aux "
    "comportements opposés : les membres annuels (64,6 % des trajets) utilisent le service de "
    "façon utilitaire pour leurs déplacements domicile-travail, tandis que les casual riders "
    "(35,4 %) ont un usage récréatif et saisonnier. L'enjeu stratégique est de convertir une "
    "partie des 1,37 million de casual riders en membres annuels, jugés plus rentables.",
    space_after=10)

# Box constats
colored_box(doc, "  CONSTATS CLÉS", '#E8F0FE', [
    (None, "Les casual riders roulent 2,5× plus longtemps (37,1 min vs 14,6 min) "
           "mais 2× moins souvent → usage loisir, non utilitaire."),
    (None, "Double pic horaire membres à 8h et 17h (rush hours) vs pic unique casual à 15–17h "
           "→ comportements structurellement différents."),
    (None, "51,5 % des trajets casual se concentrent en été (juin–août) "
           "→ fenêtre de conversion estivale prioritaire."),
    (None, "Les casual se concentrent sur des stations touristiques (Lakefront, Navy Pier, "
           "Millennium Park) → ciblage géographique précis possible."),
], BLUE)

colored_box(doc, "  TOP 3 RECOMMANDATIONS", '#E6F4EA', [
    ("1", "Campagne géolocalisée « Week-end → Abonnement » autour des stations touristiques "
          "(Instagram/TikTok, vendredi soir–samedi matin)."),
    ("2", "Offre « Été → Membre » : 2 mois offerts en mai–juin pour les casual ayant effectué "
          "3+ trajets en 30 jours — email personnalisé avec calcul d'économies."),
    ("3", "Calculateur d'économies « domicile-travail » intégré dans l'app et le site : "
          "démontrer la rentabilité de l'abonnement pour les navetteurs potentiels."),
], GREEN)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# TABLE DES MATIÈRES
# ══════════════════════════════════════════════════════════════════════════════
tp = doc.add_paragraph()
tr2 = tp.add_run("TABLE DES MATIÈRES")
tr2.font.size = Pt(14); tr2.font.bold = True; tr2.font.color.rgb = BLUE
bottom_border(tp, '1A73E8')
doc.add_paragraph()

toc_entries = [
    ("1.", "Contexte & Problématique Business",          False),
    ("2.", "Sources de données & Méthodologie",           False),
    ("3.", "Nettoyage des données",                       False),
    ("4.", "Analyse & Insights",                          False),
    ("   4.1", "Vue d'ensemble : volume et durée",        True),
    ("   4.2", "Comportement temporel",                   True),
    ("   4.3", "Types de vélos",                          True),
    ("   4.4", "Stations de départ — Casual riders",      True),
    ("5.", "Recommandations Marketing",                   False),
    ("6.", "Conclusion & Limites",                        False),
    ("A.", "Annexe — Requêtes SQL",                       False),
    ("B.", "Annexe — Sources de données & Licence",       False),
]
for num, title, sub in toc_entries:
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_after = Pt(2)
    p_toc.paragraph_format.left_indent = Cm(0.5) if sub else Cm(0)
    r_n = p_toc.add_run(f"{num}  ")
    r_n.font.bold = not sub; r_n.font.size = Pt(10)
    r_n.font.color.rgb = GRAY if sub else BLUE
    r_t = p_toc.add_run(title)
    r_t.font.size = Pt(10)
    r_t.font.color.rgb = GRAY if sub else DARK

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CONTEXTE & PROBLÉMATIQUE BUSINESS
# ══════════════════════════════════════════════════════════════════════════════
h1(doc, "1.", "Contexte & Problématique Business")

body(doc,
    "Cyclistic est un programme de bike-share basé à Chicago comptant plus de 5 800 vélos "
    "géolocalisés répartis sur 692 stations à travers la ville. Lancé en 2016, le service "
    "propose une flexibilité tarifaire — pass journée, pass trajet unique ou abonnement annuel "
    "— qui a permis d'attirer un large public d'utilisateurs aux profils variés.")

body(doc,
    "Les analystes financiers de Cyclistic ont établi que les membres annuels génèrent une "
    "rentabilité significativement supérieure à celle des casual riders. La Director of Marketing "
    "Lily Moreno a identifié une opportunité stratégique : plutôt que de cibler exclusivement "
    "de nouveaux clients, maximiser la conversion des casual riders existants en membres annuels.")

h2(doc, "1.1", "Question d'analyse principale")
qt = doc.add_table(rows=1, cols=1)
qt.alignment = WD_TABLE_ALIGNMENT.CENTER
qc = qt.cell(0, 0)
set_bg(qc, '#F8F9FA')
qcp = qc.paragraphs[0]
qcp.alignment = WD_ALIGN_PARAGRAPH.CENTER
qcr = qcp.add_run(
    "« Comment les membres annuels et les casual riders utilisent-ils "
    "les vélos Cyclistic différemment ? »"
)
qcr.font.size = Pt(12); qcr.font.italic = True; qcr.font.color.rgb = BLUE
doc.add_paragraph()

h2(doc, "1.2", "Parties prenantes")
table(doc,
    ["Partie prenante", "Rôle", "Attente"],
    [
        ["Lily Moreno", "Director of Marketing — commanditaire", "Recommandations actionnables"],
        ["Cyclistic Executive Team", "Décisionnaires finaux", "Validation data + visualisations"],
        ["Marketing Analytics Team", "Implémentation", "Données exploitables pour les campagnes"],
    ],
    widths=[4.5, 6, 5.5]
)
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — SOURCES DE DONNÉES & MÉTHODOLOGIE
# ══════════════════════════════════════════════════════════════════════════════
h1(doc, "2.", "Sources de données & Méthodologie")

h2(doc, "2.1", "Fichiers utilisés")
table(doc,
    ["Fichier", "Période", "Lignes brutes"],
    [
        ["Divvy_Trips_2019_Q1.csv", "Janv.–Mars 2019", "365 069"],
        ["Divvy_Trips_2020_Q1.csv", "Janv.–Mars 2020", "426 887"],
        ["202004-divvy-tripdata.csv", "Avril 2020", "84 776"],
        ["202005-divvy-tripdata.csv", "Mai 2020", "200 274"],
        ["202006-divvy-tripdata.csv", "Juin 2020", "343 005"],
        ["202007-divvy-tripdata.csv", "Juillet 2020", "551 480"],
        ["202008-divvy-tripdata.csv", "Août 2020", "622 361"],
        ["202009-divvy-tripdata.csv", "Septembre 2020", "532 958"],
        ["202010-divvy-tripdata.csv", "Octobre 2020", "388 653"],
        ["202011-divvy-tripdata.csv", "Novembre 2020", "259 716"],
        ["202012-divvy-tripdata.csv", "Décembre 2020", "131 573"],
        ["TOTAL", "Jan 2019 – Déc 2020", "3 906 752"],
    ],
    widths=[7.5, 4, 4.5]
)

h2(doc, "2.2", "Crédibilité des données — critères ROCCC")
table(doc,
    ["Critère", "Évaluation", "Détail"],
    [
        ["Reliable ✅", "Données opérationnelles", "Collectées automatiquement par les capteurs"],
        ["Original ✅", "Source primaire", "Motivate International Inc. — opérateur réel"],
        ["Comprehensive ✅", "Couverture totale", "Tous les trajets sur la période, pas d'échantillonnage"],
        ["Current ⚠️", "Données historiques", "2019–2020 : suffisant pour tendances comportementales"],
        ["Cited ✅", "Licence publique", "Divvy Data License Agreement"],
    ],
    widths=[3, 4, 9]
)

h2(doc, "2.3", "Méthodologie — 6 phases Google Data Analytics")
phases = [
    ("Ask",     "Définir la question business et identifier les parties prenantes"),
    ("Prepare", "Collecter et documenter les 11 fichiers sources (data/01_data_description.md)"),
    ("Process", "Nettoyage, harmonisation et consolidation (scripts/02_cleaning.py)"),
    ("Analyze", "Analyse descriptive Python + 12 requêtes SQL (03_analysis.py, 03_queries.sql)"),
    ("Share",   "8 graphiques statiques (matplotlib/seaborn) + dashboard Plotly interactif"),
    ("Act",     "Top 3 recommandations + rapport complet + export Tableau"),
]
pt = doc.add_table(rows=len(phases), cols=2)
pt.style = 'Table Grid'
pt.alignment = WD_TABLE_ALIGNMENT.CENTER
for ri, (ph, desc) in enumerate(phases):
    c0, c1 = pt.cell(ri, 0), pt.cell(ri, 1)
    set_bg(c0, '#E8F0FE')
    c0.width = Cm(2.8)
    p0 = c0.paragraphs[0]; p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0 = p0.add_run(ph); r0.bold = True; r0.font.color.rgb = BLUE; r0.font.size = Pt(10)
    r1 = c1.paragraphs[0].add_run(desc); r1.font.size = Pt(9)
doc.add_paragraph()
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — NETTOYAGE DES DONNÉES
# ══════════════════════════════════════════════════════════════════════════════
h1(doc, "3.", "Nettoyage des données")

body(doc,
    "Le nettoyage a été réalisé intégralement en Python (pandas) via scripts/02_cleaning.py. "
    "Le log complet avec les comptages est disponible dans data/02_cleaning_log.md.")

h2(doc, "3.1", "Transformations appliquées")
table(doc,
    ["Étape", "Action", "Impact"],
    [
        ["Harmonisation schéma",   "Renommage colonnes 2019 Q1 + Subscriber→member / Customer→casual", "Unification des 11 fichiers"],
        ["Conversion datetime",    "started_at et ended_at → datetime64",                               "Calculs temporels"],
        ["ride_length",            "(ended_at − started_at) en minutes",                                 "Variable d'analyse principale"],
        ["Variables temporelles",  "day_of_week, month, year, season, hour_of_day",                     "5 nouvelles colonnes"],
        ["Doublons",               "Suppression sur ride_id",                                            "Dédoublonnage"],
        ["ride_length ≤ 0 min",    "Suppression (erreurs système)",                                      "Données invalides"],
        ["ride_length > 1 440 min","Suppression (vélos non retournés > 24h)",                            "Outliers extrêmes"],
        ["Stations maintenance",   "Suppression : HQ QR, TEST, DIVVY",                                  "Trajets internes exclus"],
        ["Résultat final",         "3 906 752 → 3 885 439 trajets propres",                             "−21 313 lignes (−0,5 %)"],
    ],
    widths=[4, 8, 4]
)

h2(doc, "3.2", "Contraintes & limites des données")
for lim in [
    "Confidentialité : pas d'identifiant personnel — impossible de relier les trajets à un individu.",
    "Données manquantes : 5–15 % de valeurs nulles sur les noms de stations (vélos electric/docked).",
    "Schéma hétérogène : le fichier 2019 Q1 utilise une structure différente des fichiers 2020.",
    "Impact COVID-19 : le creux d'avril 2020 reflète le confinement — comportement atypique.",
    "Données historiques : tendances solides mais une mise à jour 2022–2024 serait recommandée.",
]:
    bullet(doc, lim)
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ANALYSE & INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
h1(doc, "4.", "Analyse & Insights")

# 4.1 Vue d'ensemble
h2(doc, "4.1", "Vue d'ensemble : volume et durée des trajets")
body(doc,
    "Les membres représentent 64,6 % du volume de trajets mais effectuent des déplacements "
    "2,5 fois plus courts que les casual riders. Cette asymétrie (plus de trajets, plus courts "
    "pour les membres ; moins de trajets, bien plus longs pour les casual) révèle des usages "
    "fondamentalement distincts.")

table(doc,
    ["Métrique", "Members", "Casual riders", "Ratio"],
    [
        ["Nombre de trajets",  "2 508 757",   "1 376 682",   "Members × 1,8"],
        ["Part du total",      "64,6 %",      "35,4 %",      "—"],
        ["Durée moyenne",      "14,6 min",    "37,1 min",    "Casual × 2,5"],
        ["Durée médiane",      "10,6 min",    "21,7 min",    "Casual × 2,0"],
        ["Durée maximale",     "1 439,7 min", "1 439,9 min", "—"],
        ["Jour de pointe",     "Jeudi",       "Samedi",      "—"],
        ["Usage principal",    "Domicile ↔ Travail", "Loisirs / Tourisme", "—"],
    ],
    widths=[5, 3.5, 3.5, 4]
)

# fig1 + fig2 côte à côte
figt = doc.add_table(rows=1, cols=2)
figt.alignment = WD_TABLE_ALIGNMENT.CENTER
for ci, (fname, cap) in enumerate([
    ("01_rides_count.png",    "Fig. 1 — Nombre total de trajets"),
    ("02_avg_ride_length.png", "Fig. 2 — Durée moyenne (minutes)"),
]):
    cell = figt.cell(0, ci)
    path = os.path.join(FIG_DIR, fname)
    if os.path.exists(path):
        pp = cell.paragraphs[0]
        pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pp.add_run().add_picture(path, width=Cm(7.5))
    pc = cell.add_paragraph()
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rc = pc.add_run(cap)
    rc.font.size = Pt(8); rc.font.italic = True; rc.font.color.rgb = GRAY
doc.add_paragraph()

doc.add_page_break()

# 4.2 Comportement temporel
h2(doc, "4.2", "Comportement temporel")

body(doc,
    "L'analyse temporelle révèle la différence structurelle la plus significative : les membres "
    "ont un usage utilitaire rythmé par la semaine de travail, les casual riders un usage "
    "récréatif concentré sur le week-end et les heures de l'après-midi.")

body(doc, "Par jour de la semaine :", space_after=2)
bullet(doc, "Members : pic le jeudi (~391k trajets), volume stable lundi–vendredi → usage domicile-travail.")
bullet(doc, "Casual : pic le samedi (~318k trajets), profil en cloche autour du week-end → usage loisir.")
figure(doc, "03_rides_by_dow.png",
       "Fig. 3 — Trajets par jour de la semaine (membres vs casual)", width=14)

body(doc, "Par mois et saison :", space_after=2)
bullet(doc, "Pic estival commun (juin–août), bien plus prononcé chez les casual.")
bullet(doc, "Casual hyper-saisonniers : 51,5 % de leurs trajets en été vs 32 % pour les membres.")
bullet(doc, "En hiver : membres actifs (556k trajets) vs casual quasi-absents (57k).")
bullet(doc, "Creux d'avril 2020 visible pour les deux types (confinement COVID-19).")
figure(doc, "04_rides_by_month.png",
       "Fig. 4 — Évolution mensuelle des trajets (Janv. 2019 – Déc. 2020)", width=15)

doc.add_page_break()

body(doc, "Par heure de départ :", space_after=2)
bullet(doc, "Members : double pic à 8h et 17h → confirme les trajets domicile-travail.")
bullet(doc, "Casual : montée progressive dès 10h, pic unique à 15–17h → loisir, pas d'urgence horaire.")
figure(doc, "07_rides_by_hour.png",
       "Fig. 5 — Répartition des trajets par heure de départ", width=14)

body(doc, "Durée moyenne par jour de la semaine :", space_after=2)
body(doc,
    "Les casual riders maintiennent des trajets longs toute la semaine (>25 min même en semaine), "
    "ce qui exclut une explication liée uniquement au week-end. Il s'agit d'un comportement "
    "d'usage récréatif structurel, indépendant du jour.")
figure(doc, "08_avg_length_by_dow.png",
       "Fig. 6 — Durée moyenne des trajets par jour de la semaine", width=14)

doc.add_page_break()

# 4.3 Types de vélos
h2(doc, "4.3", "Types de vélos utilisés")
body(doc,
    "Les docked bikes dominent pour les deux types d'utilisateurs (>83 %). Les casual riders "
    "utilisent proportionnellement plus d'electric bikes (15,2 % vs 11,8 % pour les membres), "
    "ce qui peut indiquer une sensibilité à l'effort physique ou un usage sur de plus longues "
    "distances touristiques.")
figure(doc, "05_bike_types.png",
       "Fig. 7 — Types de vélos utilisés — % par catégorie d'utilisateur", width=14)

# 4.4 Stations
h2(doc, "4.4", "Stations de départ — Casual riders")
body(doc,
    "Les 10 stations les plus fréquentées par les casual riders sont toutes situées dans des "
    "zones touristiques et de loisirs de Chicago : bord du lac Michigan (Lakefront Trail), "
    "Navy Pier, Millennium Park, Shedd Aquarium. Cette concentration géographique représente "
    "une opportunité de ciblage marketing géolocalisé précis.")
figure(doc, "06_top10_stations.png",
       "Fig. 8 — Top 10 stations de départ — Casual riders (cibles prioritaires)", width=14)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — RECOMMANDATIONS MARKETING
# ══════════════════════════════════════════════════════════════════════════════
h1(doc, "5.", "Recommandations Marketing")

body(doc,
    "Les trois recommandations suivantes s'appuient directement sur les insights de l'analyse "
    "et sont ordonnées par priorité d'impact estimé et faisabilité d'implémentation.")

colored_box(doc, "  RECOMMANDATION 1 — Campagne « Week-end → Abonnement » géolocalisée",
    '#E8F0FE', [
    ("Insight",         "Les casual riders se concentrent le week-end sur des stations touristiques identifiables."),
    ("Action",          "Publicités géolocalisées dans un rayon de 500 m autour des 10 stations casual prioritaires, "
                        "le vendredi soir et samedi matin."),
    ("Message clé",     "« Tu roules déjà le week-end — économise avec l'abonnement annuel. »"),
    ("Canaux",          "Instagram/TikTok géolocalisés · notifications push in-app · affichage stations."),
    ("Impact attendu",  "Conversion des casual récurrents du week-end au moment de leur usage maximal."),
], BLUE)

colored_box(doc, "  RECOMMANDATION 2 — Offre « Été → Membre » à tarif préférentiel",
    '#E6F4EA', [
    ("Insight",         "51,5 % des trajets casual se concentrent en été → fenêtre de conversion optimale."),
    ("Action",          "En mai–juin : abonnement annuel avec 2 premiers mois offerts pour les casual ayant fait "
                        "3+ trajets en 30 jours. Email personnalisé avec calcul d'économies réalisées."),
    ("Message clé",     "« Tu as utilisé Cyclistic X fois ce mois-ci — tu aurais économisé Y€ avec un abonnement. »"),
    ("Canaux",          "Email ciblé · notification push in-app · bannières dans l'app."),
    ("Impact attendu",  "Conversion pendant le pic d'usage, avant l'inactivité automne/hiver."),
], GREEN)

colored_box(doc, "  RECOMMANDATION 3 — Calculateur d'économies « domicile-travail »",
    '#FEF7E0', [
    ("Insight",         "Les membres utilisent les vélos aux heures de rush (8h, 17h). "
                        "Les casual ignorent peut-être cet usage et donc la valeur de l'abonnement."),
    ("Action",          "Intégrer dans l'app et le site un calculateur interactif : "
                        "« Si tu fais X trajets/semaine, l'abonnement te coûte Y€/trajet vs Z€ en pass journée. »"),
    ("Canaux",          "Content marketing (blog, réseaux) · affichage stations aux heures de rush."),
    ("Impact attendu",  "Démonstration concrète de la valeur économique de l'abonnement pour les navetteurs potentiels."),
], AMBER)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — CONCLUSION & LIMITES
# ══════════════════════════════════════════════════════════════════════════════
h1(doc, "6.", "Conclusion & Limites")

h2(doc, "6.1", "Synthèse")
body(doc,
    "Cette analyse de 3 885 439 trajets (2019–2020) établit une distinction comportementale "
    "nette entre les deux types d'utilisateurs Cyclistic. Les membres ont un usage utilitaire "
    "et régulier (domicile-travail, semaine de travail, toute l'année), tandis que les casual "
    "riders ont un usage récréatif, saisonnier et géographiquement concentré autour des sites "
    "touristiques de Chicago.")

body(doc,
    "Cette dualité est une opportunité marketing : les casual riders les plus réguliers "
    "(récurrents le week-end, actifs en été, présents sur les stations touristiques) sont des "
    "candidats naturels à la conversion, à condition que la communication leur démontre la "
    "valeur de l'abonnement dans leur contexte d'usage réel.")

h2(doc, "6.2", "Limites & prochaines étapes")
for lim in [
    "Absence de données individuelles : impossible d'identifier les casual récurrents sans accès aux comptes utilisateurs.",
    "Période historique : une mise à jour avec les données 2022–2024 est recommandée avant déploiement des campagnes.",
    "Absence de données démographiques : âge, genre et localisation résidentielle permettraient un ciblage plus fin.",
    "Prochaine étape : A/B test sur un sous-groupe de casual riders (1 offre, 1 canal, 1 station pilote) avant déploiement.",
]:
    bullet(doc, lim)

doc.add_paragraph()
fp = doc.add_paragraph()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp.paragraph_format.space_before = Pt(14)
r_q = fp.add_run(
    "« Les données ne prennent de valeur que lorsqu'elles conduisent à des décisions. "
    "Ce rapport a été conçu pour être directement actionnable. »"
)
r_q.font.italic = True; r_q.font.size = Pt(10); r_q.font.color.rgb = GRAY
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# ANNEXE A — REQUÊTES SQL
# ══════════════════════════════════════════════════════════════════════════════
h1(doc, "A.", "Annexe — Requêtes SQL")
body(doc,
    "Les 12 requêtes SQL ci-dessous reproduisent en SQL standard l'analyse réalisée en Python "
    "et sont exécutables sur tout moteur compatible (PostgreSQL, BigQuery, SQLite, DuckDB). "
    "Table source : cyclistic_clean.")

with open(SQL_FILE, encoding='utf-8') as f:
    sql_raw = f.read()

for block in re.split(r'\n(?=-- ──)', sql_raw):
    block = block.strip()
    if not block:
        continue
    lines = block.split('\n')
    title_line = next((l for l in lines if '──' in l), None)
    if title_line:
        pt_sql = doc.add_paragraph()
        pt_sql.paragraph_format.space_before = Pt(8)
        rt_sql = pt_sql.add_run(title_line.replace('--', '').replace('─', '').strip())
        rt_sql.font.bold = True; rt_sql.font.size = Pt(9); rt_sql.font.color.rgb = BLUE
    pc = doc.add_paragraph()
    pc.paragraph_format.left_indent = Cm(0.5)
    pc.paragraph_format.space_after = Pt(4)
    rc = pc.add_run(block)
    rc.font.name = 'Courier New'; rc.font.size = Pt(7.5); rc.font.color.rgb = DARK

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# ANNEXE B — SOURCES & LICENCE
# ══════════════════════════════════════════════════════════════════════════════
h1(doc, "B.", "Annexe — Sources de données & Licence")

table(doc,
    ["Élément", "Détail"],
    [
        ["Source",    "Divvy Trip Data — Motivate International Inc."],
        ["Licence",   "Divvy Data License Agreement — usage public autorisé"],
        ["Période",   "Janvier 2019 – Décembre 2020 (11 fichiers CSV)"],
        ["Volume",    "3 906 752 trajets bruts → 3 885 439 après nettoyage"],
        ["Anonymat",  "Aucune PII — données 100 % anonymisées"],
        ["Note",      "Cyclistic est une entreprise fictive (Capstone Case Study 1, Google DA Certificate). "
                      "Les données Divvy sont réelles et adaptées à des fins pédagogiques."],
    ],
    widths=[3.5, 12.5]
)

body(doc, "Scripts & livrables :", space_after=3)
for item in [
    "scripts/02_cleaning.py     — Nettoyage & consolidation",
    "scripts/03_analysis.py     — Analyse descriptive Python",
    "scripts/03_queries.sql     — 12 requêtes SQL équivalentes",
    "scripts/04_visualizations.py — 8 graphiques PNG (matplotlib/seaborn)",
    "scripts/05_dashboard.py    — Dashboard interactif Plotly",
    "scripts/06_tableau_export.py — Export CSV pour Tableau",
    "05_dashboard.html          — Dashboard interactif (ouvrir dans un navigateur)",
]:
    p_item = doc.add_paragraph()
    p_item.paragraph_format.left_indent = Cm(0.5)
    p_item.paragraph_format.space_after = Pt(2)
    r_item = p_item.add_run(item)
    r_item.font.name = 'Courier New'; r_item.font.size = Pt(8.5)

# ══════════════════════════════════════════════════════════════════════════════
doc.save(OUT_DOCX)
size_kb = os.path.getsize(OUT_DOCX) // 1024
print(f"DOCX généré  : {OUT_DOCX}")
print(f"Taille       : {size_kb} KB")
