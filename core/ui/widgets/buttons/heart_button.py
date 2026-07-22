# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from core.app.application import Application
from core.messages.message_box import MessageBox


class HeartButton(QWidget):
    """Кнопка добавляющая трек в плейлист Избранное. Протестировано: 09.07.2026"""
    def __init__(self, parent=None, app: Application = None):
        super().__init__(parent)

        self.app = app

        self.active = str(Path(__file__).parents[4] / "icons" / "heart" / "active-heart.png")
        self.deactive = str(Path(__file__).parents[4] / "icons" / "heart" / "deactive-heart.png")

        self.heart_btn = QPushButton(self)
        self.heart_btn.clicked.connect(self.on_button_clicked)
        self.heart_btn.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border: none; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 15pt;
            }
        """)
        self.heart_btn.setFixedWidth(70)
        self.heart_btn.setFixedHeight(50)

        self.set_button_state()
    
    def set_button_state(self):
        data = self.app.json_manager.load_file()
        data["liked"] = False
        self.app.json_manager.save_file(data)
    
    def liked(self):
        btn_icon = None
        track_index = self.app.frontend.track_menu.get_current_index()
        if track_index is None:
            btn_icon = QIcon(self.deactive)
            self.heart_btn.setIcon(btn_icon)
            self.heart_btn.setIconSize(QSize(25, 25))
            return
        track = self.app.frontend.play_menu.sound.tracks[track_index].name
        data = self.app.json_manager.load_file()
        favorites = data.get("favorites", [])
        if track in favorites:
            btn_icon = QIcon(self.active)
        else:
            btn_icon = QIcon(self.deactive)
        self.heart_btn.setIcon(btn_icon)
        self.heart_btn.setIconSize(QSize(25, 25))

    def on_button_clicked(self):
        data = self.app.json_manager.load_file()
        liked = data.get("liked", False)
        if liked:
            data["liked"] = False
            self.pop_from_favorites()
        else:
            data["liked"] = True
            self.add_to_favorites()
        self.app.json_manager.save_file(data)
    
    def set_button_icon(self):
        icon = ""
        data = self.app.json_manager.load_file()
        liked = data.get("liked", [])
        if liked:
            icon = self.active
        else:
            icon = self.deactive
        btn_icon = QIcon(icon)
        self.heart_btn.setIcon(btn_icon)
        self.heart_btn.setIconSize(QSize(25, 25))
    
    def add_to_favorites(self):
        track_index = self.app.frontend.track_menu.get_current_index()
        if not track_index:
            msg = "Треки не найдены"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()
            return
        track = self.app.frontend.play_menu.sound.tracks[track_index]
        data = self.app.json_manager.load_file()
        favorites = data.get("favorites", [])
        if track not in favorites:
            favorites.append(track.name)
        self.app.json_manager.save_file(data)

        path_to_track = self.app.PATH_TO_FAVORITES / track.name
        if not path_to_track.exists():
            shutil.copy(str(track), str(path_to_track))

        msg = "Добавлено в Избранное"
        message_box = MessageBox(parent=self.app.parent, message=msg)
        message_box.exec_()
    
    def pop_from_favorites(self):
        track_index = self.app.frontend.track_menu.get_current_index()
        if not track_index:
            msg = "Треки не найдены"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()
            return
        track = self.app.frontend.play_menu.sound.tracks[track_index]
        data = self.app.json_manager.load_file()
        favorites = data.get("favorites", [])
        if track in favorites:
            index = favorites.index(track.name)
            favorites.pop(index)
        self.app.json_manager.save_file(data)

        favorite_path = self.app.PATH_TO_FAVORITES / track.name
        if favorite_path:
            os.remove(str(favorite_path))

        msg = "Удалено из Избранного"
        message_box = MessageBox(parent=self.app.parent, message=msg)
        message_box.exec_()
