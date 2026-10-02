# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Кнопка Play / Pause.

Большая круглая кнопка по центру плеера. Иконка меняется автоматически: 
Play (>), когда трек остановлен или на паузе, Pause (||), когда трек играет.
Логика воспроизведения - в SoundEngine.
"""

from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont
from core.ui.style.styles import PLAYER_BUTTON

if TYPE_CHECKING:
    from core.ui.widgets.menu.main_menu import SoundEngine


class PlayButton(QWidget):
    """Кнопка Play / Pause.

    Делегирует всю логику в SoundEngine.toggle_play(). Иконка обновляется
    отдельно через update_icon() - вызывается и при клике, и при смене трека
    (из SoundEngine), и при остановке.

    Attributes:
        sound: Ссылка на SoundEngine (микшер и состояние).
        icon_font: Шрифт для иконок (Font Awesome 6 Free, 32pt).
    """

    def __init__(self, font: str, sound: Optional["SoundEngine"] = None):
        """Создаёт кнопку Play / Pause.
        
        Args:
            font: Семейство шрифта для иконки (Font Awesome).
            sound: Экземпляр SoundEngine - источник состояния.
        """
        super().__init__()
        self.sound = sound
        self.icon_font = QFont(font, 32)

        self.play_button = QPushButton()
        self.play_button.clicked.connect(self.set_button_state)
        self.play_button.setFont(self.icon_font)
        self.play_button.setText("\uf04b")
        self.play_button.setFixedSize(64, 64)
        self.play_button.setStyleSheet(PLAYER_BUTTON)
        self.play_button.setToolTip("Play / Pause (Space)")

    def set_button_state(self):
        """Обрабатывает клик - переключает воспроизведение и иконку."""
        self.sound.toggle_play()
        self.update_icon()

    def update_icon(self):
        """Обновляет иконку в зависимости от состояния SoundEngine.
        
        Показывает Pause, если трек играет, и Play - если остановлен
        или на паузе.
        """
        if self.sound.started and not self.sound.paused:
            self.play_button.setText("\uf04c")
        else:
            self.play_button.setText("\uf04b")
