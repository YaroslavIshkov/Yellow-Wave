# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Кнопка переключения режима воспроизведения.

Циклически переключает четыре режима:
    0 - Порядок (по умолчанию, стоп после последнего трека)
    1 - Повтор всех (зацикливание плейлиста)
    2 - Повтор трека (один трек играет бесконечно)
    3 - Перемешать (случайный трек после каждого окончания)

Режим хранится в SoundEngine.mode и сохраняется в QSettings, 
чтобы восстанавливаться при следующем запуске. Кнопка меняет иконку, 
фон (ярче в активных режимах) и текст state_label.
"""

from typing import TYPE_CHECKING, Optional
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont
from core.ui.style.styles import PLAYER_BUTTON

if TYPE_CHECKING:
    from core.ui.widgets.menu.main_menu import SoundEngine, MainPlayMenu


class RepeatButton(QWidget):
    """Кнопка переключения режима воспроизведения.
    
    Один клик - следующий режим по кругу: 0 -> 1 -> 2 -> 3 -> 0.
    При каждом переходе обновляет: 
        - иконку (стрелки, repeat, shuffle)
        - фон (яркий при активном режиме, тёмный в режиме 'Порядок')
        - текст в state_label ('Порядок', 'Повтор', 'Повтор трека', 'Перемешать')
    
    Attributes:
        sound: Ссылка на SoundEngine - хранит mode и settings.
        menu: Ссылка на MainPlayMenu - даёт доступ к state_label.
        icon_font: Шрифт для иконок (Font Awesome Free, 16pt).
    """

    def __init__(self, 
                    font: str, 
                    sound: Optional["SoundEngine"] = None, 
                    menu: Optional["MainPlayMenu"] = None):
        """Создаёт кнопку переключения режима.
        
        Args:
            font: Семейство шрифта для иконки (Font Awesome).
            sound: Экземпляр SoundEngine (источник и хранилище mode).
            menu: Экземпляр MainPlayMenu (для доступа к state_label).
        """
        super().__init__()
        self.sound = sound
        self.menu = menu

        self.icon_font = QFont(font, 16)

        self.repeat_shuffle_button = QPushButton()
        self.repeat_shuffle_button.clicked.connect(self.set_mode)
        self.repeat_shuffle_button.setFont(self.icon_font)
        # Начальное состояние - 'Порядок' (mode=0, иконки нет)
        self.repeat_shuffle_button.setText("--")
        self.repeat_shuffle_button.setStyleSheet(PLAYER_BUTTON)
        self.repeat_shuffle_button.setFixedSize(32, 32)
        self.repeat_shuffle_button.setToolTip("Режим воспроизведения (R)")

    def set_mode(self):
        """Переключает режим на следующий по кругу и обновляет UI.
        
        Защита от 'уплывшего' mode: если значение вне диапазона 0-3
        (например, JSON повреждён) - сбрасывает на 0.
        Новое значение сохраняется в QSettings.
        """
        if not 0 <= self.sound.mode <= 3:
            self.sound.mode = 0
        if self.sound.mode < 3:
            self.sound.mode += 1
        else:
            self.sound.mode = 0
        self.sound.app.settings.setValue("mode", self.sound.mode)
        self.set_button_icon()
        self.set_button_bg()
        self.set_text()

    def set_button_icon(self):
        """Устанавливает иконку в зависимости от режима.
        
        Иконки:
            0 - '--' (нет иконки, стандартный режим)
            1, 2 - \\uf01e (стрелки повтора; 2 отличается цветом фона)
            3 - \\uf074 (стрелки перемешивания)
        """
        icons = {
            0: lambda: self.repeat_shuffle_button.setText("--"), 
            1: lambda: self.repeat_shuffle_button.setText("\uf01e"), 
            2: lambda: self.repeat_shuffle_button.setText("\uf01e"), 
            3: lambda: self.repeat_shuffle_button.setText("\uf074")
        }
        icons[self.sound.mode]()

    def set_button_bg(self):
        """Меняет фон в зависимости от активности режима.
        
        В режиме 'Порядок' (mode=0) - приглушённый фиолетовый, 
        в остальных - ярко акцентный.
        """
        bg = "#9B69B5" if self.sound.mode > 0 else "#6A4580"
        self.repeat_shuffle_button.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; 
                border: none; 
                border-radius: 5px; 
                color: white;
            }}
        """)
    
    def set_text(self):
        """Обновляет текст в state_label через диспетчер по mode."""
        functions = {
            0: self.standard, 
            1: self.repeat_all, 
            2: self.repeat_one, 
            3: self.shuffle
        }
        functions[self.sound.mode]()
    
    def standard(self):
        """Режим 0 - 'Порядок': треки подряд, стоп после последнего."""
        self.menu.state_label.set_text("Порядок")

    def repeat_all(self):
        """Режим 1 - 'Повтор': зацикливание всего плейлита."""
        self.menu.state_label.set_text("Повтор")

    def repeat_one(self):
        """Режим 2 - 'Повтор трека': один и тот же трек бесконечно."""
        self.menu.state_label.set_text("Повтор трека")

    def shuffle(self):
        """Режим 3 - 'Перемешать': случайный трек после окончания."""
        self.menu.state_label.set_text("Перемешать")
