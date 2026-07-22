# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QFrame, QLabel, QHBoxLayout, 
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon


class AppIcon:
    def __init__(self, path: str):
        self.path = path

    def icon(self, w: int, h: int):
        return QPixmap(self.path).scaled(
            w, h, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )


class ButtonIcon:
    def __init__(self, path: str):
        self.path = path
    
    def icon(self, w: int, h: int):
        return QIcon(
            QPixmap(self.path).scaled(
                w, h, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
        )


class AppWindowHeader(QWidget):
    def __init__(self, main: Optional[QApplication] = None):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main = main

        self.icons = Path(__file__).resolve().parents[4]
        self.app_icon = self.icons / "icon.ico"
        self.btn_icon = self.icons / "close.ico"
        self.app_name = "Yellow Wave Music Player (RU)"

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet("""
            QFrame {
                background: transparent; 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QHBoxLayout()
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(self.frame_layout_2)

        pixmap = AppIcon(str(self.app_icon)).icon(64, 64)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(QSize(64, 64))
        self.icon_label.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame_layout_2.addWidget(self.icon_label)

        self.name_label = QLabel()
        self.name_label.setText(self.app_name)
        self.name_label.setFixedHeight(40)
        self.name_label.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_2.addWidget(self.name_label)

        self.frame_layout_2.addStretch()

        btn_pixmap = ButtonIcon(str(self.btn_icon)).icon(64, 64)

        self.close_button = QPushButton()
        self.close_button.clicked.connect(self.main.quit)
        self.close_button.setIcon(btn_pixmap)
        self.close_button.setIconSize(QSize(70, 70))
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border: none; 
                border-radius: 5px;
            }

            QPushButton::hover {
                background: #423189;
            }
        """)
        self.frame_layout_2.addWidget(self.close_button)
