# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Метка времени трека.

Отображает текущую позицию и общую длительность в формате 'MM:SS/MM:SS'
(например, '01:23/04:31'). Обновляется из TrackSlider при каждом тике
timer или при перетаскивании бегунка.
"""

from typing import Optional
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt
from core.ui.style.styles import DURATION_LABEL


class DurationLabel(QWidget):
    """Метка 'текущая позиция / общая длительность'.
    
    Фиксированный размер 130x50, текст по центру.
    Обновляется через прямой доступ к self.duration_lbl.setText() из
    TrackSlider (без промежуточных методов - так проще синхронизировать).

    Attributes:
        duration_lbl: QLabel, содержащая текст '00:00/00:00'.
    """

    def __init__(self):
        """Создаёт метку с начальным текстом '00:00/00:00'."""
        super().__init__()

        self.duration_lbl = QLabel("00:00/00:00", self)
        self.duration_lbl.setStyleSheet(DURATION_LABEL)
        self.duration_lbl.setFixedWidth(130)
        self.duration_lbl.setFixedHeight(50)
        self.duration_lbl.setAlignment(Qt.AlignCenter)
