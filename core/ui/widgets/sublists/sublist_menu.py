# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QListWidget, QWidget, QFrame, QVBoxLayout, 
    QSizePolicy)
from core.app.application import Application


class SubListMenu(QWidget):
    """Список поджанров. Протестировано: 09.07.2026"""
    def __init__(self, main: Application = None):
        super().__init__()
        self.main = main
        self.sublists = []
        self.shorts = []

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

        self.frame_layout_2 = QVBoxLayout()
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(self.frame_layout_2)

        self.sublists_menu = QListWidget(self)
        self.sublists_menu.doubleClicked.connect(self.on_item_clicked)
        self.sublists_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sublists_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sublists_menu.setStyleSheet("""
            QListWidget {
                background: #FFFFFF; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt; 
                outline: 0;
            }

            QListWidget::item {
                background: transparent; 
                border-radius: 5px; 
            }

            QListWidget::item:hover {
                background: #E8D0F0;
            }

            QListWidget::item:selected {
                background: #D6B4FF; 
                color: #3D3D3D;
            }
        """)
        self.frame_layout_2.addWidget(self.sublists_menu)

    def on_item_clicked(self):
        selected_index = self.sublists_menu.currentRow()
        if selected_index >= 0:
            path = self.sublists[selected_index]
            path_to_subgenre = self.main.PATH_TO_SUBGENRES / path
            self.main.frontend.play_menu.sound.load_tracks(path_to_subgenre)
            data = self.main.json_manager.load_file()
            data["music"] = str(path_to_subgenre)
            self.main.json_manager.save_file(data)
    
    def add_items_to_list(self, path: Optional[Path] = None):
        self.sublists.clear()
        self.shorts.clear()
        for folder in path.iterdir():
            self.sublists.append(folder)
            self.shorts.append(folder.name)
        self.sublists_menu.clear()
        self.sublists_menu.addItems(self.shorts)
        self.sublists_menu.setCurrentRow(0)
        self.sublists_menu.setFocus()
