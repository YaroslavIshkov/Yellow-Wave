# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Список поджанров текущего плейлиста.

Показывает подпапки внутри выбранного плейлиста
(например, внутри Rock - Grunge, Alternative). Двойной клик по
поджанру загружает его треки в TrackMenu. Ширина фиксирована
(500px), высота растягивается.
"""

from pathlib import Path
from typing import Optional, List
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QListWidget, QWidget, QFrame, QVBoxLayout, 
    QSizePolicy)
from core.app.application import Application
from core.messages.message_box import MessageBox
from core.ui.style.styles import TRANSPARENT_FRAME, WHITE_LIST_BIG


class SubListMenu(QWidget):
    """Виджет со списком поджанров.
    
    Хранит два параллельных списка:
        sublists - Path-объекты папок (для логики)
        shorts - только имена (для отображения в QListWidget)
    
    Синхронизация между ними - по индексу. При клике читаем путь из
    sublists, показываем shorts.

    Attributes:
        app: Ссылка на Application.
        sublists: Список Path-объектов папок поджанров.
        shorts: Список имён поджанров (для UI).
        sublists_menu: QListWidget с именами.
    """

    def __init__(self, app: Optional[Application] = None):
        """Создаёт виджет с пустым списком поджанров.
        
        Args:
            app: Экземпляр Application.
        """
        super().__init__()
        self.app = app

        self.sublists: List[Path] = []
        self.shorts: List[str] = []

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setFixedWidth(500)
        self.frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.frame.setStyleSheet(TRANSPARENT_FRAME)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)

        self.sublists_menu = QListWidget()
        self.sublists_menu.doubleClicked.connect(self.on_item_clicked)
        self.sublists_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sublists_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sublists_menu.setStyleSheet(WHITE_LIST_BIG)
        self.frame_layout_2.addWidget(self.sublists_menu)

    def on_item_clicked(self):
        """Обработчик двойного клика по поджанру.
        
        Загружает треки из выбранной подпапки через Application.load_tracks
        и сохраняет путь в JSON (music).
        """
        idx = self.sublists_menu.currentRow()
        if not (0 <= idx < len(self.sublists)):
            return
        
        path_to_subgenre = self.sublists[idx]

        try:
            self.app.load_tracks(str(path_to_subgenre), update_ui=False)

            data = self.app.json_manager.load_file()
            data["music"] = str(path_to_subgenre)
            self.app.json_manager.save_file(data)
        except Exception as e:
            MessageBox(parent=self.app.parent, 
                message=f'Не удалось открыть {path_to_subgenre.name}: {e}').exec_()
    
    def add_items_to_list(self, path: Optional[Path] = None):
        """Заполняет список поджанрами из указанной папки.
        
        Сканирует папку, берёт только директории (файлы игнорируются), 
        сортирует по имени. Заполняет оба списка (sublists и shorts), 
        выделяет первый элемент и ставит фокус.

        Если path=None или не существует - списки очищаются и остаются пустыми.

        Args:
            path: Путь к папке плейлиста (например, .../Playlist/Rock).
        """
        self.sublists.clear()
        self.shorts.clear()
        self.sublists_menu.clear()
        if path is None or not path.exists():
            return
        for folder in sorted(path.iterdir()):
            if not folder.is_dir():
                continue
            self.sublists.append(folder)
            self.shorts.append(folder.name)
        self.sublists_menu.addItems(self.shorts)
        if self.shorts:
            self.sublists_menu.setCurrentRow(0)
        self.sublists_menu.setFocus()
