# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt5.QtWidgets import (QDialog, QFrame, QLabel, QMainWindow, 
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt


class DeleteDialog(QDialog):
    def __init__(self, 
                    parent: QMainWindow = None, 
                    message: str = "", 
                    delete_func=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.message = message
        self.delete_func = delete_func

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame(self)
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #1E0A30, stop:0.5 #3D1A5E, stop:1 #121212
            ); 
            border: none; 
            border-radius: 5px;
        """)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout()
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)
        self.frame.setLayout(self.frame_layout_2)

        self.message_lbl = QLabel()
        self.message_lbl.setText(self.message)
        self.message_lbl.setFixedHeight(80)
        self.message_lbl.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_2.addWidget(self.message_lbl)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_3.setSpacing(10)
        self.frame_layout_3.addStretch()

        self.delete_btn = QPushButton()
        self.delete_btn.clicked.connect(self.close_window)
        self.delete_btn.setText("Удалить")
        self.delete_btn.setFixedSize(80, 40)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #D6B4FF; 
                border: none; 
                border-radius: 5px;
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QPushButton::hover {
                background: #E8E0F0;
            }
        """)
        self.frame_layout_3.addWidget(self.delete_btn)

        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.accept)
        self.cancel_btn.setText("Отмена")
        self.cancel_btn.setFixedSize(80, 40)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #D6B4FF; 
                border: none; 
                border-radius: 5px;
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QPushButton::hover {
                background: #E8E0F0;
            }
        """)
        self.frame_layout_3.addWidget(self.cancel_btn)

        self.frame_layout_2.addLayout(self.frame_layout_3)
    
    def close_window(self):
        self.delete_func()
        self.accept()
