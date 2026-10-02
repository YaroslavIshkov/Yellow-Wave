# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Кнопка Stop.

Полностью останавливает воспроизведение (в отличие от Pause - 
сбрасывает позицию на начало). Делегирует действие в MainPlayMenu.stop().
"""

from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont
from core.ui.style.styles import PLAYER_BUTTON

if TYPE_CHECKING:
    from core.ui.widgets.menu.main_menu import MainPlayMenu


class StopButton(QWidget):
    """Кнопка полной остановки трека.
    
    В отличие от Play/Pause, Stop сбрасывает позицию на 0: следующий
    Play начнёт трек с начала, а не с места паузы.

    Attributes:
        menu: Ссылка на MainPlayMenu (там же - метод stop).
        icon_font: Шрифт для иконки (Font Awesome Free, 16pt).
    """

    def __init__(self, font: str, menu: Optional["MainPlayMenu"] = None):
        """Создаёт кнопку Stop.
        
        Args:
            font: Семейство шрифта для иконки (Font Awesome).
            menu: Ссылка на MainPlayMenu, чей метод stop() вызывается.
        """
        super().__init__()
        self.menu = menu

        self.icon_font = QFont(font, 16)
        self.stop_button = QPushButton()
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setFont(self.icon_font)
        self.stop_button.setText("\uf04d")
        self.stop_button.setStyleSheet(PLAYER_BUTTON)
        self.stop_button.setFixedSize(32, 32)
        self.stop_button.setToolTip("Стоп")

    def stop(self):
        """Делегирует остановку в MainPlayMenu.stop()."""
        self.menu.stop()
