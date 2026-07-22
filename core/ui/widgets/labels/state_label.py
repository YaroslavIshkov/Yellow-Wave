# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt


class StateLabel(QWidget):
    """Метка отображающая текущий режим воспроизведения треков. Протестировано: 09.07.2026"""
    def __init__(self):
        super().__init__()
        self.state_label = QLabel()
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setStyleSheet("""
            QLabel {
                background: #D9D9D9; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 15px;
            }
        """)
        self.state_label.setFixedSize(100, 32)

    def set_text(self, text: str):
        self.state_label.setText(text)