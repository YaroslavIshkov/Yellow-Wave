# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Кнопки перемотки трека на +-5 секунд.

Две кнопки-стрелки по бокам от Stop. Не переключают треки, 
а двигают позицию внутри текущего: назад на 5 секунд и вперёд на 5 секунд.
Делегируют действие в MainPlayMenu._hotkey_seek() - тот же метод,
что вызывается при нажатии стрелок на клавиатуре.
"""

from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont
from core.ui.style.styles import PLAYER_BUTTON

if TYPE_CHECKING:
    from core.ui.widgets.menu.main_menu import MainPlayMenu


class SeekButton(QWidget):
    """Пара кнопок для перемотки трека на +-5 секунд.
    
    Содержит две независимые кнопки:
    - back_seek_button (<<<) - перемотка назад на 5 секунд
    - next_seek_button (>>>) - перемотка вперёд на 5 секунд

    Логика перемотки - в MainPlayMenu._hotkey_seek() (используется
    совместно с горячими клавишами <- / ->).

    Attributes:
        menu: Ссылка на MainPlayMenu.
        icon_font: Шрифт для иконок (Font Awesome 6 Free, 16pt).
    """

    def __init__(self, font: str, menu: Optional["MainPlayMenu"] = None):
        """Создаёт обе кнопки перемотки.
        
        Args:
            font: Семейство шрифта для иконок (Font Awesome).
            menu: Ссылка на MainPlayMenu - оттуда вызывается _hotkey_seek()
                при клике.
        """
        super().__init__()
        self.menu = menu
        self.icon_font = QFont(font, 16)

        self.back_seek_button = QPushButton()
        self.back_seek_button.clicked.connect(self.seek_back)
        self.back_seek_button.setFont(self.icon_font)
        # \uf04a - иконка 'шаг назад'
        self.back_seek_button.setText("\uf04a")
        self.back_seek_button.setStyleSheet(PLAYER_BUTTON)
        self.back_seek_button.setFixedSize(32, 32)
        self.back_seek_button.setToolTip("Перемотка назад 5 сек. (\u2190)")

        self.next_seek_button = QPushButton()
        self.next_seek_button.clicked.connect(self.seek_next)
        self.next_seek_button.setFont(self.icon_font)
        # \uf04e - иконка 'шаг вперёд'
        self.next_seek_button.setText("\uf04e")
        self.next_seek_button.setStyleSheet(PLAYER_BUTTON)
        self.next_seek_button.setFixedSize(32, 32)
        self.next_seek_button.setToolTip("Перемотка вперёд 5 сек. (\u2192)")

    def seek_back(self):
        """Перематывает трек на 5 секунд назад.

        Делегирует в MainPlayMenu._hotkey_seek(-5) - тот же путь, 
        что при нажатии <- на клавиатуре.
        """
        self.menu.seek(-5)

    def seek_next(self):
        """Перематывает трек на 5 секунд вперёд.
        
        Делегирует в MainPlayMenu._hotkey_seek(+5) - тот же путь, 
        что при нажатии -> на клавиатуре.
        """
        self.menu.seek(+5)
