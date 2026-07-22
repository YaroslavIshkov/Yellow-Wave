# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont


class StopButton(QWidget):
    """Кнопка полной остановки воспроизведения трека. Протестировано: 09.07.2026"""
    def __init__(self, font_family: str, main):
        super().__init__()
        self.main = main
        self.icon_font = QFont(font_family, 16)
        self.stop_button = QPushButton()
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setFont(self.icon_font)
        self.stop_button.setText("\uf04d")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background: #9B69B5; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF;
            }
        """)
        self.stop_button.setFixedSize(32, 32)

    def stop(self):
        self.main.stop()