# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Кнопка 'Избранное' (сердечко).

Добавляет или удаляет текущий трек из плейлиста Favorites: 
копирует файл в Music/Favorites, ведёт список имён в JSON.
Иконка меняется в зависимости от состояния (заполненная / 
пустая). В папке Favorites кнопка неактивна - трек там уже есть.
"""

import os
import shutil
from typing import Optional
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from core.app.application import Application
from core.messages.message_box import MessageBox


class HeartButton(QWidget):
    """Кнопка-сердечко для добавления трека в Избранное.
    
    Работает с текущим выделенным треком в TrackMenu. При клике: 
    копирует файл в Music/Favorites, добавляет имя в JSON-список
    favorites, меняет иконку на 'заполненное сердце'. Повторный
    клик удаляет файл и имя из списка.
    
    Attributes:
        app: Ссылка на Application.
        active: Путь к иконке 'заполненное сердце'.
        deactive: Путь к иконке 'пустое сердце'.
    """

    def __init__(self, app: Optional[Application] = None):
        """Создаёт кнопку-сердечко.
        
        Args:
            app: Экземпляр Application.
        """
        super().__init__()
        self.app = app

        self.icons = self.app.PARENT_PATH / "icons"
        self.active = str(self.icons / "heart" / "active-heart.png")
        self.deactive = str(self.icons / "heart" / "deactive-heart.png")

        self.heart_btn = QPushButton()
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

        self.heart_btn.setIcon(QIcon(self.deactive))
        self.heart_btn.setIconSize(QSize(25, 25))
        self.heart_btn.setToolTip("Добавить в избранное (L)")
    
    def liked(self):
        """Обновляет иконку в зависимости от состояния текущего трека.
        
        Порядок проверок:
        1. Если трек не выбран - показываем 'пустое сердце'.
        2. Если трек лежит в папке Favorites - 'заполненное'.
        3. Иначе - смотрим JSON favorites по имени файла.
        """
        btn_icon = None
        track_index = self.app.frontend.track_menu.get_current_index()

        tracks = self.app.frontend.play_menu.sound.tracks
        if track_index is None or not tracks or track_index >= len(tracks):
            self.heart_btn.setIcon(QIcon(self.deactive))
            self.heart_btn.setIconSize(QSize(25, 25))
            return
        
        track = tracks[track_index]

        if track.parent.name == 'Favorites':
            btn_icon = QIcon(self.active)
            self.heart_btn.setIcon(btn_icon)
            self.heart_btn.setIconSize(QSize(25, 25))
            return
        
        data = self.app.json_manager.load_file()
        favorites = data.get("favorites", [])
        
        if track.name in favorites:
            btn_icon = QIcon(self.active)
        else:
            btn_icon = QIcon(self.deactive)
        self.heart_btn.setIcon(btn_icon)
        self.heart_btn.setIconSize(QSize(25, 25))

    def on_button_clicked(self):
        """Обрабатывает клик по сердечку.
        
        Игнорирует клики на треках из папки Favorites (они там уже
        есть). Иначе - добавляет или удаляет в зависимости от того, 
        есть ли имя в JSON-списке favorites.
        """
        track_index = self.app.frontend.track_menu.get_current_index()
        if track_index is None:
            return
        
        track = self.app.frontend.play_menu.sound.tracks[track_index]
        track_name = track.name
        if track.parent.name == 'Favorites':
            return
        
        data = self.app.json_manager.load_file()
        favorites = data.get("favorites", [])

        if track_name in favorites:
            self.pop_from_favorites()
        else:
            self.add_to_favorites()

        self.liked()
    
    def add_to_favorites(self):
        """Добавляет текущий трек в Favorites.
        
        Копирует файл в Music/Favorites и добавляет имя в JSON-список.
        Если файл уже есть на диске - копирование пропускается.
        """
        track_index = self.app.frontend.track_menu.get_current_index()
        if track_index is None:
            msg = "Треки не найдены"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()
            return
        
        track = self.app.frontend.play_menu.sound.tracks[track_index]
        data = self.app.json_manager.load_file()
        favorites = data.get("favorites", [])

        if track.name not in favorites:
            favorites.append(track.name)
        data["favorites"] = favorites
        self.app.json_manager.save_file(data)

        path_to_track = self.app.PATH_TO_FAVORITES / track.name
        if not path_to_track.exists():
            shutil.copy(str(track), str(path_to_track))

        msg = "Добавлено в Избранное"
        message_box = MessageBox(parent=self.app.parent, message=msg)
        message_box.exec_()
    
    def pop_from_favorites(self):
        """Удаляет текущий трек из Favorites.

        Удаляет файл из Music/Favorites и имя из JSON-списка.
        """
        track_index = self.app.frontend.track_menu.get_current_index()
        if track_index is None:
            msg = "Треки не найдены"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()
            return
        
        track = self.app.frontend.play_menu.sound.tracks[track_index]
        data = self.app.json_manager.load_file()
        favorites = data.get("favorites", [])
        
        if track.name in favorites:
            index = favorites.index(track.name)
            favorites.pop(index)
        self.app.json_manager.save_file(data)

        favorite_path = self.app.PATH_TO_FAVORITES / track.name
        if favorite_path.exists():
            os.remove(str(favorite_path))

        msg = "Удалено из Избранного"
        message_box = MessageBox(parent=self.app.parent, message=msg)
        message_box.exec_()
