import sys
import os
import asyncio
import threading
import json
import requests as _requests

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QCheckBox, QListWidget, QListWidgetItem,
    QLineEdit, QStackedWidget, QFrame, QAbstractItemView,
)
from PyQt6.QtCore import (
    Qt, QSize, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal,
    QThread, pyqtSignal as Signal
)
from PyQt6.QtGui import (
    QPixmap, QColor, QFont, QPainter, QBrush, QPen, QLinearGradient, QDrag
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import Database


# ─── Palette ────────────────────────────────────────────────────────────────
BG         = "#0A0A0F"
SURFACE    = "#111118"
SURFACE2   = "#18181F"
BORDER     = "#2A2A35"
ACCENT     = "#C89B3C"
ACCENT2    = "#785A28"
TEXT       = "#E8E0D0"
TEXT_DIM   = "#6B6475"
TEXT_MUTED = "#3D3848"
DANGER     = "#C0392B"
SUCCESS    = "#27AE60"

STYLESHEET = f"""
* {{
    font-family: 'Segoe UI', sans-serif;
    color: {TEXT};
    background: transparent;
}}

QMainWindow {{
    background: {BG};
}}

QWidget#central, QWidget#sidebar, QWidget#header {{
    background: {BG};
}}

QListWidget, QLineEdit, QSpinBox {{
    background: {SURFACE2};
}}

/* ── Sidebar ── */
#sidebar {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
    min-width: 180px;
    max-width: 180px;
}}

#sidebarBtn {{
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 12px 20px;
    font-size: 13px;
    color: {TEXT_DIM};
    border-radius: 0px;
}}

#sidebarBtn:hover {{
    background: {SURFACE2};
    color: {TEXT};
}}

#sidebarBtn[active=true] {{
    border-left: 3px solid {ACCENT};
    color: {ACCENT};
    background: {SURFACE2};
}}

/* ── Header ── */
#header {{
    background: {SURFACE};
    border-bottom: 1px solid {BORDER};
    padding: 0px 24px;
    min-height: 72px;
    max-height: 72px;
}}

#playerName {{
    font-size: 17px;
    font-weight: 700;
    color: {TEXT};
    letter-spacing: 0.5px;
}}

#playerLevel {{
    font-size: 12px;
    color: {TEXT_DIM};
}}

#eloLabel {{
    font-size: 12px;
    font-weight: 600;
    color: {ACCENT};
    background: {SURFACE2};
    border: 1px solid {ACCENT2};
    border-radius: 4px;
    padding: 2px 8px;
}}

/* ── Start button ── */
#startBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT2}, stop:1 {ACCENT});
    border: none;
    border-radius: 6px;
    color: #0A0A0F;
    font-size: 13px;
    font-weight: 700;
    padding: 10px 28px;
    letter-spacing: 1px;
}}

#startBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT}, stop:1 #E8B84B);
}}

#startBtn[running=true] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B1A1A, stop:1 {DANGER});
    border: none;
    color: #FFFFFF;
}}

#startBtn[running=true]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {DANGER}, stop:1 #E74C3C);
}}

/* ── Checkboxes ── */
QCheckBox {{
    spacing: 8px;
    font-size: 12px;
    color: {TEXT_DIM};
}}

QCheckBox:disabled {{
    color: {TEXT_MUTED};
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid {BORDER};
    background: {SURFACE2};
}}

QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
    image: none;
}}

QCheckBox::indicator:disabled {{
    background: {TEXT_MUTED};
    border-color: {TEXT_MUTED};
}}

QCheckBox::indicator:checked:disabled {{
    background: {ACCENT2};
    border-color: {ACCENT2};
}}

/* ── Content area ── */
#contentTitle {{
    font-size: 20px;
    font-weight: 700;
    color: {TEXT};
    letter-spacing: 0.3px;
}}

#sectionLabel {{
    font-size: 10px;
    font-weight: 700;
    color: {TEXT_DIM};
    letter-spacing: 2px;
}}

/* ── Search ── */
#searchInput {{
    background: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT};
}}

#searchInput:focus {{
    border-color: {ACCENT};
    outline: none;
}}

/* ── Lists ── */
#pickList, #searchList {{
    background: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 6px;
    outline: none;
}}

#pickList::item, #searchList::item {{
    padding: 0px;
    border-bottom: 1px solid {BORDER};
    border-radius: 0px;
}}

#pickList::item:selected, #searchList::item:selected {{
    background: {SURFACE};
    border-left: 2px solid {ACCENT};
}}

#pickList::item:hover, #searchList::item:hover {{
    background: {SURFACE};
}}

/* drag placeholder */
#pickList::item:selected:active {{
    background: rgba(200,155,60,0.15);
    border-left: 2px solid {ACCENT};
}}

/* ── Divider ── */
#divider {{
    background: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}

/* ── Lane tabs ── */
#laneTab {{
    background: transparent;
    border: 1px solid {BORDER};
    border-radius: 4px;
    color: {TEXT_DIM};
    font-size: 11px;
    font-weight: 600;
    padding: 5px 12px;
    letter-spacing: 1px;
}}

#laneTab:hover {{
    border-color: {ACCENT2};
    color: {TEXT};
}}

#laneTab[active=true] {{
    background: {ACCENT2};
    border-color: {ACCENT};
    color: {ACCENT};
}}

/* ── Remove button ── */
#removeBtn {{
    background: transparent;
    border: none;
    color: {TEXT_MUTED};
    font-size: 14px;
    padding: 0px 4px;
    border-radius: 3px;
}}

#removeBtn:hover {{
    color: {DANGER};
    background: rgba(192, 57, 43, 0.1);
}}

/* ── Spin box ── */
QSpinBox {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 3px;
    color: {ACCENT};
    font-size: 11px;
    font-weight: 700;
    padding: 1px 4px;
    max-width: 40px;
    min-width: 40px;
}}

QSpinBox::up-button, QSpinBox::down-button {{
    width: 0px;
    border: none;
}}

/* ── Add button ── */
#addBtn {{
    background: rgba(200, 155, 60, 0.1);
    border: 1px solid {ACCENT2};
    border-radius: 4px;
    color: {ACCENT};
    font-size: 11px;
    font-weight: 600;
    padding: 5px 12px;
    letter-spacing: 0.5px;
}}

#addBtn:hover {{
    background: rgba(200, 155, 60, 0.2);
    border-color: {ACCENT};
}}

QScrollBar:vertical {{
    background: {SURFACE};
    width: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── Toggle switch (home page) ── */
#toggleLabel {{
    font-size: 12px;
    color: {TEXT_DIM};
    letter-spacing: 0.5px;
}}

#toggleLabel[active=true] {{
    color: {TEXT};
}}
"""

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "champ_icons")

MOCK_PLAYER = {
    "name": "tauba",
    "tag": "ivern",
    "level": 247,
    "elo": "Gold II",
}

def _load_champions_from_db() -> list[dict]:
    try:
        db = Database.get_instance()
        rows = db.get_all_champions()
        # nome_id é o filename sem extensão, já tratado pelo populate_db
        return [{"id": row["id"], "name": row["nome"], "nome_id": row["nome_id"]} for row in rows]
    except Exception as e:
        print(f"Erro ao carregar campeões do banco: {e}")
        return []

ALL_CHAMPIONS = _load_champions_from_db()
# Lookup rápido: champion_id -> nome_id  (usado no fetcher de splash)
CHAMP_ID_TO_NOME_ID: dict[int, str] = {c["id"]: c["nome_id"] for c in ALL_CHAMPIONS}

LANES = ["TOP", "JG", "MID", "ADC", "SUPP"]
LANE_PRIORITY_BASE = {"TOP": 0, "JG": 100, "MID": 200, "ADC": 300, "SUPP": 400}

ELOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "elos")

# Mapeamento tier da API (inglês) → nome do arquivo em assets/elos/
TIER_TO_FILE = {
    "IRON": "Iron", "BRONZE": "Bronze", "SILVER": "Silver",
    "GOLD": "Gold", "PLATINUM": "Platinum", "EMERALD": "Emerald",
    "DIAMOND": "Diamond", "MASTER": "Master",
    "GRANDMASTER": "GrandMaster", "CHALLENGER": "Challenger",
}
# Texto exibido na UI
TIER_DISPLAY = {
    "IRON": "Ferro", "BRONZE": "Bronze", "SILVER": "Prata",
    "GOLD": "Ouro", "PLATINUM": "Platina", "EMERALD": "Esmeralda",
    "DIAMOND": "Diamante", "MASTER": "Mestre",
    "GRANDMASTER": "Grão-Mestre", "CHALLENGER": "Challenger",
    "UNRANKED": "Sem Ranque",
}


# ─── LCU background fetch (coroutine, usa connection existente) ──────────────
async def fetch_profile_background(connection) -> QPixmap:
    """
    Recebe uma connection já aberta pelo PreGameManager e retorna
    o QPixmap do splash art de fundo do perfil. Retorna QPixmap() vazio em falha.
    """
    try:
        resp = await connection.request(
            "get", "/lol-summoner/v1/current-summoner/summoner-profile"
        )
        profile = await resp.json()
        skin_id = profile.get("backgroundSkinId", 0)
        if not skin_id:
            return QPixmap()

        champ_id = skin_id // 1000
        skin_num  = skin_id % 1000

        nome_id = CHAMP_ID_TO_NOME_ID.get(champ_id)
        if not nome_id:
            return QPixmap()

        version = Database.get_instance().get_latest_version()
        if not version:
            return QPixmap()

        img_url = (
            f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/"
            f"{nome_id}_{skin_num}.jpg"
        )
        img_r = _requests.get(img_url, timeout=10)
        px = QPixmap()
        if img_r.status_code == 200:
            px.loadFromData(img_r.content)
        return px

    except Exception as e:
        print(f"fetch_profile_background error: {e}")
        return QPixmap()


async def fetch_player_info(connection) -> dict:
    try:
        resp = await connection.request("get", "/lol-summoner/v1/current-summoner")
        summoner = await resp.json()
        print(f"[LCU] Summoner: {summoner.get('displayName')} | level {summoner.get('summonerLevel')}")

        resp2 = await connection.request("get", "/lol-ranked/v1/current-ranked-stats")
        ranked = await resp2.json()
        solo = ranked.get("queueMap", {}).get("RANKED_SOLO_5x5", {})
        tier = solo.get("tier") or "UNRANKED"
        division = "" if tier in ("MASTER", "GRANDMASTER", "CHALLENGER", "UNRANKED") else (solo.get("division") or "")
        print(f"[LCU] Rank SoloQ: {tier} {division}")

        icon_id = summoner.get("profileIconId", 0)
        version = Database.get_instance().get_latest_version()
        icon_px = QPixmap()
        if version and icon_id:
            url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/{icon_id}.png"
            r = _requests.get(url, timeout=10)
            if r.status_code == 200:
                icon_px.loadFromData(r.content)
                print(f"[LCU] Ícone de perfil carregado (id={icon_id})")

        return {
            "name":     summoner.get("displayName") or summoner.get("gameName", "?"),
            "tag":      summoner.get("tagLine", ""),
            "level":    summoner.get("summonerLevel", 0),
            "tier":     tier,
            "division": division,
            "icon_px":  icon_px,
        }
    except Exception as e:
        print(f"[LCU] fetch_player_info error: {e}")
        return {}


# ─── Champion icon loader ────────────────────────────────────────────────────
def make_champ_icon(nome_id: str, nome: str, size: int = 32) -> QPixmap:
    """Carrega ícone usando nome_id do DB (já tratado). Fallback com inicial."""
    path = os.path.join(ASSETS_DIR, nome_id + ".png")
    if os.path.exists(path):
        px = QPixmap(path)
        if not px.isNull():
            return px.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)
    # Fallback: quadrado dourado com inicial
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(ACCENT2)))
    p.setPen(QPen(QColor(ACCENT), 1))
    p.drawRoundedRect(0, 0, size, size, 4, 4)
    p.setPen(QPen(QColor(ACCENT)))
    p.setFont(QFont("Segoe UI", size // 3, QFont.Weight.Bold))
    p.drawText(0, 0, size, size, Qt.AlignmentFlag.AlignCenter, nome[0].upper())
    p.end()
    return px


def make_avatar_icon(inicial: str, size: int = 48) -> QPixmap:
    """Ícone circular com inicial do jogador."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(ACCENT2)))
    p.setPen(QPen(QColor(ACCENT), 2))
    p.drawEllipse(1, 1, size - 2, size - 2)
    p.setPen(QPen(QColor(ACCENT)))
    p.setFont(QFont("Segoe UI", size // 3, QFont.Weight.Bold))
    p.drawText(0, 0, size, size, Qt.AlignmentFlag.AlignCenter, inicial.upper())
    p.end()
    return px


def make_circular_icon(source: QPixmap, size: int, border_color: str = ACCENT) -> QPixmap:
    scaled = source.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation)
    cx = (scaled.width()  - size) // 2
    cy = (scaled.height() - size) // 2
    cropped = scaled.copy(cx, cy, size, size)

    result = QPixmap(size, size)
    result.fill(Qt.GlobalColor.transparent)
    p = QPainter(result)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(cropped))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(0, 0, size, size)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(border_color), 2))
    p.drawEllipse(1, 1, size - 2, size - 2)
    p.end()
    return result


def load_elo_emblem(tier: str, size: int = 52) -> QPixmap | None:
    filename = TIER_TO_FILE.get(tier.upper())
    if not filename:
        return None
    path = os.path.join(ELOS_DIR, filename + ".png")
    if not os.path.exists(path):
        print(f"[UI] Emblema não encontrado: {path}")
        return None
    px = QPixmap(path)
    return px.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)


# ─── Toggle switch widget ────────────────────────────────────────────────────
class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, label: str, checked: bool = False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self._label = label
        self._anim_x = 3.0
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # The pill track — drawn in paintEvent of a sub-widget
        self._track = _TrackWidget(self)
        self._track.setFixedSize(44, 24)
        layout.addWidget(self._track)

        lbl = QLabel(label)
        lbl.setObjectName("toggleLabel")
        lbl.setProperty("active", str(checked).lower())
        self._lbl = lbl
        layout.addWidget(lbl)
        layout.addStretch()

        self._anim = QPropertyAnimation(self._track, b"knob_x")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._track.knob_x = 3.0 if not checked else 21.0

    def mousePressEvent(self, e):
        self._checked = not self._checked
        target = 21.0 if self._checked else 3.0
        self._anim.stop()
        self._anim.setStartValue(float(self._track.knob_x))
        self._anim.setEndValue(target)
        self._anim.start()
        self._lbl.setProperty("active", str(self._checked).lower())
        self._lbl.style().unpolish(self._lbl)
        self._lbl.style().polish(self._lbl)
        self._track.update()
        self.toggled.emit(self._checked)

    def isChecked(self):
        return self._checked

    def setChecked(self, v: bool):
        if v != self._checked:
            self.mousePressEvent(None)


class _TrackWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._knob_x = 3.0

    def get_knob_x(self): return self._knob_x
    def set_knob_x(self, v):
        self._knob_x = v
        self.update()
    knob_x = property(get_knob_x, set_knob_x)

    # expose as Qt property for QPropertyAnimation
    from PyQt6.QtCore import pyqtProperty
    knob_x = pyqtProperty(float, get_knob_x, set_knob_x)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        checked = self._knob_x > 10
        track_color = QColor(ACCENT2) if checked else QColor(BORDER)
        p.setBrush(QBrush(track_color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 4, 44, 16, 8, 8)
        knob_color = QColor(ACCENT) if checked else QColor(TEXT_DIM)
        p.setBrush(QBrush(knob_color))
        p.drawEllipse(int(self._knob_x), 2, 20, 20)
        p.end()


# ─── Home page ───────────────────────────────────────────────────────────────
class HomePage(QWidget):
    """Aba INÍCIO: fundo splash, avatar grande, info do jogador, toggles."""

    # Sinais para sincronizar com o header
    queue_toggled  = pyqtSignal(bool)
    ban_toggled    = pyqtSignal(bool)
    pick_toggled   = pyqtSignal(bool)
    hover_toggled  = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_pixmap: QPixmap | None = None
        self._build()
        # Fundo padrão até o PreGameManager entregar o splash via set_background()
        self._draw_gradient_bg()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Background label (fills entire widget)
        self._bg_label = QLabel(self)
        self._bg_label.setScaledContents(False)
        self._bg_label.setGeometry(0, 0, self.width(), self.height())
        self._bg_label.lower()

        # Overlay content (centrado)
        overlay = QWidget(self)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(40, 60, 40, 40)
        overlay_layout.setSpacing(0)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Avatar grande
        self._avatar_lbl = QLabel()
        self._avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._avatar_lbl.setPixmap(make_avatar_icon(MOCK_PLAYER["name"][0], 96))
        self._avatar_lbl.setFixedSize(96, 96)
        overlay_layout.addWidget(self._avatar_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        overlay_layout.addSpacing(18)

        # Nome
        self._name_lbl = QLabel("Conectando...")
        self._name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_lbl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self._name_lbl.setStyleSheet(f"color: {TEXT}; letter-spacing: 1px;")
        overlay_layout.addWidget(self._name_lbl)
        overlay_layout.addSpacing(6)

        # Level + Elo em linha
        info_row = QHBoxLayout()
        info_row.setSpacing(10)
        info_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._level_lbl = QLabel("")
        self._level_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        info_row.addWidget(self._level_lbl)

        self._sep_lbl = QLabel("·")
        self._sep_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px;")
        self._sep_lbl.hide()
        info_row.addWidget(self._sep_lbl)

        self._elo_img_lbl = QLabel()
        self._elo_img_lbl.setFixedSize(52, 52)
        self._elo_img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._elo_img_lbl.hide()
        info_row.addWidget(self._elo_img_lbl)

        self._elo_text_lbl = QLabel("")
        self._elo_text_lbl.setStyleSheet(
            f"color: {ACCENT}; font-size: 13px; font-weight: 700;"
            f"background: {SURFACE2}; border: 1px solid {ACCENT2};"
            f"border-radius: 4px; padding: 2px 10px;"
        )
        self._elo_text_lbl.hide()
        info_row.addWidget(self._elo_text_lbl)

        overlay_layout.addLayout(info_row)
        overlay_layout.addSpacing(36)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {BORDER}; background: {BORDER}; max-height:1px;")
        overlay_layout.addWidget(div)
        overlay_layout.addSpacing(28)

        # Toggles
        toggles_title = QLabel("AUTOMAÇÃO")
        toggles_title.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; font-weight: 700; letter-spacing: 2px;"
        )
        toggles_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(toggles_title)
        overlay_layout.addSpacing(16)

        toggles_container = QWidget()
        toggles_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        tc_layout = QVBoxLayout(toggles_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(8)

        self._toggle_queue = ToggleSwitch("Auto Queue")
        self._toggle_ban   = ToggleSwitch("Auto Ban")
        self._toggle_pick  = ToggleSwitch("Auto Pick")
        self._toggle_hover = ToggleSwitch("Auto Hover")

        self._toggle_queue.toggled.connect(self.queue_toggled)
        self._toggle_ban.toggled.connect(self.ban_toggled)
        self._toggle_pick.toggled.connect(self.pick_toggled)
        self._toggle_hover.toggled.connect(self.hover_toggled)

        for t in [self._toggle_queue, self._toggle_ban, self._toggle_pick, self._toggle_hover]:
            tc_layout.addWidget(t)

        # Centraliza o bloco de toggles
        toggles_row = QHBoxLayout()
        toggles_row.addStretch()
        toggles_row.addWidget(toggles_container)
        toggles_row.addStretch()
        overlay_layout.addLayout(toggles_row)

        overlay_layout.addStretch()

        # Posiciona overlay sobre o bg
        self._overlay = overlay
        self._overlay.raise_()

    def set_player(self, player: dict):
        name = player.get("name", "")
        tag  = player.get("tag", "")
        self._name_lbl.setText(f"{name} #{tag}" if tag else name)

        level = player.get("level", 0)
        self._level_lbl.setText(f"Nível {level}")

        tier     = player.get("tier", "UNRANKED")
        division = player.get("division", "")
        tier_txt = TIER_DISPLAY.get(tier, tier)
        elo_str  = f"{tier_txt} {division}".strip()
        self._elo_text_lbl.setText(elo_str)
        self._elo_text_lbl.show()
        self._sep_lbl.show()

        emblem = load_elo_emblem(tier)
        if emblem:
            self._elo_img_lbl.setPixmap(emblem)
            self._elo_img_lbl.show()
        else:
            self._elo_img_lbl.hide()

        icon_px = player.get("icon_px")
        if icon_px and not icon_px.isNull():
            self._avatar_lbl.setPixmap(make_circular_icon(icon_px, 96))
        print(f"[UI] HomePage atualizada: {elo_str} | Nível {level}")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._bg_label.setGeometry(0, 0, self.width(), self.height())
        self._overlay.setGeometry(0, 0, self.width(), self.height())
        if self._bg_pixmap and not self._bg_pixmap.isNull():
            self._apply_background(self._bg_pixmap)

    def set_background(self, px: QPixmap):
        """Chamado pelo PreGameManager quando o LCU conecta."""
        if px.isNull():
            self._draw_gradient_bg()
        else:
            self._bg_pixmap = px
            self._apply_background(px)

    def _apply_background(self, px: QPixmap):
        """Escala, centraliza e aplica vinheta ao splash art."""
        w, h = self.width() or 800, self.height() or 600
        scaled = px.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation)
        # Crop ao centro
        x = (scaled.width()  - w) // 2
        y = (scaled.height() - h) // 2
        cropped = scaled.copy(x, y, w, h)

        # Vinheta escura nas bordas + gradiente inferior
        result = QPixmap(w, h)
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.drawPixmap(0, 0, cropped)

        # Sobreposição escura semi-transparente
        painter.fillRect(0, 0, w, h, QColor(10, 10, 15, 160))

        # Gradiente forte na parte inferior
        grad = QLinearGradient(0, h * 0.4, 0, h)
        grad.setColorAt(0, QColor(10, 10, 15, 0))
        grad.setColorAt(1, QColor(10, 10, 15, 230))
        painter.fillRect(0, 0, w, h, grad)
        painter.end()

        self._bg_label.setPixmap(result)

    def _draw_gradient_bg(self):
        """Fallback: gradiente bonito quando não há LCU."""
        w, h = max(self.width(), 400), max(self.height(), 300)
        px = QPixmap(w, h)
        px.fill(QColor(BG))
        p = QPainter(px)
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0, QColor(20, 18, 10))
        grad.setColorAt(0.5, QColor(15, 13, 25))
        grad.setColorAt(1, QColor(10, 10, 15))
        p.fillRect(0, 0, w, h, grad)
        # decorativo: círculo dourado difuso
        p.setOpacity(0.06)
        p.setBrush(QBrush(QColor(ACCENT)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(w // 2 - 200, -100, 500, 500)
        p.end()
        self._bg_label.setPixmap(px)
        self._bg_pixmap = px


# ─── Drag-aware QListWidget ──────────────────────────────────────────────────
class SearchList(QListWidget):
    """Lista de busca com suporte a arrastar campeões para a pick list."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.setDragEnabled(True)
        self.setSpacing(1)

    def mimeData(self, items):
        mime = super().mimeData(items)
        if items:
            champ = items[0].data(Qt.ItemDataRole.UserRole)
            if champ:
                mime.setText(json.dumps({
                    "type": "champion",
                    "id": champ["id"],
                    "name": champ["name"],
                    "nome_id": champ["nome_id"],
                }))
        return mime

    def startDrag(self, supported_actions):
        item = self.currentItem()
        if not item:
            super().startDrag(supported_actions)
            return
        champ = item.data(Qt.ItemDataRole.UserRole)
        if not champ:
            super().startDrag(supported_actions)
            return

        # Monta pixmap do drag com ícone + nome
        w, h = 220, 44
        px = QPixmap(w, h)
        px.fill(QColor(SURFACE2))
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # borda sutil
        p.setPen(QPen(QColor(BORDER)))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(0, 0, w - 1, h - 1, 4, 4)
        # ícone
        icon = make_champ_icon(champ["nome_id"], champ["name"], 30)
        p.drawPixmap(8, 7, icon)
        # nome
        p.setPen(QPen(QColor(TEXT)))
        p.setFont(QFont("Segoe UI", 11))
        p.drawText(46, 0, w - 50, h, Qt.AlignmentFlag.AlignVCenter, champ["name"])
        p.end()

        mime = self.mimeData([item])
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(px)
        drag.setHotSpot(QPoint(px.width() // 2, px.height() // 2))
        drag.exec(supported_actions)


class DraggablePickList(QListWidget):
    order_changed    = pyqtSignal()
    champion_dropped = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSpacing(1)

    @staticmethod
    def _parse_champ_drop(event) -> dict | None:
        if not event.mimeData().hasText():
            return None
        try:
            data = json.loads(event.mimeData().text())
            return data if data.get("type") == "champion" else None
        except Exception:
            return None

    def dragEnterEvent(self, e):
        if self._parse_champ_drop(e):
            e.accept()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if self._parse_champ_drop(e):
            e.accept()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self, event):
        data = self._parse_champ_drop(event)
        if data:
            self.champion_dropped.emit(data)
            event.accept()
            return
        super().dropEvent(event)
        self.order_changed.emit()


# ─── Champion row widget ─────────────────────────────────────────────────────
class ChampionRow(QWidget):
    removed = pyqtSignal(int)

    def __init__(self, champ_id: int, name: str, nome_id: str, priority: int, parent=None):
        super().__init__(parent)
        self.champ_id = champ_id
        self.name = name
        self.nome_id = nome_id
        self._priority = priority
        self.setFixedHeight(44)
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(10)

        # Número de prioridade
        prio_lbl = QLabel(str(self._priority))
        prio_lbl.setFixedWidth(18)
        prio_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prio_lbl.setStyleSheet(
            f"color: {ACCENT}; font-size: 11px; font-weight: 700;"
        )
        self._prio_lbl = prio_lbl
        layout.addWidget(prio_lbl)

        # Drag handle
        drag_lbl = QLabel("⠿")
        drag_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px;")
        drag_lbl.setCursor(Qt.CursorShape.OpenHandCursor)
        layout.addWidget(drag_lbl)

        # Ícone — tamanho fixo, sem corte
        icon_container = QWidget()
        icon_container.setFixedSize(32, 32)
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(make_champ_icon(self.nome_id, self.name, 30))
        icon_lbl.setFixedSize(30, 30)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        layout.addWidget(icon_container)

        name_lbl = QLabel(self.name)
        name_lbl.setFont(QFont("Segoe UI", 12))
        name_lbl.setStyleSheet(f"color: {TEXT};")
        layout.addWidget(name_lbl, stretch=1)

        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("removeBtn")
        remove_btn.setFixedSize(22, 22)
        remove_btn.clicked.connect(lambda: self.removed.emit(self.champ_id))
        layout.addWidget(remove_btn)

    def set_priority(self, p: int):
        self._priority = p
        self._prio_lbl.setText(str(p))


# ─── Pick / Ban panel ────────────────────────────────────────────────────────
class PickBanPanel(QWidget):
    def __init__(self, mode: str = "picks", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.db = Database.get_instance()
        self.current_lane = "MID"
        # {lane_key: [(champ_id, nome, nome_id), ...]}  — ordem = prioridade
        self.picks: dict[str, list] = {l: [] for l in LANES}
        if mode == "bans":
            self.picks = {"bans": []}
        if mode == "picks":
            self.added_ids: dict[str, set[int]] = {l: set() for l in LANES}
        else:
            self.added_ids: dict[str, set[int]] = {"bans": set()}
        self._build()
        self._load_from_db()
        self._refresh_pick_list()
        self._populate_search()

    def _lane_key(self):
        return self.current_lane if self.mode == "picks" else "bans"

    def _load_from_db(self):
        if self.mode == "picks":
            for lane in LANES:
                for row in self.db.get_picks_by_lane(lane):
                    champ = self.db.get_champion_by_id(row["champion_id"])
                    if champ:
                        self.picks[lane].append((champ["id"], champ["nome"], champ["nome_id"]))
                        self.added_ids[lane].add(champ["id"])
            total = sum(len(v) for v in self.picks.values())
            print(f"[DB] Picks carregados: {total} no total | " +
                  " | ".join(f"{l}={len(self.picks[l])}" for l in LANES))
        else:
            for row in self.db.get_bans():
                champ = self.db.get_champion_by_id(row["champion_id"])
                if champ:
                    self.picks["bans"].append((champ["id"], champ["nome"], champ["nome_id"]))
                    self.added_ids["bans"].add(champ["id"])
            print(f"[DB] Bans carregados: {len(self.picks['bans'])} | " +
                  ", ".join(n for _, n, _ in self.picks["bans"]))

    def _save_lane_to_db(self, key: str):
        if self.mode == "picks":
            for row in self.db.get_picks_by_lane(key):
                self.db.delete_pick(row["champion_id"])
            base = LANE_PRIORITY_BASE[key]
            for i, entry in enumerate(self.picks[key]):
                self.db.insert_pick(entry[0], base + i + 1, key)
            names = [entry[1] for entry in self.picks[key]]
            print(f"[DB] Picks {key} salvos ({len(names)}): {names}")
        else:
            for row in self.db.get_bans():
                self.db.delete_ban(row["champion_id"])
            for i, entry in enumerate(self.picks["bans"]):
                self.db.insert_ban(entry[0], i + 1)
            names = [entry[1] for entry in self.picks["bans"]]
            print(f"[DB] Bans salvos ({len(names)}): {names}")

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title_label = QLabel("PICKS" if self.mode == "picks" else "BANS")
        title_label.setObjectName("contentTitle")
        root.addWidget(title_label)

        if self.mode == "picks":
            lane_row = QHBoxLayout()
            lane_row.setSpacing(6)
            self.lane_btns: dict[str, QPushButton] = {}
            for lane in LANES:
                btn = QPushButton(lane)
                btn.setObjectName("laneTab")
                btn.setProperty("active", lane == self.current_lane)
                btn.clicked.connect(lambda _, l=lane: self._switch_lane(l))
                lane_row.addWidget(btn)
                self.lane_btns[lane] = btn
            lane_row.addStretch()
            root.addLayout(lane_row)

        cols = QHBoxLayout()
        cols.setSpacing(20)

        # ── Esquerda: lista atual ──
        left = QVBoxLayout()
        left.setSpacing(10)

        sec_lbl = QLabel("LISTA ATUAL")
        sec_lbl.setObjectName("sectionLabel")
        left.addWidget(sec_lbl)

        self.pick_list = DraggablePickList()
        self.pick_list.setObjectName("pickList")
        self.pick_list.order_changed.connect(self._on_drag_reorder)
        left.addWidget(self.pick_list, stretch=1)

        cols.addLayout(left, stretch=1)

        # ── Direita: busca ──
        right = QVBoxLayout()
        right.setSpacing(10)

        sec_lbl2 = QLabel("ADICIONAR CAMPEÃO")
        sec_lbl2.setObjectName("sectionLabel")
        right.addWidget(sec_lbl2)

        self.search = QLineEdit()
        self.search.setObjectName("searchInput")
        self.search.setPlaceholderText("Buscar campeão...")
        self.search.textChanged.connect(self._filter_search)
        right.addWidget(self.search)

        self.search_list = SearchList()
        self.search_list.setObjectName("searchList")
        self._populate_search()
        right.addWidget(self.search_list, stretch=1)

        add_btn = QPushButton("+ ADICIONAR")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self._add_selected)
        right.addWidget(add_btn)

        self.pick_list.champion_dropped.connect(self._add_from_drop)

        cols.addLayout(right, stretch=1)
        root.addLayout(cols, stretch=1)

    def _populate_search(self, filter_text: str = ""):
        key = self._lane_key()
        self.search_list.clear()
        for champ in sorted(ALL_CHAMPIONS, key=lambda c: c["name"]):
            if champ["id"] in self.added_ids[key]:
                continue
            if filter_text and filter_text.lower() not in champ["name"].lower():
                continue
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, champ)
            item.setSizeHint(QSize(0, 40))
            self.search_list.addItem(item)

            row_w = QWidget()
            row_w.setFixedHeight(40)
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(10, 0, 10, 0)
            row_l.setSpacing(10)

            ico = QLabel()
            ico.setPixmap(make_champ_icon(champ["nome_id"], champ["name"], 28))
            ico.setFixedSize(28, 28)
            ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row_l.addWidget(ico)

            name_lbl = QLabel(champ["name"])
            name_lbl.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
            row_l.addWidget(name_lbl)
            row_l.addStretch()
            self.search_list.setItemWidget(item, row_w)

    def _filter_search(self, text: str):
        self._populate_search(text)

    def _switch_lane(self, lane: str):
        self.current_lane = lane
        for l, btn in self.lane_btns.items():
            btn.setProperty("active", l == lane)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._refresh_pick_list()
        self._populate_search(self.search.text())

    def _on_drag_reorder(self):
        key = self._lane_key()
        new_order = []
        for i in range(self.pick_list.count()):
            item = self.pick_list.item(i)
            cid = item.data(Qt.ItemDataRole.UserRole)
            entry = next(((n, nid) for c, n, nid in self.picks.get(key, []) if c == cid), ("", ""))
            new_order.append((cid, entry[0], entry[1]))
        self.picks[key] = new_order
        print(f"[DB] Reordenação {key}: {[e[1] for e in new_order]}")
        self._save_lane_to_db(key)
        # Atualiza apenas os números sem recriar tudo
        for i in range(self.pick_list.count()):
            item = self.pick_list.item(i)
            widget = self.pick_list.itemWidget(item)
            if isinstance(widget, ChampionRow):
                widget.set_priority(i + 1)

    def _refresh_pick_list(self):
        self.pick_list.clear()
        key = self._lane_key()
        for idx, (champ_id, name, nome_id) in enumerate(self.picks.get(key, [])):
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 44))
            item.setData(Qt.ItemDataRole.UserRole, champ_id)
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled |
                Qt.ItemFlag.ItemIsSelectable |
                Qt.ItemFlag.ItemIsDragEnabled
            )
            self.pick_list.addItem(item)
            row = ChampionRow(champ_id, name, nome_id, idx + 1)
            row.removed.connect(self._remove_champ)
            self.pick_list.setItemWidget(item, row)

    def _add_selected(self):
        sel = self.search_list.currentItem()
        if not sel:
            return
        champ = sel.data(Qt.ItemDataRole.UserRole)
        key = self._lane_key()
        max_count = 20 if self.mode == "picks" else 5
        current = self.picks.get(key, [])
        if len(current) >= max_count:
            return
        current.append((champ["id"], champ["name"], champ["nome_id"]))
        self.picks[key] = current
        self.added_ids[key].add(champ["id"])
        print(f"[DB] Adicionado → {self.mode.upper()} | {key} | {champ['name']} (id={champ['id']}) | prioridade {len(current)}")
        self._save_lane_to_db(key)
        self._refresh_pick_list()
        self._populate_search(self.search.text())

    def _add_from_drop(self, data: dict):
        key = self._lane_key()
        if data["id"] in self.added_ids[key]:
            return
        max_count = 20 if self.mode == "picks" else 5
        current = self.picks.get(key, [])
        if len(current) >= max_count:
            return
        current.append((data["id"], data["name"], data["nome_id"]))
        self.picks[key] = current
        self.added_ids[key].add(data["id"])
        print(f"[DB] Adicionado (drag) → {self.mode.upper()} | {key} | {data['name']} (id={data['id']}) | prioridade {len(current)}")
        self._save_lane_to_db(key)
        self._refresh_pick_list()
        self._populate_search(self.search.text())

    def _remove_champ(self, champ_id: int):
        key = self._lane_key()
        removed = next((n for cid, n, _ in self.picks.get(key, []) if cid == champ_id), str(champ_id))
        self.picks[key] = [(cid, n, nid) for cid, n, nid in self.picks.get(key, []) if cid != champ_id]
        self.added_ids[key].discard(champ_id)
        print(f"[DB] Removido → {self.mode.upper()} | {key} | {removed} (id={champ_id})")
        self._save_lane_to_db(key)
        self._refresh_pick_list()
        self._populate_search(self.search.text())


# ─── DB update thread ────────────────────────────────────────────────────────
class _DbUpdateThread(QThread):
    done = pyqtSignal()

    def run(self):
        print("[DB] Verificando versão e atualizando banco...")
        try:
            from populate_db import update_db
            update_db()
            print("[DB] Banco atualizado com sucesso.")
        except Exception as e:
            print(f"[DB] Erro ao atualizar banco: {e}")
        self.done.emit()


# ─── Main Window ─────────────────────────────────────────────────────────────
class LolBotWindow(QMainWindow):
    _bg_ready     = pyqtSignal(QPixmap)
    _player_ready = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LoL Bot")
        self.setMinimumSize(1000, 680)
        self.is_running = False
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        self.header = QWidget()
        self.header.setObjectName("header")
        self.header.setFixedHeight(72)
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(24, 0, 24, 0)
        h_layout.setSpacing(16)

        self._hdr_avatar = QLabel()
        self._hdr_avatar.setPixmap(make_avatar_icon("?", 44))
        self._hdr_avatar.setFixedSize(44, 44)
        h_layout.addWidget(self._hdr_avatar)

        player_info = QVBoxLayout()
        player_info.setSpacing(2)
        self._hdr_name = QLabel("Conectando...")
        self._hdr_name.setObjectName("playerName")
        self._hdr_level = QLabel("")
        self._hdr_level.setObjectName("playerLevel")
        player_info.addWidget(self._hdr_name)
        player_info.addWidget(self._hdr_level)
        h_layout.addLayout(player_info)

        self._hdr_elo = QLabel()
        self._hdr_elo.setFixedSize(36, 36)
        self._hdr_elo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hdr_elo.hide()
        h_layout.addWidget(self._hdr_elo)

        h_layout.addStretch()

        checks_layout = QHBoxLayout()
        checks_layout.setSpacing(18)
        self.cb_queue  = QCheckBox("Auto Queue")
        self.cb_ban    = QCheckBox("Auto Ban")
        self.cb_pick   = QCheckBox("Auto Pick")
        self.cb_hover  = QCheckBox("Auto Hover")
        for cb in [self.cb_queue, self.cb_ban, self.cb_pick, self.cb_hover]:
            checks_layout.addWidget(cb)
        h_layout.addLayout(checks_layout)

        h_layout.addSpacing(20)

        self.start_btn = QPushButton("INICIAR")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedHeight(38)
        self.start_btn.clicked.connect(self._toggle_running)
        h_layout.addWidget(self.start_btn)

        root.addWidget(self.header)

        # ── Body ──
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(160)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 16, 0, 16)
        sb_layout.setSpacing(2)

        self.sidebar_btns: list[QPushButton] = []
        # INÍCIO é índice 0, PICKS=1, BANS=2
        pages = ["INÍCIO", "PICKS", "BANS"]
        for i, label in enumerate(pages):
            btn = QPushButton(label)
            btn.setObjectName("sidebarBtn")
            btn.setProperty("active", i == 0)
            btn.clicked.connect(lambda _, idx=i: self._switch_page(idx))
            sb_layout.addWidget(btn)
            self.sidebar_btns.append(btn)

        sb_layout.addStretch()
        body.addWidget(sidebar)

        # pages
        self.stack = QStackedWidget()
        self.home_panel  = HomePage()
        self.picks_panel = PickBanPanel(mode="picks")
        self.bans_panel  = PickBanPanel(mode="bans")
        self.stack.addWidget(self.home_panel)   # 0
        self.stack.addWidget(self.picks_panel)  # 1
        self.stack.addWidget(self.bans_panel)   # 2
        body.addWidget(self.stack, stretch=1)

        root.addLayout(body, stretch=1)

        # Conecta toggles da HomePage com checkboxes do header
        self.home_panel.queue_toggled.connect(self.cb_queue.setChecked)
        self.home_panel.ban_toggled.connect(self.cb_ban.setChecked)
        self.home_panel.pick_toggled.connect(self.cb_pick.setChecked)
        self.home_panel.hover_toggled.connect(self.cb_hover.setChecked)

        # Começa na aba INÍCIO → esconde header
        self._switch_page(0)

        self._bg_ready.connect(self.home_panel.set_background)
        self._player_ready.connect(self._on_player_ready)

        from pregamemanager import PreGameManager
        self.manager = PreGameManager()

        @self.manager.connector.ready
        async def _on_lcu_ready(connection):
            print("[LCU] Conectado — buscando perfil e background...")
            results = await asyncio.gather(
                fetch_profile_background(connection),
                fetch_player_info(connection),
                return_exceptions=True,
            )
            px = results[0] if not isinstance(results[0], Exception) else QPixmap()
            player = results[1] if not isinstance(results[1], Exception) else {}
            if isinstance(results[0], Exception):
                print(f"[LCU] Erro ao buscar background: {results[0]}")
            if isinstance(results[1], Exception):
                print(f"[LCU] Erro ao buscar perfil: {results[1]}")
            self._bg_ready.emit(px)
            if player:
                self._player_ready.emit(player)

        # Salva preferências no DB (não aplica ao manager — só Iniciar faz isso)
        _db = Database.get_instance()
        self.cb_queue.toggled.connect(lambda v: _db.set_setting("auto_queue", "1" if v else "0"))
        self.cb_ban.toggled.connect(  lambda v: _db.set_setting("auto_ban",   "1" if v else "0"))
        self.cb_pick.toggled.connect( lambda v: _db.set_setting("auto_pick",  "1" if v else "0"))
        self.cb_hover.toggled.connect(lambda v: _db.set_setting("auto_hover", "1" if v else "0"))

        # Carrega estado salvo (propaga via toggle → checkbox para manter sincronia visual)
        for toggle, key in [
            (self.home_panel._toggle_queue, "auto_queue"),
            (self.home_panel._toggle_ban,   "auto_ban"),
            (self.home_panel._toggle_pick,  "auto_pick"),
            (self.home_panel._toggle_hover, "auto_hover"),
        ]:
            if _db.get_setting(key, "0") == "1":
                toggle.setChecked(True)

        self.manager.setup_auto_accept()
        self.manager.setup_champion_select()

        self._db_thread = _DbUpdateThread()
        self._db_thread.done.connect(self._on_db_updated)
        self._db_thread.start()

    def _on_db_updated(self):
        global ALL_CHAMPIONS, CHAMP_ID_TO_NOME_ID
        ALL_CHAMPIONS = _load_champions_from_db()
        CHAMP_ID_TO_NOME_ID = {c["id"]: c["nome_id"] for c in ALL_CHAMPIONS}
        print(f"[DB] {len(ALL_CHAMPIONS)} campeões disponíveis após atualização.")
        for panel in [self.picks_panel, self.bans_panel]:
            if panel.mode == "picks":
                panel.picks = {l: [] for l in LANES}
                panel.added_ids = {l: set() for l in LANES}
            else:
                panel.picks = {"bans": []}
                panel.added_ids = {"bans": set()}
            panel._load_from_db()
            panel._refresh_pick_list()
            panel._populate_search()

    def _on_player_ready(self, player: dict):
        # HomePage
        self.home_panel.set_player(player)

        # Header
        name = player.get("name", "")
        tag  = player.get("tag", "")
        self._hdr_name.setText(f"{name} #{tag}" if tag else name)
        self._hdr_level.setText(f"Nível {player.get('level', '')}")

        tier = player.get("tier", "UNRANKED")
        emblem = load_elo_emblem(tier, size=36)
        if emblem:
            self._hdr_elo.setPixmap(emblem)
            self._hdr_elo.show()
        else:
            self._hdr_elo.hide()

        icon_px = player.get("icon_px")
        if icon_px and not icon_px.isNull():
            self._hdr_avatar.setPixmap(make_circular_icon(icon_px, 44))

    def _switch_page(self, idx: int):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.sidebar_btns):
            btn.setProperty("active", i == idx)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        # Header visível apenas fora do INÍCIO
        self.header.setVisible(idx != 0)

    def _toggle_running(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.manager.auto_queue = self.cb_queue.isChecked()
            self.manager.auto_ban   = self.cb_ban.isChecked()
            self.manager.auto_pick  = self.cb_pick.isChecked()
            self.manager.auto_hover = self.cb_hover.isChecked()
            print(f"[AUTO] INICIADO | queue={self.manager.auto_queue} | ban={self.manager.auto_ban} | pick={self.manager.auto_pick} | hover={self.manager.auto_hover}")
            self.start_btn.setText("PARAR")
            self.start_btn.setProperty("running", True)
            for cb in [self.cb_queue, self.cb_ban, self.cb_pick, self.cb_hover]:
                cb.setEnabled(False)
        else:
            self.manager.auto_queue = False
            self.manager.auto_ban   = False
            self.manager.auto_pick  = False
            self.manager.auto_hover = False
            print("[AUTO] PARADO | todos os autos desligados")
            self.start_btn.setText("INICIAR")
            self.start_btn.setProperty("running", False)
            for cb in [self.cb_queue, self.cb_ban, self.cb_pick, self.cb_hover]:
                cb.setEnabled(True)
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)


# ─── Entry point ─────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    win = LolBotWindow()
    win.show()
    threading.Thread(target=win.manager.connector.start, daemon=True).start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()