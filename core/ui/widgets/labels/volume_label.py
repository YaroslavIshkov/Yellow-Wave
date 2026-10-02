# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Метка процента громкости.

Отображает текущую громкость в виде '50%'. Синхронизирует
с VolumeSlider - при движении бегунка текст обновляется через
прямой доступ к self.percent_lbl.setText().
"""

from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt
from core.ui.style.styles import STATE_LABEL

if TYPE_CHECKING:
    from core.ui.widgets.menu.main_menu import SoundEngine


class VolumeLabel(QWidget):
    """Метка c процентом громкости. 
    
    Фиксированный размер 50x32, текст по центру.
    Обновляется из VolumeSlider.update_level() - сама метка
    не подписана на сигналы Qt.

    Attributes:
        sound: Ссылка на SoundEngine (источник текущей громкости).
        percent_lbl: QLabel с текстом '50%'.
    """

    def __init__(self, sound: Optional["SoundEngine"] = None):
        """Создаёт метку с текущим значением громкости.
        
        Args:
            sound: Экземпляр SoundEngine - оттуда берётся начальное
                значение volume.
        """
        super().__init__()
        self.sound = sound

        initial = 0 if self.sound.muted else self.sound.volume
        self.percent_lbl = QLabel()
        self.percent_lbl.setText(str(initial) + " %")
        self.percent_lbl.setAlignment(Qt.AlignCenter)
        self.percent_lbl.setStyleSheet(STATE_LABEL)
        self.percent_lbl.setFixedSize(50, 32)
