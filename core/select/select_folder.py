# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QFrame, QMainWindow, QVBoxLayout, 
    QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QPushButton, 
    QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize


class SelectDialog(QDialog):
    def __init__(self, app=None, parent: QMainWindow = None):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 450)

        self.app = app
        self.icons_path = Path(__file__).parents[2] / "icons" / "other"
        self.icon_path = self.icons_path / "Folder.png"

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

        self.title_lbl = QLabel()
        self.title_lbl.setText("Выбор папки:")
        self.title_lbl.setFixedHeight(40)
        self.title_lbl.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_2.addWidget(self.title_lbl)

        self.folders_menu = QListWidget()
        self.folders_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.folders_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.folders_menu.setIconSize(QSize(64, 64))
        self.folders_menu.setStyleSheet("""
            QListWidget {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt; 
                outline: 0;
            }

            QListWidget::item {
                min-width: 130px; 
                min-height: 30px; 
                text-align: center; 
                padding: 5px 12px; 
                margin: 2px; 
                border-radius: 5px; 
                background: transparent; 
                padding-left: 5px;
            }

            QListWidget::item:hover {
                background: #423189; 
                border-radius: 5px;
            }

            QListWidget::item:selected {
                background: #423189; 
                border-radius: 5px; 
                color: #FFFFFF;
            }
        """)
        self.frame_layout_2.addWidget(self.folders_menu)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_layout_3.addStretch()
        
        self.select_btn = QPushButton()
        self.select_btn.clicked.connect(self.open_folder)
        self.select_btn.setText("Выбрать")
        self.select_btn.setFixedSize(80, 40)
        self.select_btn.setStyleSheet("""
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
        self.frame_layout_3.addWidget(self.select_btn)
        
        self.frame_layout_2.addLayout(self.frame_layout_3)

        self.add_items_to_list()
    
    def add_items_to_list(self):
        self.folders_menu.clear()
        for path in self.app.relative:
            item = QListWidgetItem(QIcon(str(self.icon_path)), str(path))
            self.folders_menu.addItem(item)
        self.folders_menu.setCurrentRow(0)
        self.folders_menu.setFocus()
    
    def open_folder(self):
        selected_index = self.folders_menu.currentRow()
        if selected_index >= 0:
            path_to_folder = self.app.absolute[selected_index]
            self.accept()
            self.app.load_tracks(path_to_folder)
