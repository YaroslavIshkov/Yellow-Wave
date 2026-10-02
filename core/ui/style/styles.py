# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional
from PyQt5.QtWidgets import QWidget

"""Общие QSS-стили для всего приложения.

Все повторяющиеся стили собраны здесь, чтобы менять их в одном месте.
Имена констант описывают назначение, а не внешний вид.
"""

# ============================================================
# ФОНЫ
# ============================================================

MAIN_GRADIENT = """
    QWidget {
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #1E0A30, stop:0.5 #3D1A5E, stop:1 #121212
        );
        border: none;
        border-radius: 5px;
    }
"""

DIALOG_FRAME = """
    QFrame {
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #1E0A30, stop:0.5 #3D1A5E, stop:1 #121212
        );
        border: none;
        border-radius: 5px;
    }
"""

TRANSPARENT_FRAME = """
    QFrame {
        background: transparent;
        border: none;
        border-radius: 5px;
    }
"""

WHITE_FRAME = """
    QFrame {
        background: white;
        border: none;
        border-radius: 5px;
    }
"""

# ============================================================
# ТЕКСТ
# ============================================================

DIALOG_LABEL = """
    QLabel {
        background: transparent;
        border: none;
        color: white;
        font-family: Segoe UI;
        font-size: 15px;
    }
"""

DARK_LABEL = """
    QLabel {
        background: transparent;
        border: none;
        color: #3D3D3D;
        font-family: Segoe UI;
        font-size: 15px;
    }
"""

INFO_LABEL = """
    QLabel {
        background: #E8D0F0;
        border: none;
        border-radius: 5px;
        color: #3D3D3D;
        font-family: Segoe UI;
        font-size: 15px;
        padding-left: 10px;
    }
"""

STATE_LABEL = """
    QLabel {
        background: #D9D9D9;
        border: none;
        border-radius: 5px;
        color: #3D3D3D;
        font-family: Segoe UI;
        font-size: 15px;
    }
"""

# ============================================================
# КНОПКИ
# ============================================================

PRIMARY_BUTTON = """
    QPushButton {
        background: #D6B4FF;
        border: none;
        border-radius: 5px;
        color: #3D3D3D;
        font-family: Segoe UI;
        font-size: 15px;
    }
    QPushButton::hover {
        background: #E8D0F0;
    }
"""

TRANSPARENT_BUTTON = """
    QPushButton {
        background: transparent;
        border: none;
        border-radius: 5px;
        color: white;
        font-family: Segoe UI;
        font-size: 15px;
    }
    QPushButton::hover {
        background: #423189;
    }
"""

TRANSPARENT_BUTTON_SMALL = """
    QPushButton {
        background: transparent;
        border-radius: 5px;
        color: white;
        font-family: Segoe UI;
        font-size: 15px;
    }
    QPushButton::hover {
        background: #423189;
    }
"""

TRANSPARENT_BUTTON_BIG = """
    QPushButton {
        background: transparent;
        border: none;
        border-radius: 5px;
        color: white;
        font-family: Segoe UI;
        font-size: 20px;
    }
    QPushButton::hover {
        background: #423189;
    }
"""

PLAYER_BUTTON = """
    QPushButton {
        background: #9B69B5;
        border: none;
        border-radius: 5px;
        color: white;
    }
"""

CLOSE_BUTTON = """
    QPushButton {
        background: transparent;
        border: none;
        border-radius: 5px;
    }
    QPushButton::hover {
        background: #423189;
    }
"""

# ============================================================
# СПИСКИ
# ============================================================

TRANSPARENT_LIST = """
    QListWidget {
        background: transparent;
        border: none;
        border-radius: 5px;
        color: white;
        font-family: Segoe UI;
        font-size: 20px; 
        outline: 0;
    }
    QListWidget::item {
        min-width: 130px;
        min-height: 30px;
        text-align: center;
        padding: 5px 12px;
        margin: 2px;
        border-radius: 5px;
        background: transparent;
    }
    QListWidget::item:hover {
        background: #423189;
        border-radius: 5px;
    }
    QListWidget::item:selected {
        background: #423189;
        border-radius: 5px;
        color: white;
    }
"""

WHITE_LIST = """
    QListWidget {
        background: #FFFFFF;
        border: none;
        border-radius: 5px;
        color: #3D3D3D;
        font-family: Segoe UI;
        font-size: 15px;
        outline: 0;
    }
    QListWidget::item {
        background: transparent;
        border-radius: 5px;
    }
    QListWidget::item:hover {
        background: #E8D0F0;
    }
    QListWidget::item:selected {
        background: #D6B4FF;
        color: #3D3D3D;
    }
"""

WHITE_LIST_BIG = """
    QListWidget {
        background: #FFFFFF;
        border: none;
        border-radius: 5px;
        color: #3D3D3D;
        font-family: Segoe UI;
        font-size: 15px; 
        outline: 0;
    }
    QListWidget::item {
        background: transparent;
        border-radius: 5px;
    }
    QListWidget::item:hover {
        background: #E8D0F0;
    }
    QListWidget::item:selected {
        background: #D6B4FF;
        color: #3D3D3D;
    }
"""

# ============================================================
# ПОЛЯ ВВОДА
# ============================================================

LINE_EDIT = """
    QLineEdit {
        background: white;
        border: 3px solid;
        border-color: #D6B4FF;
        border-radius: 5px;
        color: #3D3D3D;
        font-family: Segoe UI;
        font-size: 15px;
    }
    QLineEdit::hover {
        border-color: #E8D0F0;
    }
"""

# ============================================================
# СЛАЙДЕРЫ
# ============================================================

SLIDER_TRACK = """
    QSlider {
        background: transparent;
        border: none;
    }
    QSlider::groove:horizontal {
        background: #DCDCDC;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #9B59B6;
        width: 14px;
        height: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }
    QSlider::handle:horizontal:hover {
        background: #7D3C98;
    }
    QSlider::sub-page:horizontal {
        background: #9B59B6;
        border-radius: 3px;
    }
"""

SLIDER_VOLUME = """
    QSlider {
        background: transparent;
        border: none;
    }
    QSlider::groove:horizontal {
        background: #DCDCDC;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #9B69B5;
        width: 14px;
        height: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }
    QSlider::handle:horizontal:hover {
        background: #7D3C98;
    }
    QSlider::sub-page:horizontal {
        background: #9B69B5;
        border-radius: 3px;
    }
"""

# ============================================================
# СПЕЦИАЛЬНЫЕ СПИСКИ
# ============================================================

SELECT_LIST = """
    QListWidget {
        background: transparent; 
        border: none; 
        border-radius: 5px; 
        color: white; 
        font-family: Segoe UI; 
        font-size: 15px; 
        outline: 0;
    }
    QListWidget::item {
        min-width: 130px; 
        min-height: 30px; 
        text-align: center; 
        padding: 5px 12px; 
        margin: 2px; 
        border-radius: 5px; 
        background: transparent; 
        padding-left: 5px;
    }
    QListWidget::item:hover {
        background: #432189; 
        border-radius: 5px;
    }
    QListWidget::item:selected {
        background: #423189; 
        border-radius: 5px; 
        color: white;
    }
"""

# ============================================================
# ТЕКСТ (продолжение)
# ============================================================

TRANSPARENT_LABEL = """
    QLabel {
        background: transparent; 
        border: none; 
        border-radius: 5px;
    }
"""

DURATION_LABEL = """
    QLabel {
        background: transparent; 
        border: none; 
        color: #3D3D3D; 
        font-family: Segoe UI; 
        font-size: 20px;
    }
"""

SHADOW_MARGIN = 15

def apply_shadow(
    widget: Optional[QWidget] = None, 
    blur=30, 
    offset_x=8, 
    offset_y=8, 
    color=(155, 115, 181, 160), 
    margin=SHADOW_MARGIN) -> int:
    """Накладывает мягкую тень на виджет.

    margin - сколько места оставить вокруг виджета под тень.
    Возвращает margin, чтобы можно было использовать в layout.

    Args:
        widget: Виджет, к которому будет применена тень.
        blur: Радиус действия тени.
        x_offset: Смещение тени по x.
        y_offset: Смещение тени по y.
        color: Задаёт цвет для тени.
        margin: Отступы предотвращающие обрезание тени.
    """
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
    from PyQt5.QtGui import QColor

    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setOffset(offset_x, offset_y)
    effect.setColor(QColor(*color))
    widget.setGraphicsEffect(effect)
    return margin
