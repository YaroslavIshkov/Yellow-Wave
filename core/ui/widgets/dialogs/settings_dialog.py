# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt5.QtWidgets import (QDialog, QFrame, QLabel, QMainWindow, 
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt
from core.settings.settings_core import SettingsCore


class SettingsDialog(QDialog):
    def __init__(self, settings: SettingsCore = None, parent: QMainWindow = None):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.settings = settings

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame()
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

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel()
        self.title_label.setText("Настройки:")
        self.title_label.setFixedHeight(40)
        self.title_label.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_3.addWidget(self.title_label)

        self.close_btn = QPushButton()
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setText("Закрыть")
        self.close_btn.setFixedSize(80, 40)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QPushButton::hover {
                background: #423189;
            }
        """)
        self.frame_layout_3.addWidget(self.close_btn)

        self.frame_layout_4 = QHBoxLayout()
        self.frame_layout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_layout_4.setSpacing(60)

        self.search_label = QLabel()
        self.search_label.setText("Сканировать устройство")
        self.search_label.setFixedHeight(40)
        self.search_label.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_4.addWidget(self.search_label)

        self.search_btn = QPushButton()
        self.search_btn.clicked.connect(self.settings.search_music)
        self.search_btn.setText("Поиск")
        self.search_btn.setFixedSize(80, 40)
        self.search_btn.setStyleSheet("""
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
        self.frame_layout_4.addWidget(self.search_btn)

        self.frame_layout_5 = QHBoxLayout()
        self.frame_layout_5.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_5.setSpacing(60)

        self.label_1 = QLabel()
        self.label_1.setText("Добавить в поджанр")
        self.label_1.setFixedHeight(40)
        self.label_1.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_5.addWidget(self.label_1)

        self.button_1 = QPushButton()
        self.button_1.clicked.connect(self.settings.add_track_to_sublist)
        self.button_1.setText("Добавить")
        self.button_1.setFixedSize(80, 40)
        self.button_1.setStyleSheet("""
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
        self.frame_layout_5.addWidget(self.button_1)

        self.frame_layout_6 = QHBoxLayout()
        self.frame_layout_6.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_6.setSpacing(60)

        self.label_2 = QLabel()
        self.label_2.setText("Удалить из поджанра")
        self.label_2.setFixedHeight(40)
        self.label_2.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_6.addWidget(self.label_2)

        self.button_2 = QPushButton()
        self.button_2.clicked.connect(self.settings.delete_track_from_sublist)
        self.button_2.setText("Удалить")
        self.button_2.setFixedSize(80, 40)
        self.button_2.setStyleSheet("""
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
        self.frame_layout_6.addWidget(self.button_2)

        self.frame_layout_7 = QHBoxLayout()
        self.frame_layout_7.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_7.setSpacing(60)

        self.label_3 = QLabel()
        self.label_3.setText("Добавить поджанр")
        self.label_3.setFixedHeight(40)
        self.label_3.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_7.addWidget(self.label_3)

        self.button_3 = QPushButton()
        self.button_3.clicked.connect(self.settings.create_dialog)
        self.button_3.setText("Добавить")
        self.button_3.setFixedSize(80, 40)
        self.button_3.setStyleSheet("""
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
        self.frame_layout_7.addWidget(self.button_3)

        self.frame_layout_8 = QHBoxLayout()
        self.frame_layout_8.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_8.setSpacing(60)

        self.label_4 = QLabel()
        self.label_4.setText("Удалить поджанр")
        self.label_4.setFixedHeight(40)
        self.label_4.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_8.addWidget(self.label_4)

        self.button_4 = QPushButton()
        self.button_4.clicked.connect(self.settings.delete_dialog)
        self.button_4.setText("Удалить")
        self.button_4.setFixedSize(80, 40)
        self.button_4.setStyleSheet("""
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
        self.frame_layout_8.addWidget(self.button_4)

        self.frame_layout_9 = QHBoxLayout()
        self.frame_layout_9.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_9.setSpacing(60)

        self.label_5 = QLabel()
        self.label_5.setText("Удалить трек")
        self.label_5.setFixedHeight(40)
        self.label_5.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_9.addWidget(self.label_5)

        self.button_5 = QPushButton()
        self.button_5.clicked.connect(self.settings.delete_track_from_list)
        self.button_5.setText("Удалить")
        self.button_5.setFixedSize(80, 40)
        self.button_5.setStyleSheet("""
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
        self.frame_layout_9.addWidget(self.button_5)

        self.frame_layout_2.addLayout(self.frame_layout_3)
        self.frame_layout_2.addLayout(self.frame_layout_4)
        self.frame_layout_2.addLayout(self.frame_layout_5)
        self.frame_layout_2.addLayout(self.frame_layout_6)
        self.frame_layout_2.addLayout(self.frame_layout_7)
        self.frame_layout_2.addLayout(self.frame_layout_8)
        self.frame_layout_2.addLayout(self.frame_layout_9)
