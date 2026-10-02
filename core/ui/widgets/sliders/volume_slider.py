# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ползунок регулировки громкости.

Горизонтальный слайдер 0-100. При изменении положения обновляет
процентную метку и передаёт значение в SoundEngine. Если сейчас
включен mute - не трогает громкость, но запоминает last_volume
(чтобы при снятии mute восстановить именно это значение).
"""

from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QWidget, QLabel, QSlider, QSizePolicy
from PyQt5.QtCore import Qt
from core.ui.style.styles import SLIDER_VOLUME

if TYPE_CHECKING:
    from core.ui.widgets.menu.main_menu import SoundEngine


class VolumeSlider(QWidget):
    """Слайдер громкости 0-100.
    
    Синхронизирован с SoundEngine: при движении бегунка вызывает
    set_volume(), а если mute активен - только запоминает значение
    в last_volume, не применяя его к микшеру.

    Attributes:
        label: QLabel для отображения процентов ('50%').
        sound: Ссылка на SoundEngine (микшер).
    """

    def __init__(self, label: QLabel, sound: Optional["SoundEngine"] = None):
        """Создаёт слайдер громкости.
        
        Args:
            label: QLabel для обновления процентов (обычно VolumeLabel).
            sound: Экземпляр SoundEngine - источник и приёмник громкости.
        """
        super().__init__()
        self.label = label
        self.sound = sound

        # Если mute включён - показываем 0, иначе текущую громкость
        initial = 0 if self.sound.muted else self.sound.volume
        self.volume_sld = QSlider(Qt.Horizontal)
        self.volume_sld.setRange(0, 100)
        self.volume_sld.setFocusPolicy(Qt.NoFocus)
        self.volume_sld.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.volume_sld.setSliderPosition(initial)
        self.volume_sld.setFixedWidth(100)
        self.volume_sld.setToolTip("Громкость (\u2191 / \u2193)")
        self.volume_sld.setStyleSheet(SLIDER_VOLUME)

        self.volume_sld.valueChanged[int].connect(self.update_level)

    def update_level(self, value: int):
        """Обрабатывает изменение положения слайдера.
        
        Обновляет метку процентов. Если mute выключен - применяет громкость
        к микшеру, иначе только запоминает её в last_volume
        (применится при снятии mute).

        Args:
            value: Новая громкость (0-100).
        """
        self.label.setText(str(value) + " %")
        if not self.sound.muted:
            self.sound.set_volume(value)
        else:
            self.sound.last_volume = value
