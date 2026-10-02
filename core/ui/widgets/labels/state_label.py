# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Метка текущего режима воспроизведения.

Отображает один из четырёх режимов: 'Порядок', 'Повтор', 'Повтор трека',
'Перемешать'. Обновляется из RepeatButton при каждом переключении режима
(клавиша R или клик).
"""

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt
from core.ui.style.styles import STATE_LABEL


class StateLabel(QWidget):
    """Метка для отображения режима воспроизведения.
    
    Фиксированный размер 100x32, текст по центру.
    Содержимое меняется извне через set_text() - сама метка не знает
    про режимы, просто показывает переданную строку.

    Attributes:
        state_label: QLabel с текстом текущего режима.
    """

    def __init__(self):
        """Создаёт пустую метку состояния."""
        super().__init__()
        self.state_label = QLabel()
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setStyleSheet(STATE_LABEL)
        self.state_label.setFixedSize(100, 32)

    def set_text(self, text: str):
        """Устанавливает текст метки.
        
        Args:
            text: Название режима ('Порядок', 'Повтор' и т.д.).
        """
        self.state_label.setText(text)