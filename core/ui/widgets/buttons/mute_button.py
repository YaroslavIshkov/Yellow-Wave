# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Кнопка Mute (вкл/выкл звук).

Переключает состояние микшера между текущей громкостью и нулём.
Запоминает прежнюю громкость в last_volume, чтобы восстановить её
при повторном клике. Синхронизирует положение слайдера и метку
процентов, сохраняет состояние в QSettings.
"""

from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont
from core.ui.style.styles import PLAYER_BUTTON

if TYPE_CHECKING:
    from core.ui.widgets.menu.main_menu import SoundEngine
    from core.ui.widgets.sliders.volume_slider import VolumeSlider


class MuteButton(QWidget):
    """Кнопка управления Mute.
    
    Клик переключает is_enabled. Внутри - флаг muted у SoundEngine
    и сохранённая громкость last_volume. При включении mute слайдер
    и метка показывают 0%, при выключении - возвращается к прежнему значению.

    Attributes:
        sound: Ссылка на SoundEngine (микшер).
        slider: Ссылка на VolumeSlider (для синхронизации UI).
        is_enabled: Текущее состояние - True если mute включен.
        icon_font: Шрифт для иконки кнопки (Font Awesome).
    """

    def __init__(self, 
                    font: str, 
                    sound: Optional["SoundEngine"] = None, 
                    slider: Optional["VolumeSlider"] = None):
        """Создаёт кнопку Mute.
        
        Args:
            font: Семейство шрифта для иконки (Font Awesome 6 Free).
            sound: Экземпляр SoundEngine - источник состояния громкости.
            slider: Виджет VolumeSlider для синхронизации положения.
        """
        super().__init__()
        self.sound = sound
        self.slider = slider

        self.is_enabled = bool(self.sound.muted) if self.sound else False
        self.icon_font = QFont(font, 16)

        self.mute_button = QPushButton()
        self.mute_button.clicked.connect(self.set_button_state)
        self.mute_button.setFont(self.icon_font)
        self.mute_button.setText("\uf026" if self.is_enabled else "\uf028")
        self.mute_button.setStyleSheet(PLAYER_BUTTON)
        self.mute_button.setFixedSize(32, 32)
        self.mute_button.setToolTip("Mute (M)")

    def set_button_state(self):
        """Переключает состояние mute и обновляет иконку.
        
        Не трогает громкость напрямую - делегирует в set_volume_level.
        """
        self.is_enabled = not self.is_enabled
        if self.is_enabled:
            self.mute_button.setText("\uf026")
        else:
            self.mute_button.setText("\uf028")
        self.set_volume_level()

    def set_volume_level(self):
        """Применяет новую громкость к SoundEngine и синхронизирует UI.
        
        При включении mute: запоминает текущую громкость в last_volume
        и ставит volume=0. При выключении возвращает last_volume.
        Также двигает слайдер и сохраняет состояние в QSettings.
        """
        if self.is_enabled:
            self.sound.muted = True
            self.sound.last_volume = self.sound.volume
            self.sound.volume = 0
        else:
            self.sound.muted = False
            self.sound.volume = self.sound.last_volume
        
        self.slider.volume_sld.setSliderPosition(self.sound.volume)
        self.sound.set_volume(self.sound.volume)

        s = self.sound.app.settings
        s.setValue("muted", self.sound.muted)
        s.setValue("last_volume", self.sound.last_volume)
