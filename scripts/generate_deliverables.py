"""Genera todos los diagramas (.png y .drawio), capturas reales del sistema,
anexos exportados y el Manual PDF oficial 'Línea de productos basada en Django'.
"""

import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / 'entregables_documentacion'
DIAG_DIR = OUT_DIR / 'diagramas'
CAP_DIR = OUT_DIR / 'capturas'
ANEXO_DIR = OUT_DIR / 'anexos'

for d in (OUT_DIR, DIAG_DIR, CAP_DIR, ANEXO_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# UTILIDADES DE FUENTES Y DIBUJO PILLOW
# ==============================================================================
def load_font(size, bold=False, mono=False):
    candidates = []
    if mono:
        candidates = [
            r'C:\Windows\Fonts\consolab.ttf' if bold else r'C:\Windows\Fonts\consola.ttf',
            r'C:\Windows\Fonts\courbd.ttf' if bold else r'C:\Windows\Fonts\cour.ttf',
        ]
    else:
        candidates = [
            r'C:\Windows\Fonts\segoeuib.ttf' if bold else r'C:\Windows\Fonts\segoeui.ttf',
            r'C:\Windows\Fonts\arialbd.ttf' if bold else r'C:\Windows\Fonts\arial.ttf',
        ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


NAVY = (11, 37, 69)
BLUE = (19, 64, 116)
ORANGE = (245, 130, 32)
TEAL = (15, 118, 110)
TEAL_BG = (204, 251, 241)
EMERALD = (5, 150, 105)
EMERALD_BG = (209, 250, 229)
INDIGO = (55, 48, 163)
INDIGO_BG = (224, 231, 255)
AMBER = (180, 83, 9)
AMBER_BG = (254, 243, 199)
ROSE = (190, 18, 60)
ROSE_BG = (255, 228, 230)
SLATE_BG = (248, 250, 252)
SLATE_BORDER = (203, 213, 225)
TEXT_DARK = (15, 23, 42)
TEXT_MUTED = (71, 85, 105)
WHITE = (255, 255, 255)


def draw_header(draw, width, title, subtitle):
    draw.rectangle([0, 0, width, 102], fill=NAVY)
    draw.rectangle([0, 96, width, 102], fill=ORANGE)
    f_title = load_font(30, bold=True)
    f_sub = load_font(17, bold=False)
    draw.text((40, 20), title, fill=WHITE, font=f_title)
    draw.text((40, 62), subtitle, fill=(203, 213, 225), font=f_sub)


def draw_box(draw, box, title, lines, fill=WHITE, border=BLUE, header_fill=BLUE, title_color=WHITE):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle([x1 + 4, y1 + 4, x2 + 4, y2 + 4], radius=12, fill=(226, 232, 240))
    draw.rounded_rectangle([x1, y1, x2, y2], radius=12, fill=fill, outline=border, width=2)
    draw.rounded_rectangle([x1, y1, x2, y1 + 38], radius=12, fill=header_fill)
    draw.rectangle([x1, y1 + 24, x2, y1 + 38], fill=header_fill)
    f_h = load_font(17, bold=True)
    f_b = load_font(15, bold=False)
    draw.text((x1 + 14, y1 + 9), title, fill=title_color, font=f_h)
    cy = y1 + 50
    for line in lines:
        draw.text((x1 + 14, cy), line, fill=TEXT_DARK, font=f_b)
        cy += 24


def draw_arrow(draw, start, end, color=TEXT_MUTED, width=3, dashed=False):
    x1, y1 = start
    x2, y2 = end
    if dashed:
        dx, dy = x2 - x1, y2 - y1
        dist = max(1, int((dx * dx + dy * dy) ** 0.5))
        step = 14
        for i in range(0, dist, step * 2):
            t1 = i / dist
            t2 = min(1.0, (i + step) / dist)
            draw.line(
                [(x1 + dx * t1, y1 + dy * t1), (x1 + dx * t2, y1 + dy * t2)],
                fill=color,
                width=width,
            )
    else:
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)

    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    head_len = 12
    p1 = (x2 - head_len * math.cos(angle - 0.42), y2 - head_len * math.sin(angle - 0.42))
    p2 = (x2 - head_len * math.cos(angle + 0.42), y2 - head_len * math.sin(angle + 0.42))
    draw.polygon([(x2, y2), p1, p2], fill=color)


# ==============================================================================
# GENERACIÓN DE ARCHIVOS .DRAWIO EDITABLES
# ==============================================================================
def write_drawio(path, page_name, cells):
    """Genera un diagrama .drawio válido compatible con draw.io / diagrams.net."""
    xml_cells = [
        '<mxCell id="0"/>',
        '<mxCell id="1" parent="0"/>',
    ]
    for c in cells:
        cid = c['id']
        val = escape(c['value'])
        style = escape(c['style'])
        if c.get('edge'):
            src = c['source']
            tgt = c['target']
            xml_cells.append(
                f'<mxCell id="{cid}" value="{val}" style="{style}" edge="1" parent="1" source="{src}" target="{tgt}">'
                '<mxGeometry relative="1" as="geometry"/></mxCell>'
            )
        else:
            x, y, w, h = c['x'], c['y'], c['w'], c['h']
            xml_cells.append(
                f'<mxCell id="{cid}" value="{val}" style="{style}" vertex="1" parent="1">'
                f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
            )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mxfile host="app.diagrams.net" version="24.7.17">\n'
        f'  <diagram id="{escape(page_name)}" name="{escape(page_name)}">\n'
        '    <mxGraphModel dx="1420" dy="860" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="1000">\n'
        '      <root>\n        ' + '\n        '.join(xml_cells) + '\n      </root>\n'
        '    </mxGraphModel>\n'
        '  </diagram>\n'
        '</mxfile>\n'
    )
    path.write_text(xml, encoding='utf-8')


# ==============================================================================
# DIAGRAMA 1: ARQUITECTURA DE CARPETAS DEL PROYECTO (SESIÓN 1)
# ==============================================================================
def build_diagram_01_folders():
    w, h = 1500, 920
    img = Image.new('RGB', (w, h), SLATE_BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        w,
        'Sesión 1 — Diagrama de Arquitectura de Carpetas del Proyecto Django SPL',
        'Organización modular separando configuración de variabilidad, núcleo, apps reutilizables y apps opcionales',
    )

    draw_box(
        draw,
        (510, 128, 990, 250),
        'Raíz: practica gestion/ (Proyecto Django SPL)',
        [
            '• config_product.py   -> Perfiles PRODUCT_A y PRODUCT_B',
            '• manage.py           -> CLI administrativo de Django',
            '• run_variante_a.bat / run_variante_b.bat',
        ],
        fill=WHITE,
        border=NAVY,
        header_fill=NAVY,
    )

    cols = [
        (
            (40, 320, 315, 760),
            'spl_project/ (Config)',
            BLUE,
            WHITE,
            [
                '__init__.py',
                'settings.py',
                '  -> Lee config_product.py',
                '  -> ENABLE_REPORTS',
                '  -> ENABLE_NOTIFICATIONS',
                'urls.py',
                '  -> include() condicional',
                'wsgi.py / asgi.py',
            ],
        ),
        (
            (340, 320, 615, 760),
            'core/ (Núcleo Base)',
            INDIGO,
            INDIGO_BG,
            [
                'models.py',
                '  -> AcademicProject',
                'views.py',
                '  -> if settings.ENABLE_REPORTS',
                'context_processors.py',
                '  -> Banderas globales SPL',
                'urls.py / admin.py',
                'templates/core/*.html',
            ],
        ),
        (
            (640, 320, 920, 760),
            'Apps Reutilizables',
            TEAL,
            TEAL_BG,
            [
                'accounts/',
                '  -> UserProfile, roles',
                '  -> Sin acoplamiento a core',
                '  -> templates/accounts/',
                'file_manager/',
                '  -> Attachment (reference_tag)',
                '  -> Carga documental portátil',
                '  -> templates/file_manager/',
            ],
        ),
        (
            (945, 320, 1215, 760),
            'Apps Opcionales (SPL)',
            AMBER,
            AMBER_BG,
            [
                'reports/ (Sesión 2)',
                '  -> views.py (PDF & CSV)',
                '  -> urls.py (include cond.)',
                '  -> templates/reports/',
                'notifications/ (Sesión 3)',
                '  -> SystemNotification',
                '  -> views.py / urls.py',
                '  -> templates/notifications/',
            ],
        ),
        (
            (1240, 320, 1465, 760),
            'Soporte & Evidencia',
            EMERALD,
            EMERALD_BG,
            [
                'templates/base.html',
                'static/css/styles.css',
                'scripts/',
                '  -> init_db.py',
                '  -> verify_spl.py',
                '  -> generate_deliverables.py',
                'entregables_documentacion/',
                '  -> Manual PDF + Diagramas',
            ],
        ),
    ]

    for box, title, hdr, bg, lines in cols:
        draw_box(draw, box, title, lines, fill=bg, border=hdr, header_fill=hdr)
        cx = (box[0] + box[2]) // 2
        draw_arrow(draw, (750, 250), (cx, box[1]), color=BLUE, width=3)

    draw.rounded_rectangle([40, 800, 1465, 882], radius=10, fill=WHITE, outline=SLATE_BORDER, width=2)
    f_note = load_font(16, bold=False)
    f_note_b = load_font(16, bold=True)
    draw.text((62, 815), 'Principio SPL aplicado:', fill=NAVY, font=f_note_b)
    draw.text(
        (252, 815),
        'Cada carpeta representa una responsabilidad aislada. Las apps reutilizables (accounts, file_manager) y las opcionales (reports,',
        fill=TEXT_DARK,
        font=f_note,
    )
    draw.text(
        (62, 845),
        'notifications) pueden copiarse o activarse en otros proyectos Django con mínima configuración en settings.py y urls.py.',
        fill=TEXT_DARK,
        font=f_note,
    )

    img.save(DIAG_DIR / '01_arquitectura_carpetas.png')

    cells = [
        {'id': 'root', 'value': 'practica gestion/\nconfig_product.py | manage.py', 'x': 560, 'y': 40, 'w': 360, 'h': 80, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#0B2545;fontColor=#FFFFFF;fontStyle=1;'},
        {'id': 'cfg', 'value': 'spl_project/\nsettings.py\nurls.py (include condicional)', 'x': 60, 'y': 220, 'w': 240, 'h': 150, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#134074;fontStyle=1;'},
        {'id': 'core', 'value': 'core/ (Núcleo)\nAcademicProject\nviews.py + context_processors.py', 'x': 340, 'y': 220, 'w': 240, 'h': 150, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#E0E7FF;strokeColor=#3730A3;fontStyle=1;'},
        {'id': 'reus', 'value': 'Apps Reutilizables\naccounts/\nfile_manager/', 'x': 620, 'y': 220, 'w': 240, 'h': 150, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#CCFBF1;strokeColor=#0F766E;fontStyle=1;'},
        {'id': 'opt', 'value': 'Apps Opcionales\nreports/ (ENABLE_REPORTS)\nnotifications/ (ENABLE_NOTIFICATIONS)', 'x': 900, 'y': 220, 'w': 260, 'h': 150, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#B45309;fontStyle=1;'},
        {'id': 'sup', 'value': 'templates/ | static/\nscripts/ | entregables_documentacion/', 'x': 1200, 'y': 220, 'w': 240, 'h': 150, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#D1FAE5;strokeColor=#059669;fontStyle=1;'},
        {'id': 'e1', 'value': '', 'edge': True, 'source': 'root', 'target': 'cfg', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;'},
        {'id': 'e2', 'value': '', 'edge': True, 'source': 'root', 'target': 'core', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;'},
        {'id': 'e3', 'value': '', 'edge': True, 'source': 'root', 'target': 'reus', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;'},
        {'id': 'e4', 'value': '', 'edge': True, 'source': 'root', 'target': 'opt', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;'},
        {'id': 'e5', 'value': '', 'edge': True, 'source': 'root', 'target': 'sup', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;'},
    ]
    write_drawio(DIAG_DIR / '01_arquitectura_carpetas.drawio', 'Arquitectura_Carpetas', cells)


# ==============================================================================
# DIAGRAMA 2: ARQUITECTURA FUNCIONAL (REUTILIZABLES VS OPCIONALES)
# ==============================================================================
def build_diagram_02_functional():
    w, h = 1500, 920
    img = Image.new('RGB', (w, h), SLATE_BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        w,
        'Sesión 1 — Diagrama de Arquitectura Funcional (Reutilizables vs. Opcionales)',
        'Interacción entre el Orquestador de Configuración (config_product.py), el Núcleo y los Puntos de Variabilidad',
    )

    draw_box(
        draw,
        (430, 130, 1070, 265),
        'Capa de Configuración y Variabilidad (SPL)',
        [
            '• config_product.py: define perfiles PRODUCT_A (Básico) y PRODUCT_B (Completo)',
            '• spl_project/settings.py: expone ENABLE_REPORTS y ENABLE_NOTIFICATIONS',
            '• spl_project/urls.py: enruta dinámicamente mediante include() condicional',
        ],
        fill=WHITE,
        border=NAVY,
        header_fill=NAVY,
    )

    draw_box(
        draw,
        (60, 350, 470, 620),
        'Componentes Reutilizables (Core Assets)',
        [
            '1. accounts/ (Usuarios y Roles)',
            '   • Perfiles ADMIN / DOCENTE / ESTUDIANTE',
            '   • Portátil sin cambios a otros sistemas',
            '',
            '2. file_manager/ (Gestor Documental)',
            '   • Adjuntos con reference_tag genérico',
            '   • Cero llaves foráneas rígidas a core',
        ],
        fill=TEAL_BG,
        border=TEAL,
        header_fill=TEAL,
    )

    draw_box(
        draw,
        (525, 350, 975, 620),
        'Núcleo Obligatorio del Producto (core/)',
        [
            '• Modelo AcademicProject (proyectos, avance, estado)',
            '• Dashboard central con filtros y creación',
            '• Context Processor: inyecta banderas a HTML',
            '• Puntos de extensión en vistas y plantillas:',
            '  if settings.ENABLE_REPORTS:',
            '      mostrar botones Exportar PDF / CSV',
        ],
        fill=INDIGO_BG,
        border=INDIGO,
        header_fill=INDIGO,
    )

    draw_box(
        draw,
        (1030, 350, 1440, 620),
        'Funcionalidades Opcionales (Variabilidad)',
        [
            '1. reports/ [Flag: ENABLE_REPORTS]',
            '   • Dashboard analítico de cartera',
            '   • Exportación PDF (ReportLab) y CSV',
            '',
            '2. notifications/ [Flag: ENABLE_NOTIFICATIONS]',
            '   • Centro de alertas y estado de lectura',
            '   • Desactivada por completo en PRODUCT_A',
        ],
        fill=AMBER_BG,
        border=AMBER,
        header_fill=AMBER,
    )

    draw_box(
        draw,
        (260, 710, 1240, 855),
        'Capa de Presentación y Persistencia Compartida',
        [
            '• Plantillas base.html + CSS Institucional UNEMI: muestran u ocultan menús con {% if ENABLE_REPORTS %} y {% if ENABLE_NOTIFICATIONS %}',
            '• Base de Datos SQLite (db.sqlite3): almacena esquemas de core, accounts, file_manager y notifications',
        ],
        fill=WHITE,
        border=BLUE,
        header_fill=BLUE,
    )

    draw_arrow(draw, (630, 265), (265, 350), color=TEAL, width=3)
    draw_arrow(draw, (750, 265), (750, 350), color=INDIGO, width=3)
    draw_arrow(draw, (870, 265), (1235, 350), color=AMBER, width=3, dashed=True)
    draw_arrow(draw, (470, 485), (525, 485), color=TEAL, width=3)
    draw_arrow(draw, (1030, 485), (975, 485), color=AMBER, width=3, dashed=True)
    draw_arrow(draw, (265, 620), (480, 710), color=BLUE, width=3)
    draw_arrow(draw, (750, 620), (750, 710), color=BLUE, width=3)
    draw_arrow(draw, (1235, 620), (1020, 710), color=AMBER, width=3, dashed=True)

    img.save(DIAG_DIR / '02_arquitectura_funcional.png')

    cells = [
        {'id': 'cfg', 'value': 'Capa de Configuración SPL\nconfig_product.py | settings.py | urls.py', 'x': 480, 'y': 40, 'w': 440, 'h': 90, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#0B2545;fontColor=#FFFFFF;fontStyle=1;'},
        {'id': 'reus', 'value': 'Componentes Reutilizables\naccounts/ + file_manager/', 'x': 80, 'y': 220, 'w': 320, 'h': 150, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#CCFBF1;strokeColor=#0F766E;fontStyle=1;'},
        {'id': 'core', 'value': 'Núcleo Obligatorio\ncore/ (AcademicProject + Dashboard)', 'x': 540, 'y': 220, 'w': 320, 'h': 150, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#E0E7FF;strokeColor=#3730A3;fontStyle=1;'},
        {'id': 'opt', 'value': 'Funcionalidades Opcionales\nreports/ + notifications/', 'x': 1000, 'y': 220, 'w': 320, 'h': 150, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#B45309;fontStyle=1;'},
        {'id': 'ui', 'value': 'Plantillas Condicionales + Base de Datos SQLite', 'x': 360, 'y': 460, 'w': 680, 'h': 90, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#134074;fontStyle=1;'},
        {'id': 'e1', 'value': 'Siempre activo', 'edge': True, 'source': 'cfg', 'target': 'reus', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e2', 'value': 'Siempre activo', 'edge': True, 'source': 'cfg', 'target': 'core', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e3', 'value': 'Condicional (Flags)', 'edge': True, 'source': 'cfg', 'target': 'opt', 'style': 'edgeStyle=orthogonalEdgeStyle;dashed=1;'},
        {'id': 'e4', 'value': '', 'edge': True, 'source': 'reus', 'target': 'ui', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e5', 'value': '', 'edge': True, 'source': 'core', 'target': 'ui', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e6', 'value': 'include() condicional', 'edge': True, 'source': 'opt', 'target': 'ui', 'style': 'edgeStyle=orthogonalEdgeStyle;dashed=1;'},
    ]
    write_drawio(DIAG_DIR / '02_arquitectura_funcional.drawio', 'Arquitectura_Funcional', cells)


# ==============================================================================
# DIAGRAMA 3: MODELO DE CARACTERÍSTICAS SPL (SESIÓN 4 — FODA)
# ==============================================================================
def draw_feature_node(draw, box, title, subtitle, mandatory=True, bg=WHITE, border=BLUE):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle([x1 + 3, y1 + 3, x2 + 3, y2 + 3], radius=10, fill=(226, 232, 240))
    draw.rounded_rectangle([x1, y1, x2, y2], radius=10, fill=bg, outline=border, width=2)
    f_t = load_font(16, bold=True)
    f_s = load_font(13, bold=False)
    draw.text((x1 + 14, y1 + 14), title, fill=NAVY, font=f_t)
    draw.text((x1 + 14, y1 + 42), subtitle, fill=TEXT_MUTED, font=f_s)
    cx = (x1 + x2) // 2
    r = 8
    if mandatory is not None:
        fill_c = NAVY if mandatory else WHITE
        draw.ellipse([cx - r, y1 - r, cx + r, y1 + r], fill=fill_c, outline=NAVY, width=2)


def build_diagram_03_feature_model():
    w, h = 1500, 920
    img = Image.new('RGB', (w, h), SLATE_BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        w,
        'Sesión 4 — Modelo de Características (Feature Model SPL — Notación FODA)',
        'Representación formal de características obligatorias y opcionales del Sistema Académico Django',
    )

    # Raíz
    draw_feature_node(
        draw,
        (510, 140, 990, 230),
        'Sistema Académico Modular (SPL UNEMI)',
        'Línea de Productos Base en Django 6 · config_product.py',
        mandatory=None,
        bg=INDIGO_BG,
        border=NAVY,
    )

    # Nivel 2
    draw_feature_node(
        draw,
        (110, 330, 560, 420),
        'Núcleo y Componentes Reutilizables',
        'Características Obligatorias (Presentes en A y B)',
        mandatory=True,
        bg=TEAL_BG,
        border=TEAL,
    )
    draw_feature_node(
        draw,
        (940, 330, 1390, 420),
        'Módulos de Variabilidad Extendida',
        'Características Opcionales (Controladas por Flags)',
        mandatory=False,
        bg=AMBER_BG,
        border=AMBER,
    )

    draw.line([(750, 230), (750, 280), (335, 280), (335, 330)], fill=NAVY, width=3)
    draw.line([(750, 280), (1165, 280), (1165, 330)], fill=NAVY, width=3)
    # Redibujar círculos sobre líneas
    draw.ellipse([335 - 8, 330 - 8, 335 + 8, 330 + 8], fill=NAVY, outline=NAVY, width=2)
    draw.ellipse([1165 - 8, 330 - 8, 1165 + 8, 330 + 8], fill=WHITE, outline=NAVY, width=2)

    # Hijos obligatorios
    mand_children = [
        ((50, 530, 275, 630), 'App core/', 'Proyectos y Tablero'),
        ((295, 530, 520, 630), 'App accounts/', 'Usuarios y Roles'),
        ((540, 530, 765, 630), 'App file_manager/', 'Gestión de Archivos'),
    ]
    draw.line([(335, 420), (335, 475), (162, 475), (162, 530)], fill=TEAL, width=3)
    draw.line([(335, 475), (407, 475), (407, 530)], fill=TEAL, width=3)
    draw.line([(335, 475), (652, 475), (652, 530)], fill=TEAL, width=3)
    for box, t, s in mand_children:
        draw_feature_node(draw, box, t, s, mandatory=True, bg=WHITE, border=TEAL)

    # Hijos opcionales
    opt_children = [
        ((825, 530, 1135, 630), 'App reports/', 'Flag: ENABLE_REPORTS (PDF / CSV)'),
        ((1160, 530, 1465, 630), 'App notifications/', 'Flag: ENABLE_NOTIFICATIONS (Alertas)'),
    ]
    draw.line([(1165, 420), (1165, 475), (980, 475), (980, 530)], fill=AMBER, width=3)
    draw.line([(1165, 475), (1312, 475), (1312, 530)], fill=AMBER, width=3)
    for box, t, s in opt_children:
        draw_feature_node(draw, box, t, s, mandatory=False, bg=WHITE, border=AMBER)

    # Leyenda y Reglas de Configuración
    draw.rounded_rectangle([50, 700, 1465, 875], radius=12, fill=WHITE, outline=SLATE_BORDER, width=2)
    f_b = load_font(17, bold=True)
    f_r = load_font(15, bold=False)
    draw.text((80, 718), 'Leyenda FODA y Reglas de Derivación de Productos:', fill=NAVY, font=f_b)
    draw.ellipse([80, 756, 98, 774], fill=NAVY, outline=NAVY, width=2)
    draw.text((112, 754), 'Característica Obligatoria (Mandatory): incluida siempre en todas las variantes (core, accounts, file_manager).', fill=TEXT_DARK, font=f_r)
    draw.ellipse([80, 792, 98, 810], fill=WHITE, outline=NAVY, width=2)
    draw.text((112, 790), 'Característica Opcional (Optional): habilitada según la configuración seleccionada en config_product.py.', fill=TEXT_DARK, font=f_r)
    draw.text((80, 828), 'Restricciones válidas:  PRODUCT_A = {core, accounts, file_manager}   |   PRODUCT_B = PRODUCT_A + {reports, notifications}', fill=BLUE, font=f_b)

    img.save(DIAG_DIR / '03_modelo_caracteristicas_spl.png')

    cells = [
        {'id': 'spl', 'value': 'Sistema Académico Modular (SPL UNEMI)', 'x': 500, 'y': 40, 'w': 380, 'h': 70, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#0B2545;fontColor=#FFFFFF;fontStyle=1;'},
        {'id': 'mand', 'value': '● Obligatorias (Core Assets)', 'x': 160, 'y': 180, 'w': 320, 'h': 70, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#CCFBF1;strokeColor=#0F766E;fontStyle=1;'},
        {'id': 'opt', 'value': '○ Opcionales (Variabilidad)', 'x': 900, 'y': 180, 'w': 320, 'h': 70, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#B45309;fontStyle=1;'},
        {'id': 'c1', 'value': '● core/', 'x': 40, 'y': 330, 'w': 180, 'h': 70, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0F766E;fontStyle=1;'},
        {'id': 'c2', 'value': '● accounts/', 'x': 240, 'y': 330, 'w': 180, 'h': 70, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0F766E;fontStyle=1;'},
        {'id': 'c3', 'value': '● file_manager/', 'x': 440, 'y': 330, 'w': 180, 'h': 70, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0F766E;fontStyle=1;'},
        {'id': 'o1', 'value': '○ reports/\n(ENABLE_REPORTS)', 'x': 780, 'y': 330, 'w': 240, 'h': 70, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#B45309;fontStyle=1;'},
        {'id': 'o2', 'value': '○ notifications/\n(ENABLE_NOTIFICATIONS)', 'x': 1060, 'y': 330, 'w': 260, 'h': 70, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#B45309;fontStyle=1;'},
        {'id': 'e1', 'value': 'Obligatoria', 'edge': True, 'source': 'spl', 'target': 'mand', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e2', 'value': 'Opcional', 'edge': True, 'source': 'spl', 'target': 'opt', 'style': 'edgeStyle=orthogonalEdgeStyle;dashed=1;'},
        {'id': 'e3', 'value': '', 'edge': True, 'source': 'mand', 'target': 'c1', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e4', 'value': '', 'edge': True, 'source': 'mand', 'target': 'c2', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e5', 'value': '', 'edge': True, 'source': 'mand', 'target': 'c3', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e6', 'value': '', 'edge': True, 'source': 'opt', 'target': 'o1', 'style': 'edgeStyle=orthogonalEdgeStyle;dashed=1;'},
        {'id': 'e7', 'value': '', 'edge': True, 'source': 'opt', 'target': 'o2', 'style': 'edgeStyle=orthogonalEdgeStyle;dashed=1;'},
    ]
    write_drawio(DIAG_DIR / '03_modelo_caracteristicas_spl.drawio', 'Modelo_Caracteristicas_SPL', cells)


# ==============================================================================
# DIAGRAMA 4: ÁRBOL DE DECISIONES PARA VARIANTES (SESIÓN 4)
# ==============================================================================
def build_diagram_04_decision_tree():
    w, h = 1500, 920
    img = Image.new('RGB', (w, h), SLATE_BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        w,
        'Sesión 4 — Árbol de Decisiones para Configuración de Variantes (SPL)',
        'Flujo de evaluación desde config_product.py -> settings.py -> urls.py para derivar Variante A y Variante B',
    )

    draw_box(
        draw,
        (485, 130, 1015, 235),
        '1. Inicio: Variable SPL_VARIANT / config_product.py',
        [
            'get_product_config(SPL_VARIANT) carga el perfil seleccionado',
            'Base fija incluida: core + accounts + file_manager',
        ],
        fill=WHITE,
        border=NAVY,
        header_fill=NAVY,
    )

    draw_box(
        draw,
        (470, 295, 1030, 395),
        '2. Decisión: ¿Qué nivel funcional requiere el cliente/entorno?',
        [
            'Evaluación de banderas: ENABLE_REPORTS y ENABLE_NOTIFICATIONS',
        ],
        fill=INDIGO_BG,
        border=INDIGO,
        header_fill=INDIGO,
    )
    draw_arrow(draw, (750, 235), (750, 295), color=NAVY, width=3)

    # Rama A
    draw_box(
        draw,
        (80, 470, 670, 695),
        'Rama A: Sistema Básico (PRODUCT_A)',
        [
            '• ENABLE_REPORTS = False',
            '• ENABLE_NOTIFICATIONS = False',
            '• INSTALLED_APPS excluye reports y notifications',
            '• urls.py omite include("reports.urls") y include("notifications.urls")',
            '• Resultado: rutas /reports/ y /notifications/ retornan HTTP 404',
        ],
        fill=WHITE,
        border=BLUE,
        header_fill=BLUE,
    )

    # Rama B
    draw_box(
        draw,
        (830, 470, 1420, 695),
        'Rama B: Sistema Completo (PRODUCT_B)',
        [
            '• ENABLE_REPORTS = True',
            '• ENABLE_NOTIFICATIONS = True',
            '• INSTALLED_APPS incorpora reports y notifications',
            '• urls.py ejecuta include() condicional para ambas rutas',
            '• Resultado: Exportación PDF/CSV y Alertas activas (HTTP 200)',
        ],
        fill=EMERALD_BG,
        border=EMERALD,
        header_fill=EMERALD,
    )

    draw_arrow(draw, (580, 395), (375, 470), color=BLUE, width=3)
    draw_arrow(draw, (920, 395), (1125, 470), color=EMERALD, width=3)

    f_lbl = load_font(15, bold=True)
    draw.text((215, 412), 'SPL_VARIANT = PRODUCT_A', fill=BLUE, font=f_lbl)
    draw.text((1060, 412), 'SPL_VARIANT = PRODUCT_B', fill=EMERALD, font=f_lbl)

    # Rama Sesión 2 (caso intermedio)
    draw_box(
        draw,
        (220, 745, 1280, 875),
        'Variante Intermedia (Sesión 2 — Aislamiento Individual)',
        [
            'Es posible activar solo ENABLE_REPORTS = True manteniendo ENABLE_NOTIFICATIONS = False (vía SPL_ENABLE_REPORTS=True).',
            'Esto demuestra independencia modular total: cada característica opcional puede activarse sin depender de la otra.',
        ],
        fill=AMBER_BG,
        border=AMBER,
        header_fill=AMBER,
    )

    img.save(DIAG_DIR / '04_arbol_decisiones_variantes.png')

    cells = [
        {'id': 'start', 'value': '1. Inicio: config_product.py\n(Núcleo: core + accounts + file_manager)', 'x': 500, 'y': 40, 'w': 400, 'h': 80, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#0B2545;fontColor=#FFFFFF;fontStyle=1;'},
        {'id': 'dec', 'value': '2. Selección de Variante (SPL_VARIANT)', 'x': 530, 'y': 170, 'w': 340, 'h': 80, 'style': 'rhombus;whiteSpace=wrap;html=1;fillColor=#E0E7FF;strokeColor=#3730A3;fontStyle=1;'},
        {'id': 'varA', 'value': 'PRODUCT_A (Sistema Básico)\nENABLE_REPORTS = False\nENABLE_NOTIFICATIONS = False', 'x': 120, 'y': 330, 'w': 380, 'h': 130, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#134074;fontStyle=1;'},
        {'id': 'varB', 'value': 'PRODUCT_B (Sistema Completo)\nENABLE_REPORTS = True\nENABLE_NOTIFICATIONS = True', 'x': 900, 'y': 330, 'w': 380, 'h': 130, 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#D1FAE5;strokeColor=#059669;fontStyle=1;'},
        {'id': 'e1', 'value': '', 'edge': True, 'source': 'start', 'target': 'dec', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e2', 'value': 'PRODUCT_A', 'edge': True, 'source': 'dec', 'target': 'varA', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
        {'id': 'e3', 'value': 'PRODUCT_B', 'edge': True, 'source': 'dec', 'target': 'varB', 'style': 'edgeStyle=orthogonalEdgeStyle;'},
    ]
    write_drawio(DIAG_DIR / '04_arbol_decisiones_variantes.drawio', 'Arbol_Decisiones_SPL', cells)


# ==============================================================================
# CAPTURAS DE PANTALLA REALES DESDE NAVEGADOR HEADLESS CONTRA SERVIDOR DJANGO
# ==============================================================================
def find_browser():
    candidates = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def wait_port(port, timeout=15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) == 0:
                return True
        time.sleep(0.25)
    return False


def capture_live_screenshots():
    browser = find_browser()
    if not browser:
        raise RuntimeError('No se encontró Microsoft Edge ni Google Chrome para capturar vistas.')

    scenarios = [
        {
            'port': 8111,
            'env': {'SPL_VARIANT': 'PRODUCT_A'},
            'pages': [
                ('/', CAP_DIR / '01_sesion2_vista_sin_reportes.png'),
                ('/', CAP_DIR / '03_sesion3_variante_A_sistema_basico.png'),
            ],
        },
        {
            'port': 8112,
            'env': {'SPL_VARIANT': 'PRODUCT_A', 'SPL_ENABLE_REPORTS': 'True'},
            'pages': [
                ('/', CAP_DIR / '02_sesion2_vista_con_reportes.png'),
            ],
        },
        {
            'port': 8113,
            'env': {'SPL_VARIANT': 'PRODUCT_B'},
            'pages': [
                ('/', CAP_DIR / '04_sesion3_variante_B_sistema_completo.png'),
                ('/reports/', CAP_DIR / '05_sesion3_vista_reportes_y_pdf.png'),
                ('/notifications/', CAP_DIR / '06_sesion3_vista_notificaciones.png'),
                ('/spl-architecture/', CAP_DIR / '07_sesion1_arquitectura_en_vivo.png'),
            ],
            'download_samples': True,
        },
    ]

    for sc in scenarios:
        env = os.environ.copy()
        env.pop('SPL_VARIANT', None)
        env.pop('SPL_ENABLE_REPORTS', None)
        env.pop('SPL_ENABLE_NOTIFICATIONS', None)
        env.update(sc['env'])

        port = sc['port']
        proc = subprocess.Popen(
            [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'],
            cwd=str(BASE_DIR),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            if not wait_port(port):
                raise RuntimeError(f'El servidor Django no respondió en el puerto {port}')

            for route, out_png in sc['pages']:
                url = f'http://127.0.0.1:{port}{route}'
                cmd = [
                    browser,
                    '--headless=new',
                    '--disable-gpu',
                    '--no-sandbox',
                    '--hide-scrollbars',
                    '--window-size=1440,1080',
                    f'--screenshot={out_png}',
                    url,
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f'  [Captura] {out_png.name} <- {url}')

            if sc.get('download_samples'):
                pdf_out = ANEXO_DIR / 'reporte_proyectos_spl_ejemplo.pdf'
                csv_out = ANEXO_DIR / 'reporte_proyectos_spl_ejemplo.csv'
                urllib.request.urlretrieve(f'http://127.0.0.1:{port}/reports/export/pdf/', pdf_out)
                urllib.request.urlretrieve(f'http://127.0.0.1:{port}/reports/export/csv/', csv_out)
                print(f'  [Anexo] {pdf_out.name} y {csv_out.name} descargados desde /reports/')
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


# ==============================================================================
# MANUAL PDF OFICIAL: "LÍNEA DE PRODUCTOS BASADA EN DJANGO" (SESIÓN 4)
# ==============================================================================
def build_manual_pdf():
    pdf_path = OUT_DIR / 'Manual_Linea_de_Productos_basada_en_Django.pdf'
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title='Manual: Línea de productos basada en Django',
    )

    styles = getSampleStyleSheet()
    s_title = ParagraphStyle('SPLTitle', parent=styles['Title'], fontSize=22, leading=26, textColor=colors.HexColor('#0B2545'), alignment=TA_CENTER, spaceAfter=10)
    s_sub = ParagraphStyle('SPLSub', parent=styles['Heading2'], fontSize=13, leading=16, textColor=colors.HexColor('#F58220'), alignment=TA_CENTER, spaceAfter=18)
    s_h1 = ParagraphStyle('SPLH1', parent=styles['Heading1'], fontSize=15, leading=19, textColor=colors.HexColor('#0B2545'), spaceBefore=14, spaceAfter=8)
    s_h2 = ParagraphStyle('SPLH2', parent=styles['Heading2'], fontSize=12, leading=15, textColor=colors.HexColor('#134074'), spaceBefore=10, spaceAfter=6)
    s_body = ParagraphStyle('SPLBody', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=7)
    s_code = ParagraphStyle('SPLCode', parent=styles['Code'], fontName='Courier', fontSize=8.5, leading=11, backColor=colors.HexColor('#F1F5F9'), borderPadding=8, leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=8)
    s_cap = ParagraphStyle('SPLCap', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor('#475569'), alignment=TA_CENTER, spaceAfter=12)

    story = []

    # Portada
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph('UNIVERSIDAD ESTATAL DE MILAGRO (UNEMI)', s_h1))
    story.append(Paragraph('FACULTAD DE CIENCIAS E INGENIERÍAS · CARRERA DE SOFTWARE', s_sub))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph('Manual Técnico: “Línea de productos basada en Django”', s_title))
    story.append(Paragraph('Guía de Práctica N° 4 — Gestión de la Configuración de Software [GESCONSOF]', s_sub))
    story.append(Spacer(1, 0.25 * inch))

    meta_table = Table(
        [
            ['Asignatura', 'Gestión de la Configuración de Software [GESCONSOF]'],
            ['Docente de la Asignatura', 'Ing. Lissett Margarita Arévalo Gamboa'],
            ['Docente de la Práctica', 'Ing. Omar Andrés Oviedo Armijos'],
            ['Integrantes del Grupo', 'Francisco Steven Arias Pérez\nDarly Douglas Farías Mendoza'],
            ['Proyecto Base', 'Sistema Académico Modular de Proyectos (Django 6.1)'],
            ['Variantes Implementadas', 'PRODUCT_A (Sistema Básico) | PRODUCT_B (Sistema Completo)'],
        ],
        colWidths=[2.2 * inch, 4.6 * inch],
    )
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0B2545')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.6, colors.HexColor('#CBD5E1')),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # Sección 1
    story.append(Paragraph('1. Visión General de la Línea de Productos de Software (SPL)', s_h1))
    story.append(Paragraph(
        'Una Línea de Productos de Software (SPL) permite construir múltiples variantes de un mismo sistema compartiendo '
        'una base común de activos reutilizables (Core Assets) y gestionando las diferencias mediante puntos de variación '
        'controlados. En este proyecto Django, el sistema académico separa los módulos transversales reutilizables '
        '(<b>accounts</b> y <b>file_manager</b>) y el núcleo obligatorio (<b>core</b>) de las funcionalidades opcionales '
        '(<b>reports</b> y <b>notifications</b>).',
        s_body,
    ))
    story.append(RLImage(str(DIAG_DIR / '02_arquitectura_funcional.png'), width=6.6 * inch, height=4.05 * inch))
    story.append(Paragraph('Figura 1. Arquitectura funcional y separación entre componentes reutilizables y opcionales.', s_cap))

    # Sección 2
    story.append(Paragraph('2. Instrucciones para Activar y Desactivar Características', s_h1))
    story.append(Paragraph('El control de variabilidad se centraliza en tres puntos coordinados del proyecto:', s_body))
    story.append(Paragraph('Paso A: Definir el perfil de producto en <b>config_product.py</b>', s_h2))
    story.append(Preformatted(
        "# config_product.py\n"
        "PRODUCT_A = {\n"
        "    'ENABLE_REPORTS': False,\n"
        "    'ENABLE_NOTIFICATIONS': False,\n"
        "}\n"
        "PRODUCT_B = {\n"
        "    'ENABLE_REPORTS': True,\n"
        "    'ENABLE_NOTIFICATIONS': True,\n"
        "}",
        s_code,
    ))
    story.append(Paragraph('Paso B: Seleccionar la variante activa mediante variable de entorno o DEFAULT_VARIANT', s_h2))
    story.append(Preformatted(
        "# Ejecutar Variante A (Sistema Básico)\n"
        "set SPL_VARIANT=PRODUCT_A\n"
        "venv\\Scripts\\python.exe manage.py runserver 8001\n\n"
        "# Ejecutar Variante B (Sistema Completo)\n"
        "set SPL_VARIANT=PRODUCT_B\n"
        "venv\\Scripts\\python.exe manage.py runserver 8002",
        s_code,
    ))
    story.append(Paragraph('Paso C: Comportamiento automático en settings.py, urls.py y views.py', s_h2))
    story.append(Paragraph(
        'Al arrancar Django, <b>spl_project/settings.py</b> carga <i>ACTIVE_CONFIG</i> y asigna <i>ENABLE_REPORTS</i> y '
        '<i>ENABLE_NOTIFICATIONS</i>, agregando únicamente las apps activas a <i>INSTALLED_APPS</i>. A continuación, '
        '<b>spl_project/urls.py</b> ejecuta <i>include()</i> de forma condicional:',
        s_body,
    ))
    story.append(Preformatted(
        "if settings.ENABLE_REPORTS:\n"
        "    urlpatterns.append(path('reports/', include('reports.urls')))\n\n"
        "if settings.ENABLE_NOTIFICATIONS:\n"
        "    urlpatterns.append(path('notifications/', include('notifications.urls')))",
        s_code,
    ))
    story.append(PageBreak())

    # Sección 3
    story.append(Paragraph('3. Recomendaciones para Reutilizar Apps entre Proyectos Django', s_h1))
    recs = [
        '<b>1. Desacoplamiento de modelos:</b> Evite llaves foráneas directas desde apps reutilizables (como <i>file_manager</i> o <i>accounts</i>) hacia modelos de negocio específicos (<i>core.AcademicProject</i>). Utilice identificadores genéricos (<i>reference_tag</i>) o <i>AUTH_USER_MODEL</i>.',
        '<b>2. Espacios de nombres en rutas (app_name):</b> Defina siempre <i>app_name = "nombre_app"</i> dentro de <i>urls.py</i> en cada aplicación para evitar colisiones al usar <i>include()</i> en nuevos proyectos.',
        '<b>3. Plantillas encapsuladas:</b> Almacene las plantillas dentro de <i>&lt;app&gt;/templates/&lt;app&gt;/</i> y extienda un layout mínimo configurable, evitando depender de variables exclusivas de un solo proyecto.',
        '<b>4. Banderas de configuración con valores por defecto seguros:</b> Lea banderas opcionales con <i>getattr(settings, "ENABLE_REPORTS", False)</i> para que una app pueda integrarse sin romper configuraciones existentes.',
        '<b>5. Empaquetado como librería interna (Modelo RiSE):</b> Cuando una app alcance madurez (ej. <i>accounts</i> o <i>file_manager</i>), empaquétela con <i>pyproject.toml</i> para instalarla vía <i>pip</i> en múltiples sistemas de la organización.',
    ]
    for r in recs:
        story.append(Paragraph(r, s_body))

    # Sección 4
    story.append(PageBreak())
    story.append(Paragraph('4. Modelo de Características y Matriz de Variantes', s_h1))
    story.append(RLImage(str(DIAG_DIR / '03_modelo_caracteristicas_spl.png'), width=6.6 * inch, height=4.05 * inch))
    story.append(Paragraph('Figura 2. Modelo de Características SPL (FODA) con activos obligatorios y opcionales.', s_cap))
    story.append(RLImage(str(DIAG_DIR / '04_arbol_decisiones_variantes.png'), width=6.6 * inch, height=4.05 * inch))
    story.append(Paragraph('Figura 3. Árbol de decisiones para derivar Variante A y Variante B.', s_cap))
    story.append(PageBreak())

    story.append(Paragraph('Tabla Comparativa de Variantes y Configuración', s_h2))
    s_th = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.white)
    s_td = ParagraphStyle('TD', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#0F172A'))
    variant_table = Table(
        [
            [Paragraph('Característica / Módulo', s_th), Paragraph('Clasificación SPL', s_th), Paragraph('Variante A (PRODUCT_A)', s_th), Paragraph('Variante B (PRODUCT_B)', s_th)],
            [Paragraph('<b>core</b> (Proyectos y Tablero)', s_td), Paragraph('Obligatoria (Núcleo)', s_td), Paragraph('Activo (HTTP 200)', s_td), Paragraph('Activo (HTTP 200)', s_td)],
            [Paragraph('<b>accounts</b> (Usuarios y Roles)', s_td), Paragraph('Obligatoria (Reutilizable)', s_td), Paragraph('Activo (HTTP 200)', s_td), Paragraph('Activo (HTTP 200)', s_td)],
            [Paragraph('<b>file_manager</b> (Archivos)', s_td), Paragraph('Obligatoria (Reutilizable)', s_td), Paragraph('Activo (HTTP 200)', s_td), Paragraph('Activo (HTTP 200)', s_td)],
            [Paragraph('<b>reports</b> (Exportar PDF/CSV)', s_td), Paragraph('Opcional (ENABLE_REPORTS)', s_td), Paragraph('Desactivado (HTTP 404)', s_td), Paragraph('Activo (HTTP 200)', s_td)],
            [Paragraph('<b>notifications</b> (Alertas)', s_td), Paragraph('Opcional (ENABLE_NOTIFICATIONS)', s_td), Paragraph('Desactivado (HTTP 404)', s_td), Paragraph('Activo (HTTP 200)', s_td)],
        ],
        colWidths=[1.85 * inch, 2.05 * inch, 1.55 * inch, 1.55 * inch],
    )
    variant_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B2545')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(variant_table)
    story.append(Spacer(1, 14))

    # Sección 5: Evidencias
    story.append(Paragraph('5. Evidencias Comparativas de Interfaz por Variante', s_h1))
    story.append(Paragraph(
        'Las siguientes capturas fueron obtenidas directamente de la ejecución real del servidor Django bajo ambas variantes:',
        s_body,
    ))
    story.append(RLImage(str(CAP_DIR / '03_sesion3_variante_A_sistema_basico.png'), width=6.4 * inch, height=4.6 * inch))
    story.append(Paragraph('Figura 4. Variante A (PRODUCT_A): Sistema básico sin botones ni rutas de reportes/notificaciones.', s_cap))
    story.append(PageBreak())
    story.append(RLImage(str(CAP_DIR / '04_sesion3_variante_B_sistema_completo.png'), width=6.4 * inch, height=4.6 * inch))
    story.append(Paragraph('Figura 5. Variante B (PRODUCT_B): Sistema completo con módulos opcionales habilitados.', s_cap))

    doc.build(story)
    print(f'  [Manual PDF] {pdf_path.name} generado exitosamente.')


if __name__ == '__main__':
    print('1. Generando diagramas (.png y .drawio)...')
    build_diagram_01_folders()
    build_diagram_02_functional()
    build_diagram_03_feature_model()
    build_diagram_04_decision_tree()

    print('2. Capturando vistas reales desde navegador headless...')
    capture_live_screenshots()

    print('3. Construyendo Manual PDF oficial...')
    build_manual_pdf()

    print('Todos los entregables gráficos y PDF fueron generados.')
