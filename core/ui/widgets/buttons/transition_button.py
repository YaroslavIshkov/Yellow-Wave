# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Кнопки переключения треков (Предыдущий / Следующий).

Две кнопки-стрелки по бокам от Play. Делегируют действия в
MainPlayMenu, который в свою очередь дёргает SoundEngine.
"""

from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont
from core.ui.style.styles import PLAYER_BUTTON

if TYPE_CHECKING:
    from core.ui.widgets.menu.main_menu import MainPlayMenu


class TransitionButton(QWidget):
    """Пара кнопок для переключения треков.
    
    Содержит две независимые кнопки: 
    - previous_button (<<) - предыдущий трек
    - next_button (>>) - следующий трек

    Вся логика переключения - в SoundEngine.to_previous / to_next
    (доступны через MainPlayMenu).

    Attributes:
        menu: Ссылка на MainPlayMenu.
        icon_font: Шрифт для иконок (Font Awesome 6 Free, 16pt).
    """

    def __init__(self, font: str, menu: Optional["MainPlayMenu"] = None):
        """Создаёт обе кнопки переключения.
        
        Args:
            font: Семейство шрифта для иконок (Font Awesome).
            menu: Ссылка на MainPlayMenu - оттуда вызываются to_previous()
                и to_next().
        """
        super().__init__()
        self.menu = menu
        self.icon_font = QFont(font, 16)

        self.previous_button = QPushButton()
        self.previous_button.clicked.connect(self.to_previous)
        self.previous_button.setFont(self.icon_font)
        # \uf048 - иконка 'шаг назад'
        self.previous_button.setText("\uf048")
        self.previous_button.setStyleSheet(PLAYER_BUTTON)
        self.previous_button.setFixedSize(32, 32)
        self.previous_button.setToolTip("Предыдущий трек (Ctrl+\u2190)")

        self.next_button = QPushButton()
        self.next_button.clicked.connect(self.to_next)
        self.next_button.setFont(self.icon_font)
        # \uf051 - иконка 'шаг вперёд'
        self.next_button.setText("\uf051")
        self.next_button.setStyleSheet(PLAYER_BUTTON)
        self.next_button.setFixedSize(32, 32)
        self.next_button.setToolTip("Следующий трек (Ctrl+\u2192)")

    def to_previous(self):
        """Делегирует переход к предыдущему треку в MainPlayMenu."""
        self.menu.to_previous()

    def to_next(self):
        """Делегирует переход к следующему треку в MainPlayMenu."""
        self.menu.to_next()
