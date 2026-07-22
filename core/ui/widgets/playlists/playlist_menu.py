# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

import shutil
from pathlib import Path
from typing import List
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QListWidget, 
    QListView, QPushButton, QListWidgetItem, QFrame, QVBoxLayout, 
    QHBoxLayout, QSizePolicy)
from core.ui.widgets.dialogs.create_dialog import CreateDialog
from core.ui.widgets.dialogs.delete_dialog import DeleteDialog
from core.ui.widgets.dialogs.settings_dialog import SettingsDialog
from core.app.application import Application


class PlayListMenu(QWidget):
    """Список жанров. Протестировано: 09.07.2026"""
    def __init__(self, 
                    main: Application = None, 
                    parent: QMainWindow = None, 
                    app: QApplication = None):
        super().__init__()
        self.main = main
        self.parent = parent
        self.app = app
        self.data = self.main.json_manager.load_file()
        self.names: List = self.data["names"]
        self.paths: List = self.data["paths"]

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

        self.back_btn = QPushButton(self)
        self.back_btn.setText("<")
        self.back_btn.setFixedSize(60, 40)
        self.back_btn.clicked.connect(self.scroll_left)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 15pt;
            }

            QPushButton::hover {
                background: #423189;
            }
        """)
        self.frame_layout_2.addWidget(self.back_btn)

        self.playlists_menu = QListWidget(self)
        self.playlists_menu.doubleClicked.connect(self.on_item_clicked)
        self.playlists_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.playlists_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.playlists_menu.setFlow(QListView.LeftToRight)
        self.playlists_menu.setUniformItemSizes(True)
        self.playlists_menu.setWrapping(False)
        self.playlists_menu.setIconSize(QSize(50, 50))
        self.playlists_menu.setStyleSheet("""
            QListWidget {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 13pt; 
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
        self.frame_layout_2.addWidget(self.playlists_menu)
        self.add_items_to_list()

        self.next_btn = QPushButton(self)
        self.next_btn.setText(">")
        self.next_btn.setFixedSize(60, 40)
        self.next_btn.clicked.connect(self.scroll_right)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 15pt;
            }

            QPushButton::hover {
                background: #423189;
            }
        """)
        self.frame_layout_2.addWidget(self.next_btn)
        self.set_btn_visible()

        self.add_btn = QPushButton(self)
        self.add_btn.setText("Создать")
        self.add_btn.setFixedSize(80, 40)
        self.add_btn.clicked.connect(self.create_dialog)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 10pt;
            }

            QPushButton::hover {
                background: #423189;
            }
        """)
        self.frame_layout_2.addWidget(self.add_btn)

        self.pop_btn = QPushButton(self)
        self.pop_btn.setText("Удалить")
        self.pop_btn.setFixedSize(80, 40)
        self.pop_btn.clicked.connect(self.delete_dialog)
        self.pop_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 10pt;
            }

            QPushButton::hover {
                background: #423189;
            }
        """)
        self.frame_layout_2.addWidget(self.pop_btn)

        self.settings_btn = QPushButton(self)
        self.settings_btn.setText("Настройки")
        self.settings_btn.setFixedSize(80, 40)
        self.settings_btn.clicked.connect(self.settings_dialog)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 10pt;
            }

            QPushButton::hover {
                background: #423189;
            }
        """)
        self.frame_layout_2.addWidget(self.settings_btn)
    
    def get_current_text(self):
        selected_index = self.playlists_menu.currentRow()
        if selected_index >= 0:
            return self.names[selected_index]

    def on_item_clicked(self):
        selected_index = self.playlists_menu.currentRow()
        if selected_index >= 0:
            path = self.names[selected_index]
            path_to_playlist = self.main.PATH_TO_PLAYLISTS / path
            self.main.frontend.sublist_menu.add_items_to_list(path_to_playlist)
            data = self.main.json_manager.load_file()
            data["current"] = selected_index
            self.main.json_manager.save_file(data)
    
    def scroll_left(self):
        current = self.playlists_menu.currentRow()
        if current > 0:
            self.playlists_menu.setCurrentRow(current - 1)
            self.playlists_menu.scrollToItem(self.playlists_menu.currentItem())
    
    def scroll_right(self):
        current = self.playlists_menu.currentRow()
        if current < self.playlists_menu.count() - 1:
            self.playlists_menu.setCurrentRow(current + 1)
            self.playlists_menu.scrollToItem(self.playlists_menu.currentItem())

    def set_btn_visible(self):
        count = self.playlists_menu.count() > 5
        self.back_btn.setVisible(count)
        self.next_btn.setVisible(count)
    
    def add_items_to_list(self):
        data = self.main.json_manager.load_file()
        index = data.get("current", 0)
        try:
            count = 0
            self.playlists_menu.clear()
            for path in self.paths:
                if count < len(self.names):
                    icon = QIcon(path)
                    genre = self.names[count]
                    item = QListWidgetItem(icon, Path(genre).name)
                    count += 1
                    self.playlists_menu.addItem(item)
            self.playlists_menu.setCurrentRow(index)
            self.playlists_menu.setFocus()
        except IndexError:
            pass
    
    def create_dialog(self):
        dialog = CreateDialog(
            parent=self.parent, 
            create_func=self.create_playlist
        )
        dialog.exec_()
    
    def create_playlist(self, name, path):
        self.names.append(name)
        self.paths.append(path)
        self.add_items_to_list()
        self.create_folder(name)
        data = self.main.json_manager.load_file()
        data["names"] = self.names
        data["paths"] = self.paths
        self.main.json_manager.save_file(data)
    
    def create_folder(self, path: str):
        path_to_playlist = self.main.PATH_TO_PLAYLISTS / path
        path_to_playlist.mkdir(parents=True)
    
    def delete_folder(self, path: str):
        path_to_playlist = self.main.PATH_TO_PLAYLISTS / path
        shutil.rmtree(path_to_playlist)

    def get_delete_element(self):
        selected_index = self.playlists_menu.currentRow()
        if selected_index >= 0:
            return self.names[selected_index]
    
    def delete_element(self):
        try:
            selected_index = self.playlists_menu.currentRow()
            if selected_index >= 0:
                self.names.pop(selected_index)
                self.paths.pop(selected_index)
        except IndexError as e:
            print(e)

    def delete_dialog(self):
        name = self.get_delete_element()
        msg = (
            f"Вы действительно хотите удалить {name} без возможности восстановления?\n\n"
            "Продолжить?"
        )
        dialog = DeleteDialog(
            parent=self.parent, 
            message=msg, 
            delete_func=self.delete_playlist
        )
        dialog.exec_()
    
    def delete_playlist(self):
        name = self.get_delete_element()
        self.delete_element()
        self.add_items_to_list()
        self.delete_folder(name)

        data = self.main.json_manager.load_file()
        data["names"] = self.names
        data["paths"] = self.paths
        self.main.json_manager.save_file(data)
    
    def settings_dialog(self):
        dialog = SettingsDialog(
            parent=self.parent, 
            settings=self.main.settings_core
        )
        dialog.exec_()

    def load_current_playlist(self):
        data = self.main.json_manager.load_file()
        current = data.get("current", 0)
        path = self.main.genres[current]
        path_to_playlist = self.main.PATH_TO_PLAYLISTS / path
        self.main.PATH_TO_SUBGENRES = path_to_playlist
        self.main.frontend.sublist_menu.add_items_to_list(path_to_playlist)
