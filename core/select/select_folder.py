# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Диалог выбора папки с треками.

Открывается после сканирования Music (LoadDialog). Показывает
уникальные папки, найденные при сканировании, в виде списка
с иконками. Пльзователь выбирает папку и запускает загрузку треков.
"""

from typing import Optional, TYPE_CHECKING
from PyQt5.QtWidgets import (QDialog, QFrame, QMainWindow, QVBoxLayout, 
    QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QPushButton, 
    QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from core.ui.style.styles import (DIALOG_FRAME, DIALOG_LABEL, PRIMARY_BUTTON, 
    TRANSPARENT_BUTTON, SELECT_LIST, apply_shadow)

if TYPE_CHECKING:
    from core.app.application import Application

class SelectDialog(QDialog):
    """Модальный диалог выбора папки из результатов сканирования.
    
    Показывает список папок, которые были найдены в Music во время
    LoadDialog. Список берётся из Application.folders - это уже
    отфильтрованный и отсортированный набор уникальных папок с
    аудиофайлами.
    
    Attributes:
        app: Ссылка на Application.
        icon_path: Путь к иконке папки (одна для всех элементов).
    """
    def __init__(self, 
                    app: Optional["Application"] = None, 
                    parent: Optional[QMainWindow] = None):
        """Создаёт диалог выбора папки.
        
        Args:
            app: Экземпляр Application с заполнением folders.
            parent: Родительское окно (обычно MainWindow).
        """
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 450)
        self.app = app

        self.icons = self.app.PARENT_PATH / "icons"
        self.icon_path = self.icons / "other" / "Folder.png"

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(20, 20, 30, 30)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(DIALOG_FRAME)
        apply_shadow(self.frame)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 0, 0, 0)

        self.title_lbl = QLabel()
        self.title_lbl.setText("Выбор папки:")
        self.title_lbl.setFixedHeight(40)
        self.title_lbl.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_3.addWidget(self.title_lbl)
        self.frame_layout_3.addStretch()

        self.close_btn = QPushButton()
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setText("Закрыть")
        self.close_btn.setFixedSize(80, 40)
        self.close_btn.setStyleSheet(TRANSPARENT_BUTTON)
        self.frame_layout_3.addWidget(self.close_btn)

        self.frame_layout_4 = QVBoxLayout()
        self.frame_layout_4.setContentsMargins(0, 0, 0, 0)

        self.folders_menu = QListWidget()
        self.folders_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.folders_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.folders_menu.setTextElideMode(Qt.ElideMiddle)
        self.folders_menu.setIconSize(QSize(64, 64))
        self.folders_menu.setStyleSheet(SELECT_LIST)
        self.frame_layout_4.addWidget(self.folders_menu)
        
        self.select_btn = QPushButton()
        self.select_btn.clicked.connect(self.open_folder)
        self.select_btn.setText("Выбрать")
        self.select_btn.setFixedSize(80, 40)
        self.select_btn.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_4.addWidget(self.select_btn)
        
        self.frame_layout_2.addLayout(self.frame_layout_3)
        self.frame_layout_2.addLayout(self.frame_layout_4)

        self.add_items_to_list()
    
    def add_items_to_list(self):
        """Заполняет список папками из Application.folders.
        
        Каждая папка получает одну и ту же иконку Folder.png. Если список
        не пустой - выделяет первый элемент. Если пустой - пользователь увидит
        пустой список и неактивную кнопку 'Выбрать' (обрабатывается в open_folder).
        """
        self.folders_menu.clear()
        for path in self.app.folders:
            item = QListWidgetItem(QIcon(str(self.icon_path)), path.name)
            self.folders_menu.addItem(item)
        if self.app.folders:
            self.folders_menu.setCurrentRow(0)
        self.folders_menu.setFocus()
    
    def open_folder(self):
        """Обрабатывает выбор папки и запускает загрузку треков.
        
        Проверяет границы индекса (защита от IndexError), сбрасывает
        состояние плейлиста (снимает подсветку, очищает sublist, 
        сбрасывает current в JSON) и передаёт путь в Application.load_tracks.
        """
        selected_index = self.folders_menu.currentRow()
        if 0 <= selected_index < len(self.app.folders):
            path_to_folder = self.app.folders[selected_index]
            self.accept()
            self.app.reset_playlist_state()
            self.app.load_tracks(str(path_to_folder))
            sound = self.app.frontend.play_menu.sound
            sound.started = False
            sound.paused = False
            self.app.frontend.play_menu.play_button.update_icon()
