"""
export_pdf.py — Rapport professionnel Cyclistic (.pdf) avec figures embarquées
Génère un PDF complet équivalent au rapport DOCX, via ReportLab.
"""

import os, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Enregistrement police Unicode (DejaVuSans) ────────────────────────────────
import matplotlib
_FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf')
pdfmetrics.registerFont(TTFont('DejaVu',        os.path.join(_FONT_DIR, 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVu-Bold',   os.path.join(_FONT_DIR, 'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('DejaVu-Italic', os.path.join(_FONT_DIR, 'DejaVuSans-Oblique.ttf')))
pdfmetrics.registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu-Bold', italic='DejaVu-Italic')

FONT_NORM = 'DejaVu'
FONT_BOLD = 'DejaVu-Bold'
FONT_ITAL = 'DejaVu-Italic'

BASE_DIR = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
FIG_DIR  = os.path.join(BASE_DIR, "figures")
SQL_FILE = os.path.join(BASE_DIR, "scripts", "03_queries.sql")
OUT_PDF  = os.path.join(BASE_DIR, "06_report.pdf")
BADGE    = os.path.join(FIG_DIR, "badge_google_da.png")
CREDLY   = "https://www.credly.com/go/RarXbDJG"

# ── Couleurs ──────────────────────────────────────────────────────────────────
C_BLUE   = colors.HexColor('#1A73E8')
C_GREEN  = colors.HexColor('#34A853')
C_AMBER  = colors.HexColor('#B06000')
C_DARK   = colors.HexColor('#202124')
C_GRAY   = colors.HexColor('#5F6368')
C_WHITE  = colors.white
C_LGRAY  = colors.HexColor('#F1F3F4')
C_BLUE_L = colors.HexColor('#E8F0FE')
C_GREEN_L= colors.HexColor('#E6F4EA')
C_AMB_L  = colors.HexColor('#FEF7E0')

W, H = A4
SS = getSampleStyleSheet()

def sty(name, parent='Normal', **kw):
    s = ParagraphStyle(name, parent=SS[parent])
    for k, v in kw.items():
        setattr(s, k, v)
    return s

S_BODY   = sty('body',   fontSize=10, leading=15, textColor=C_DARK, spaceAfter=6,  fontName='DejaVu')
S_BODY_J = sty('bodyj',  fontSize=10, leading=15, textColor=C_DARK, spaceAfter=6,  fontName='DejaVu', alignment=TA_JUSTIFY)
S_H1     = sty('h1',     fontSize=16, leading=20, textColor=C_BLUE, spaceBefore=12, spaceAfter=4, fontName='DejaVu-Bold')
S_H2     = sty('h2',     fontSize=12, leading=16, textColor=C_DARK, spaceBefore=8,  spaceAfter=4, fontName='DejaVu-Bold')
S_CAPTION= sty('cap',    fontSize=8,  leading=11, textColor=C_GRAY, spaceAfter=8,   alignment=TA_CENTER, fontName='DejaVu-Italic')
S_BULLET = sty('bul',    fontSize=10, leading=15, textColor=C_DARK, spaceAfter=3,   leftIndent=16, bulletIndent=4, fontName='DejaVu')
S_CODE   = sty('code',   fontSize=7.5,leading=10, textColor=C_DARK, fontName='Courier', spaceAfter=6, leftIndent=14, backColor=colors.HexColor('#F8F9FA'))
S_SMALL  = sty('small',  fontSize=8,  leading=11, textColor=C_GRAY, fontName='DejaVu')
S_CENTER = sty('center', fontSize=10, leading=15, textColor=C_DARK, alignment=TA_CENTER, fontName='DejaVu')

def clean(text):
    """Remplace les caractères Unicode non supportés par des équivalents ASCII/Latin."""
    if not isinstance(text, str):
        return text
    return (text
        .replace(' ', ' ')   # espace insécable → espace normale
        .replace(' ', ' ')   # espace fine insécable → espace normale
        .replace(' ', ' ')   # espace fine → espace normale
        .replace('’', "'")   # apostrophe typographique → apostrophe
        .replace('‘', "'")
        .replace('“', '"')   # guillemets typographiques
        .replace('”', '"')
        .replace('«', '<<')  # guillemets français
        .replace('»', '>>')
    )

def hr(color=C_BLUE, thickness=1.5):
    return HRFlowable(width='100%', thickness=thickness, color=color, spaceAfter=6, spaceBefore=2)

def sp(n=4):
    return Spacer(1, n)

def h1_flow(num, title):
    return [Paragraph(f'<b><font color="#1A73E8">{clean(num)}</font>  {clean(title)}</b>', S_H1), hr()]

def h2_flow(lbl, title):
    return [Paragraph(f'<b>{clean(lbl)}{"  " if lbl else ""}{clean(title)}</b>', S_H2)]

def body_p(text, justify=False):
    return Paragraph(clean(text), S_BODY_J if justify else S_BODY)

def bullet_p(text):
    return Paragraph(f'•  {clean(text)}', S_BULLET)

def figure_flow(fname, fig_num, caption, width=14*cm):
    path = os.path.join(FIG_DIR, fname)
    items = []
    if os.path.exists(path):
        img = Image(path, width=width, height=width * 0.62)
        img.hAlign = 'CENTER'
        items.append(img)
    items.append(Paragraph(f'Fig. {fig_num} — {caption}  ({fname})', S_CAPTION))
    items.append(sp(6))
    return items

def tbl_style(col_widths, data, hdr_bg=C_BLUE):
    data = [[clean(c) if isinstance(c, str) else c for c in row] for row in data]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), hdr_bg),
        ('TEXTCOLOR',  (0,0), (-1,0), C_WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'DejaVu-Bold'),
        ('FONTSIZE',   (0,0), (-1,0), 9),
        ('FONTSIZE',   (0,1), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#DADCE0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LGRAY]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

def colored_box_flow(header, bg_color, items, hdr_color):
    rows = [[Paragraph(f'<b><font color="{hdr_color.hexval()}">{header}</font></b>', S_BODY)]]
    for lbl, val in items:
        if lbl:
            rows.append([Paragraph(f'<b>{lbl} :</b> {val}', S_BODY)])
        else:
            rows.append([Paragraph(f'•  {val}', S_BULLET)])
    t = Table(rows, colWidths=[16.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 1, hdr_color),
    ]))
    return [t, sp(8)]

def insight_flow(text):
    t = Table([[Paragraph(
        f'<b><font color="#1A73E8">  Insight cle</font></b><br/><i>{text}</i>', S_BODY)
    ]], colWidths=[16.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BLUE_L),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, C_BLUE),
    ]))
    return [t, sp(10)]

# ── Footer / header ──────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    if doc.page == 1:
        canvas.restoreState()
        return
    canvas.setFont('DejaVu', 8)
    canvas.setFillColor(C_GRAY)
    canvas.drawString(cm*2.5, cm*1.2,
        'Cyclistic Bike-Share  |  Sidi Mohamed ALLY  |  Google Data Analytics Certificate')
    canvas.drawRightString(W - cm*2.5, cm*1.2, str(doc.page))
    canvas.setStrokeColor(colors.HexColor('#DADCE0'))
    canvas.setLineWidth(0.5)
    canvas.line(cm*2.5, cm*1.5, W-cm*2.5, cm*1.5)
    canvas.restoreState()

# ══════════════════════════════════════════════════════════════════════════════
doc = SimpleDocTemplate(
    OUT_PDF, pagesize=A4,
    topMargin=2*cm, bottomMargin=2.5*cm,
    leftMargin=2.5*cm, rightMargin=2.5*cm,
    title="Cyclistic Bike-Share — Rapport d'Analyse",
    author="Sidi Mohamed ALLY",
    subject="Google Data Analytics Certificate — Case Study 1",
)

story = []

# ─── PAGE DE GARDE ──────────────────────────────────────────────────────────
S_TITLE  = sty('title',  fontSize=26, leading=32, textColor=C_WHITE, fontName='DejaVu-Bold', alignment=TA_CENTER)
S_SUBT   = sty('subt',   fontSize=11, leading=16, textColor=colors.HexColor('#C5D9FD'), alignment=TA_CENTER)

band = Table([[Paragraph('CYCLISTIC BIKE-SHARE', S_TITLE)],
              [Paragraph("Rapport d'Analyse  ·  Case Study Google Data Analytics", S_SUBT)]],
             colWidths=[16.5*cm])
band.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), C_BLUE),
    ('TOPPADDING', (0,0), (-1,-1), 14),
    ('BOTTOMPADDING', (0,0), (-1,-1), 14),
]))
story += [band, sp(16)]
story += [
    Paragraph("Rapport d'Analyse — Case Study",
        sty('cov_big', fontSize=16, fontName='DejaVu-Bold', textColor=C_DARK, alignment=TA_CENTER)),
    sp(6),
    Paragraph(
        "« Comment les membres annuels et les casual riders<br/>"
        "utilisent-ils les vélos Cyclistic différemment ? »",
        sty('coverq', fontSize=12, leading=18, textColor=C_GRAY, fontName='DejaVu-Italic', alignment=TA_CENTER)),
    sp(16),
]

kpi = Table(
    [['3 885 439','64,6 %','35,4 %','14,6 min','37,1 min'],
     ['Trajets analysés','Part Members','Part Casual','Durée moy. Member','Durée moy. Casual']],
    colWidths=[3.3*cm]*5)
kpi.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),C_BLUE_L), ('BACKGROUND',(0,1),(-1,1),C_LGRAY),
    ('FONTNAME',(0,0),(-1,0),'DejaVu-Bold'), ('FONTSIZE',(0,0),(-1,0),13),
    ('TEXTCOLOR',(0,0),(-1,0),C_BLUE),
    ('FONTSIZE',(0,1),(-1,1),8), ('TEXTCOLOR',(0,1),(-1,1),C_GRAY),
    ('ALIGN',(0,0),(-1,-1),'CENTER'),
    ('TOPPADDING',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),8),
    ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#DADCE0')),
]))
story += [kpi, sp(16)]

info_data = [
    ['Analyste',        'Sidi Mohamed ALLY'],
    ['Titre',           'Analyste de données Professionnel Certifié'],
    ['Certification',   'Google Data Analytics Professional Certificate — Google / Coursera (13 juin 2026)'],
    ['Destinataire',    'Lily Moreno, Director of Marketing  |  Cyclistic Executive Team'],
    ['Date du rapport', 'Juin 2026'],
    ['Période',    'Janvier 2019 – Décembre 2020'],
    ['Outils',          'Python (pandas · matplotlib · seaborn · plotly)  ·  SQL  ·  Tableau'],
]
info_tbl = Table(info_data, colWidths=[3.8*cm, 12.7*cm])
info_tbl.setStyle(TableStyle([
    ('FONTNAME',(0,0),(0,-1),'DejaVu-Bold'), ('FONTSIZE',(0,0),(-1,-1),9),
    ('FONTSIZE',(0,0),(1,0),11), ('FONTNAME',(1,0),(1,0),'DejaVu-Bold'),
    ('TEXTCOLOR',(0,0),(0,-1),C_BLUE),
    ('ROWBACKGROUNDS',(0,0),(-1,-1),[C_LGRAY, colors.white]),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
    ('LEFTPADDING',(0,0),(-1,-1),8),
    ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#DADCE0')),
]))
story += [info_tbl, sp(14)]

if os.path.exists(BADGE):
    badge_img = Image(BADGE, width=3.2*cm, height=3.2*cm)
    badge_info = [
        Paragraph('<b>Google Data Analytics Professional Certificate</b>', S_BODY),
        Paragraph('Délivré le 13 juin 2026  ·  Émis par Google &amp; Coursera', S_SMALL),
        Paragraph(f'Vérifier le badge : <link href="{CREDLY}" color="#1A73E8"><u>{CREDLY}</u></link>', S_SMALL),
    ]
    bt = Table([[badge_img, badge_info]], colWidths=[4*cm, 12.5*cm])
    bt.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),4)]))
    story.append(bt)
story.append(PageBreak())

# ─── RÉSUMÉ EXÉCUTIF ─────────────────────────────────────────────────────────
story += [Paragraph('<b><font color="#1A73E8">RÉSUMÉ EXÉCUTIF</font></b>', S_H1), hr(), sp(4)]
story.append(body_p(
    "Cyclistic, programme de bike-share de Chicago, dispose de deux profils d'utilisateurs aux "
    "comportements opposés : les membres annuels (64,6 %) utilisent le service pour leurs "
    "déplacements domicile-travail, tandis que les casual riders (35,4 %) ont un usage récréatif "
    "et saisonnier. L'objectif stratégique est de convertir une partie des 1,37 million de casual "
    "riders en membres annuels, jugés plus rentables.", True))
story.append(sp(8))

story += colored_box_flow('CONSTATS CLÉS', C_BLUE_L, [
    (None, "Les casual riders roulent 2,5× plus longtemps (37,1 min vs 14,6 min) mais 2× moins souvent."),
    (None, "Double pic horaire membres à 8h et 17h (rush hours) vs pic unique casual à 15–17h."),
    (None, "51,5 % des trajets casual en été (juin–août) → fenêtre de conversion prioritaire."),
    (None, "Casual concentrés sur des stations touristiques (Lakefront, Navy Pier, Millennium Park)."),
], C_BLUE)
story += colored_box_flow('TOP 3 RECOMMANDATIONS', C_GREEN_L, [
    ("1", "Campagne géolocalisée « Week-end → Abonnement » autour des stations touristiques."),
    ("2", "Offre « Été → Membre » : 2 mois offerts en mai–juin aux casual ayant 3+ trajets en 30 jours."),
    ("3", "Calculateur d'économies « domicile-travail » dans l'app pour démontrer la valeur de l'abonnement."),
], C_GREEN)
story.append(PageBreak())

# ─── TABLE DES MATIÈRES ──────────────────────────────────────────────────────
story += [Paragraph('<b><font color="#1A73E8">TABLE DES MATIÈRES</font></b>', S_H1), hr(), sp(4)]
toc_entries = [
    ("1.", "Contexte &amp; Problématique Business", False),
    ("2.", "Sources de données &amp; Méthodologie", False),
    ("3.", "Nettoyage des données", False),
    ("4.", "Analyse &amp; Insights", False),
    ("   4.1", "Vue d'ensemble : volume et durée", True),
    ("   4.2", "Comportement temporel", True),
    ("   4.3", "Types de vélos", True),
    ("   4.4", "Stations de départ — Casual riders", True),
    ("5.", "Recommandations Marketing", False),
    ("6.", "Conclusion &amp; Limites", False),
    ("—", "Signature de l'auteur", False),
    ("—", "Glossaire", False),
    ("A.", "Annexe — Requêtes SQL", False),
    ("B.", "Annexe — Scripts Python clés", False),
    ("C.", "Annexe — Sources de données &amp; Licence", False),
]
for num, title, sub in toc_entries:
    color = '#5F6368' if sub else '#1A73E8'
    indent = 12 if sub else 0
    s = sty(f'toc{num}', fontSize=10, leading=15, textColor=C_DARK, spaceAfter=2, leftIndent=indent)
    story.append(Paragraph(f'<font color="{color}"><b>{num}</b></font>  {title}', s))

story += [sp(12), Paragraph('<b><font color="#1A73E8">LISTE DES FIGURES</font></b>',
    sty('lfh', fontSize=12, leading=16, fontName='DejaVu-Bold', textColor=C_BLUE, spaceAfter=4))]
story.append(hr(colors.HexColor('#E8EAED'), 0.8))
story.append(tbl_style([1.4*cm, 6.8*cm, 5.1*cm, 2*cm], [
    ['N°', 'Titre', 'Fichier', 'Section'],
    ['Fig. 1', 'Nombre total de trajets',               '01_rides_count.png',       '4.1'],
    ['Fig. 2', 'Durée moyenne des trajets',          '02_avg_ride_length.png',   '4.1'],
    ['Fig. 3', 'Trajets par jour de la semaine',        '03_rides_by_dow.png',      '4.2'],
    ['Fig. 4', 'Évolution mensuelle des trajets',   '04_rides_by_month.png',    '4.2'],
    ['Fig. 5', 'Trajets par heure de départ',       '07_rides_by_hour.png',     '4.2'],
    ['Fig. 6', 'Durée moyenne par jour de la sem.', '08_avg_length_by_dow.png', '4.2'],
    ['Fig. 7', 'Types de vélos utilisés',       '05_bike_types.png',        '4.3'],
    ['Fig. 8', 'Top 10 stations — Casual riders',   '06_top10_stations.png',    '4.4'],
]))
story.append(PageBreak())

# ─── SECTION 1 ───────────────────────────────────────────────────────────────
story += h1_flow("1.", "Contexte &amp; Problématique Business")
story.append(body_p(
    "Cyclistic est un programme de bike-share basé à Chicago comptant plus de 5 800 vélos "
    "géolocalisés répartis sur 692 stations. Les analystes financiers ont établi que les membres "
    "annuels génèrent une rentabilité significativement supérieure. L'objectif stratégique : "
    "maximiser la conversion des casual riders existants.", True))
story += h2_flow("1.2", "Parties prenantes")
story.append(tbl_style([4*cm, 6*cm, 6.5*cm], [
    ['Partie prenante', 'Rôle', 'Attente'],
    ['Lily Moreno', 'Director of Marketing', 'Recommandations actionnables'],
    ['Executive Team', 'Décisionnaires', 'Validées par visualisations'],
    ['Analytics Team', 'Implémentation', 'Données exploitables'],
]))
story.append(PageBreak())

# ─── SECTION 2 ───────────────────────────────────────────────────────────────
story += h1_flow("2.", "Sources de données &amp; Méthodologie")
story.append(tbl_style([7.5*cm, 4.5*cm, 4.5*cm], [
    ['Fichier', 'Période', 'Lignes brutes'],
    ['Divvy_Trips_2019_Q1.csv', 'Janv.–Mars 2019', '365 069'],
    ['Divvy_Trips_2020_Q1.csv', 'Janv.–Mars 2020', '426 887'],
    ['202004 → 202012-divvy-tripdata.csv', 'Avr.–Déc. 2020', '3 114 796'],
    ['TOTAL', 'Jan 2019 – Déc 2020', '3 906 752'],
]))
story.append(tbl_style([3*cm, 1.5*cm, 12*cm], [
    ['Critère', 'Statut', 'Détail'],
    ['Reliable', '✅', 'Données opérationnelles capteurs automatiques'],
    ['Original', '✅', 'Source primaire : Motivate International Inc.'],
    ['Comprehensive', '✅', 'Tous les trajets sur la période, aucun échantillonnage'],
    ['Current', '⚠️', 'Données 2019–2020 : solides pour tendances, actualisation recommandée'],
    ['Cited', '✅', 'Divvy Data License Agreement — usage public autorisé'],
]))
story.append(PageBreak())

# ─── SECTION 3 ───────────────────────────────────────────────────────────────
story += h1_flow("3.", "Nettoyage des données")
story.append(tbl_style([4*cm, 7*cm, 5.5*cm], [
    ['Étape', 'Action', 'Impact'],
    ['Harmonisation', 'Renommage colonnes 2019 + Subscriber→member', 'Unification 11 fichiers'],
    ['Conversion datetime', 'started_at, ended_at → datetime64', 'Calculs temporels'],
    ['ride_length', '(ended_at − started_at) en minutes', 'Variable principale'],
    ['Variables temp.', 'day_of_week, month, year, season, hour_of_day', '5 nouvelles colonnes'],
    ['Doublons', 'Suppression sur ride_id', 'Dédoublonnage'],
    ['ride_length ≤ 0', 'Suppression (erreurs système)', 'Données invalides'],
    ['ride_length > 1440', 'Suppression (vélos non retournés)', 'Outliers extrêmes'],
    ['Stations maintenance', 'HQ QR, TEST, DIVVY exclus', 'Trajets internes'],
    ['Résultat final', '3 906 752 → 3 885 439 trajets propres', '−21 313 (−0,5 %)'],
]))
story.append(PageBreak())

# ─── SECTION 4 ───────────────────────────────────────────────────────────────
story += h1_flow("4.", "Analyse &amp; Insights")

story += h2_flow("4.1", "Vue d'ensemble : volume et durée")
story.append(body_p(
    "Sur 3 885 439 trajets analysés, les membres représentent 64,6 % du volume mais effectuent "
    "des déplacements 2,5× plus courts que les casual riders.", True))
story.append(tbl_style([5*cm, 3.5*cm, 3.5*cm, 4.5*cm], [
    ['Métrique', 'Members', 'Casual riders', 'Ratio'],
    ['Nombre de trajets', '2 508 757', '1 376 682', 'Members × 1,8'],
    ['Part du total', '64,6 %', '35,4 %', '—'],
    ['Durée moyenne', '14,6 min', '37,1 min', 'Casual × 2,5'],
    ['Durée médiane', '10,6 min', '21,7 min', 'Casual × 2,0'],
    ['Jour de pointe', 'Jeudi', 'Samedi', '—'],
    ['Usage principal', 'Domicile ↔ Travail', 'Loisirs / Tourisme', '—'],
]))
# Figures 1 & 2 côte à côte
fig1 = os.path.join(FIG_DIR, '01_rides_count.png')
fig2 = os.path.join(FIG_DIR, '02_avg_ride_length.png')
side_row = []
for p in [fig1, fig2]:
    if os.path.exists(p):
        side_row.append(Image(p, width=7.5*cm, height=5.4*cm))
    else:
        side_row.append(Paragraph('[Image manquante]', S_SMALL))
if side_row:
    t2 = Table([side_row], colWidths=[8.5*cm, 8*cm])
    t2.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(t2)
    story.append(Paragraph(
        'Fig. 1 — Nombre de trajets  (01_rides_count.png)         '
        'Fig. 2 — Durée moyenne  (02_avg_ride_length.png)', S_CAPTION))
story += insight_flow(
    "Les casual riders effectuent 2,5× plus de minutes de vélo par trajet que les membres. "
    "Ce n'est pas un usage utilitaire — c'est un comportement récréatif ou touristique structurel.")

story += h2_flow("4.2", "Comportement temporel")
for lbl, items in [
    ("Par jour de la semaine", [
        "Members : pic le jeudi (~391k trajets), volume stable lundi–vendredi → usage domicile-travail.",
        "Casual : pic le samedi (~318k trajets), profil en cloche autour du week-end → usage loisir."]),
    ("Par mois / saison", [
        "Casual hyper-saisonniers : 51,5 % de leurs trajets annuels en été vs 32 % pour les membres.",
        "Hiver : membres actifs (556k) vs casual quasi-absents (57k)."]),
    ("Par heure de départ", [
        "Members : double pic à 8h et 17h → trajets domicile-travail confirmés.",
        "Casual : montée progressive dès 10h, pic unique à 15–17h → loisir."]),
]:
    story += h2_flow("", lbl)
    for item in items:
        story.append(bullet_p(item))

story += figure_flow('03_rides_by_dow.png', '3', 'Trajets par jour de la semaine')
story += figure_flow('04_rides_by_month.png', '4', 'Évolution mensuelle des trajets', width=15*cm)
story += figure_flow('07_rides_by_hour.png', '5', 'Répartition des trajets par heure de départ')
story += figure_flow('08_avg_length_by_dow.png', '6', 'Durée moyenne par jour de la semaine')
story += insight_flow(
    "Trois signaux temporels convergent — week-end, après-midi (15–17h), été (juin–août). "
    "Ce sont les trois fenêtres d'intervention marketing prioritaires pour cibler les casual riders.")

story += h2_flow("4.3", "Types de vélos utilisés")
story.append(body_p(
    "Les docked bikes dominent pour les deux types (>83 %). Les casual riders utilisent "
    "proportionnellement plus d'electric bikes (15,2 % vs 11,8 % pour les membres)."))
story += figure_flow('05_bike_types.png', '7', "Types de vélos utilisés — % par catégorie d'utilisateur")
story += insight_flow(
    "La préférence casual pour l'electric bike (15,2 %) ouvre une piste de communication "
    "sur le confort et la polyvalence.")

story += h2_flow("4.4", "Stations de départ — Casual riders")
story.append(body_p(
    "Les 10 stations les plus fréquentées par les casual riders sont toutes situées dans des "
    "zones touristiques : Lakefront Trail, Navy Pier, Millennium Park, Shedd Aquarium.", True))
story += figure_flow('06_top10_stations.png', '8', 'Top 10 stations de départ — Casual riders', width=15*cm)
story += insight_flow(
    "Les 10 stations prioritaires sont toutes concentrées sur le Lakefront de Chicago "
    "— une zone de ciblage géographique très précise.")
story.append(PageBreak())

# ─── SECTION 5 ───────────────────────────────────────────────────────────────
story += h1_flow("5.", "Recommandations Marketing")
story += colored_box_flow("RECOMMANDATION 1 — Campagne géolocalisée", C_BLUE_L, [
    ("Insight",  "Les casual se concentrent le week-end sur des stations touristiques identifiables."),
    ("Action",   "Publicités dans un rayon de 500 m autour des 10 stations casual, vendredi soir et samedi matin."),
    ("Message",  "« Tu roules déjà le week-end — économise avec l'abonnement annuel. »"),
    ("Canaux",   "Instagram/TikTok géolocalisés · notifications push in-app · affichage en station."),
    ("Impact",   "Conversion des casual récurrents du week-end au moment de leur usage maximal."),
], C_BLUE)
story += colored_box_flow("RECOMMANDATION 2 — Offre Été → Membre", C_GREEN_L, [
    ("Insight", "51,5 % des trajets casual en été → fenêtre de conversion optimale."),
    ("Action",  "En mai–juin : 2 premiers mois offerts aux casual ayant 3+ trajets en 30 jours."),
    ("Message", "« Tu as utilisé Cyclistic X fois ce mois-ci — tu aurais économisé Y€ avec un abonnement. »"),
    ("Canaux",  "Email ciblé · notification push in-app · bannières dans l'app."),
    ("Impact",  "Conversion pendant le pic d'usage, avant l'inactivité automne/hiver."),
], C_GREEN)
story += colored_box_flow("RECOMMANDATION 3 — Calculateur d'économies", C_AMB_L, [
    ("Insight", "Les membres utilisent les vélos aux heures de rush (8h, 17h). Les casual ignorent peut-être cet usage."),
    ("Action",  "Calculateur dans l'app : « Si tu fais X trajets/semaine, l'abonnement te coûte Y€/trajet. »"),
    ("Canaux",  "Content marketing · affichage stations aux heures de rush."),
], C_AMBER)
story += h2_flow("5.4", "Matrice de priorisation")
story.append(tbl_style([4.5*cm, 2*cm, 3*cm, 2.5*cm, 4.5*cm], [
    ['Recommandation', 'Effort', 'Impact', 'Délai', 'KPI de mesure'],
    ['1 — Géolocalisée', 'Faible', '★★★★', '1–2 sem.', 'Taux conversion/station'],
    ['2 — Offre été', 'Moyen', '★★★★★', '2–4 sem.', 'Nouveaux membres juin–août'],
    ['3 — Calculateur', 'Moyen', '★★★', '4–8 sem.', 'CTR calculateur &amp; conversions'],
]))
story.append(PageBreak())

# ─── SECTION 6 ───────────────────────────────────────────────────────────────
story += h1_flow("6.", "Conclusion &amp; Limites")
story.append(body_p(
    "Cette analyse de 3 885 439 trajets (2019–2020) établit une distinction comportementale nette "
    "entre membres et casual riders. La convergence de trois signaux temporels (week-end, après-midi, "
    "été) et d'un signal géographique (Lakefront) offre un cadre de ciblage marketing très précis.", True))
for lim in [
    "Absence de données individuelles : impossible d'identifier les casual récurrents sans accès aux comptes.",
    "Période historique : données 2019–2020, mise à jour 2022–2024 recommandée avant déploiement.",
    "Absence de données démographiques : âge, genre, localisation permettraient un ciblage plus fin.",
    "Recommandation : A/B test sur un sous-groupe de casual (1 offre, 1 canal, 1 station pilote).",
]:
    story.append(bullet_p(lim))
story.append(PageBreak())

# ─── SIGNATURE ───────────────────────────────────────────────────────────────
story += [Paragraph('<b><font color="#1A73E8">RÉALISÉ PAR</font></b>', S_H1), hr(), sp(8)]
badge_cell2 = [Image(BADGE, width=3.8*cm, height=3.8*cm)] if os.path.exists(BADGE) else [Paragraph('', S_SMALL)]
info_cell2 = [
    Paragraph('<b>Sidi Mohamed ALLY</b>',
        sty('sn', fontSize=16, fontName='DejaVu-Bold', textColor=C_DARK, leading=22)),
    Paragraph('<i>Analyste de données Professionnel Certifié</i>',
        sty('st', fontSize=11, textColor=C_GRAY, leading=16, fontName='DejaVu-Italic')),
    Paragraph('<b>Google Data Analytics Professional Certificate</b>',
        sty('sc', fontSize=10, textColor=C_BLUE, leading=15, fontName='DejaVu-Bold')),
    Paragraph('Certifié le 13 juin 2026  ·  Délivré par Google &amp; Coursera', S_SMALL),
    Paragraph(f'Badge vérifiable : <link href="{CREDLY}" color="#1A73E8"><u>{CREDLY}</u></link>', S_SMALL),
]
sig_tbl = Table([[badge_cell2, info_cell2]], colWidths=[5*cm, 11.5*cm])
sig_tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),6)]))
story += [sig_tbl, PageBreak()]

# ─── GLOSSAIRE ───────────────────────────────────────────────────────────────
story += h1_flow("—", "Glossaire")
story.append(tbl_style([3.5*cm, 13*cm], [
    ['Terme', 'Définition'],
    ['A/B Test', "Expérimentation comparant deux variantes pour mesurer laquelle est la plus efficace."],
    ['Casual rider', "Utilisateur ayant souscrit un pass journée ou trajet unique (non-membre)."],
    ['Credly', "Plateforme de badges de certification numériques vérifiables en ligne."],
    ['CTR', "Click-Through Rate — taux de clic sur une publicité ou un élément interactif."],
    ['CSV', "Comma-Separated Values — format de fichier texte pour les données tabulaires."],
    ['KPI', "Key Performance Indicator — indicateur clé permettant de mesurer l'atteinte d'un objectif."],
    ['Member', "Utilisateur Cyclistic détenteur d'un abonnement annuel."],
    ['PII', "Personally Identifiable Information — données permettant d'identifier une personne."],
    ['ROCCC', "Cadre d'évaluation : Reliable, Original, Comprehensive, Current, Cited."],
    ['Rush hours', "Heures de pointe des transports (7h–9h et 16h–18h)."],
    ['SQL', "Structured Query Language — langage de requête pour les bases de données relationnelles."],
]))
story.append(PageBreak())

# ─── ANNEXE A — SQL ──────────────────────────────────────────────────────────
story += h1_flow("A.", "Annexe — Requêtes SQL")
story.append(body_p(
    "12 requêtes SQL reproduisant l'analyse en SQL standard (PostgreSQL / BigQuery / DuckDB). "
    "PERCENTILE_CONT utilisé à la place de MEDIAN() pour assurer la portabilité."))

with open(SQL_FILE, encoding='utf-8') as f:
    sql_raw = f.read()
for block in re.split(r'\n(?=-- ──)', sql_raw):
    block = block.strip()
    if not block:
        continue
    lines_b = block.split('\n')
    title_l = next((l for l in lines_b if '──' in l or '--' in l[:4]), None)
    if title_l:
        story.append(Paragraph(
            f'<b>{title_l.replace("--","").strip()}</b>',
            sty(f'sqlt{len(story)}', fontSize=9, fontName='DejaVu-Bold',
                textColor=C_BLUE, spaceAfter=2, spaceBefore=10)))
    story.append(Paragraph(
        block.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'), S_CODE))

story.append(PageBreak())

# ─── ANNEXE B — PYTHON ───────────────────────────────────────────────────────
story += h1_flow("B.", "Annexe — Scripts Python clés")
snippets = [
    ("B.1 — Harmonisation schéma Legacy 2019 (02_cleaning.py)", """\
def load_legacy_2019(path):
    df = pd.read_csv(path, low_memory=False)
    df = df.rename(columns={
        "trip_id":"ride_id","start_time":"started_at","end_time":"ended_at",
        "from_station_id":"start_station_id","from_station_name":"start_station_name",
        "to_station_id":"end_station_id","to_station_name":"end_station_name",
        "usertype":"member_casual"})
    df["member_casual"] = df["member_casual"].replace(
        {"Subscriber":"member","Customer":"casual"})
    df["rideable_type"] = "unknown"
    return df[COLS_2020]"""),
    ("B.2 — Pipeline de nettoyage (02_cleaning.py)", """\
df["ride_length"] = (df["ended_at"]-df["started_at"]).dt.total_seconds()/60
df["day_of_week"] = df["started_at"].dt.dayofweek.map({6:1,0:2,1:3,2:4,3:5,4:6,5:7})
df["month"]  = df["started_at"].dt.month
df["year"]   = df["started_at"].dt.year
df["season"] = df["month"].map({12:"Winter",1:"Winter",2:"Winter",
    3:"Spring",4:"Spring",5:"Spring",6:"Summer",7:"Summer",8:"Summer",
    9:"Fall",10:"Fall",11:"Fall"})
df = df.drop_duplicates(subset=["ride_id"])
df = df[(df["ride_length"] > 0) & (df["ride_length"] <= 1440)]"""),
    ("B.3 — Analyse descriptive &amp; top 10 stations (03_analysis.py)", """\
desc = df.groupby("member_casual")["ride_length"].agg(
    mean_ride_length="mean", median_ride_length="median",
    max_ride_length="max", total_rides="count").round(2).reset_index()

top10_casual = (df[(df["start_station_name"].notna()) &
                   (df["member_casual"]=="casual")]
    .groupby("start_station_name").size()
    .reset_index(name="total_rides")
    .sort_values("total_rides", ascending=False).head(10))"""),
]
for title, code in snippets:
    story.append(Paragraph(f'<b>{title}</b>',
        sty(f'pyt{len(story)}', fontSize=9, fontName='DejaVu-Bold',
            textColor=C_BLUE, spaceAfter=2, spaceBefore=10)))
    story.append(Paragraph(
        code.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'), S_CODE))
story.append(PageBreak())

# ─── ANNEXE C ────────────────────────────────────────────────────────────────
story += h1_flow("C.", "Annexe — Sources de données &amp; Licence")
story.append(tbl_style([3.5*cm, 13*cm], [
    ['Élément', 'Détail'],
    ['Source',   'Divvy Trip Data — Motivate International Inc.'],
    ['Licence',  'Divvy Data License Agreement — usage public autorisé'],
    ['Période',  'Janvier 2019 – Décembre 2020 (11 fichiers CSV)'],
    ['Volume',   '3 906 752 trajets bruts → 3 885 439 après nettoyage'],
    ['Anonymat', 'Aucune PII — données 100 % anonymisées'],
    ['Note',     "Cyclistic est une entreprise fictive (Capstone Case Study 1, Google DA Certificate). "
                 "Les données Divvy sont réelles et adaptées à des fins pédagogiques."],
]))

# ══════════════════════════════════════════════════════════════════════════════
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
size_kb = os.path.getsize(OUT_PDF) // 1024
print(f"PDF genere  : {OUT_PDF}")
print(f"Taille      : {size_kb} KB")
