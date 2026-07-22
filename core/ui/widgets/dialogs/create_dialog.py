# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt5.QtWidgets import (QMainWindow, QDialog, QFrame, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QLabel, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt


class CreateDialog(QDialog):
    def __init__(self, parent: QMainWindow = None, create_func=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.create_func = create_func

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame(self)
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1E0A30, stop:0.5 #3D1A5E, stop:1 #121212
                );
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout()
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)
        self.frame.setLayout(self.frame_layout_2)

        self.title_1 = QLabel()
        self.title_1.setText("Название:")
        self.title_1.setFixedHeight(40)
        self.title_1.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_2.addWidget(self.title_1)

        self.entry_1 = QLineEdit()
        self.entry_1.textChanged.connect(self.check_characters)
        self.entry_1.setPlaceholderText("Например: Pop")
        self.entry_1.setFixedWidth(350)
        self.entry_1.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF; 
                border: 3px solid; 
                border-color: #D6B4FF; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QLineEdit::hover {
                border-color: #E8D0F0;
            }
        """)
        self.frame_layout_2.addWidget(self.entry_1)

        self.title_2 = QLabel()
        self.title_2.setText("Путь к файлу:")
        self.title_2.setFixedHeight(40)
        self.title_2.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_2.addWidget(self.title_2)

        self.entry_2 = QLineEdit()
        self.entry_2.setPlaceholderText("Например: pop-icon.png")
        self.entry_2.setFixedWidth(350)
        self.entry_2.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF; 
                border: 3px solid; 
                border-color: #D6B4FF; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QLineEdit::hover {
                border-color: #E8D0F0;
            }
        """)
        self.frame_layout_2.addWidget(self.entry_2)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_3.setSpacing(10)
        self.frame_layout_3.addStretch()

        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(self.close_window)
        self.next_btn.setText("Далее")
        self.next_btn.setEnabled(False)
        self.next_btn.setFixedSize(80, 40)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: #D6B4FF; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QPushButton::hover {
                background: #E8D0F0;
            }
        """)
        self.frame_layout_3.addWidget(self.next_btn)

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
                background: #E8D0F0;
            }
        """)
        self.frame_layout_3.addWidget(self.cancel_btn)

        self.frame_layout_2.addLayout(self.frame_layout_3)
    
    def close_window(self):
        name = self.entry_1.text()
        path = self.entry_2.text()
        self.create_func(name, path)
        self.accept()

    def check_characters(self):
        enabled = True if len(self.entry_1.text()) > 0 else False
        self.next_btn.setEnabled(enabled)
