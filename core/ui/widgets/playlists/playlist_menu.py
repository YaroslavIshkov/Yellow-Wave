# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Панель плейлистов (верхняя строка с жанрами).

Показывает список плейлистов в горизонтальной прокрутке с иконками.
Кнопки: стрелки влево/вправо (прокрутка), Создать, Удалить, Настройки.
Двойной клик по плейлисту загружает его в sublist и список треков.

Список плейлистов берётся из файловой системы (scan_playlists), а не из
JSON - так UI всегда актуален, даже если вручную папку создали в проводнике.
"""

import shutil
import logging
from pathlib import Path
from typing import List, Optional
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QListWidget, QListView, QPushButton, 
    QListWidgetItem, QFrame, QVBoxLayout, QHBoxLayout, QSizePolicy)
from core.ui.widgets.dialogs.create_dialog import CreateDialog
from core.ui.widgets.dialogs.delete_dialog import DeleteDialog
from core.ui.widgets.dialogs.settings_dialog import SettingsDialog
from core.app.application import Application
from core.messages.message_box import MessageBox
from core.ui.style.styles import (TRANSPARENT_FRAME, TRANSPARENT_LIST, 
    TRANSPARENT_BUTTON_BIG, TRANSPARENT_BUTTON_SMALL)

log = logging.getLogger("YellowWave")


class PlayListMenu(QWidget):
    """Панель плейлистов с горизонтальной прокруткой.
    
    Содержит QListWidget в режиме LeftToRight (горизонтальный flow), 
    набор кнопок управления и стрелки для прокрутки. Список пересобирается
    через scan_playlists() после каждой операции создания/удаления - единый
    источник правды.

    Attributes:
        app: Ссылка на Application.
        playlists: Список словарей {name, path, icon}.
        playlists_menu: QListWidget с плейлистами.
    """

    def __init__(self, app: Optional[Application] = None):
        """Создаёт панель плейлистов.
        
        Args:
            app: Экземпляр Application.
        """
        super().__init__()
        self.app = app

        self.playlists: List[dict] = []

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(TRANSPARENT_FRAME)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QHBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)

        self.back_btn = QPushButton()
        self.back_btn.setText("<")
        self.back_btn.setFixedSize(60, 40)
        self.back_btn.clicked.connect(self.scroll_left)
        self.back_btn.setStyleSheet(TRANSPARENT_BUTTON_BIG)
        self.frame_layout_2.addWidget(self.back_btn)

        self.playlists_menu = QListWidget()
        self.playlists_menu.doubleClicked.connect(self.on_item_clicked)
        self.playlists_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.playlists_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.playlists_menu.setFlow(QListView.LeftToRight)
        self.playlists_menu.setUniformItemSizes(True)
        self.playlists_menu.setWrapping(False)
        self.playlists_menu.setIconSize(QSize(50, 50))
        self.playlists_menu.setStyleSheet(TRANSPARENT_LIST)
        self.frame_layout_2.addWidget(self.playlists_menu)
        self.add_items_to_list()

        self.next_btn = QPushButton()
        self.next_btn.setText(">")
        self.next_btn.setFixedSize(60, 40)
        self.next_btn.clicked.connect(self.scroll_right)
        self.next_btn.setStyleSheet(TRANSPARENT_BUTTON_BIG)
        self.frame_layout_2.addWidget(self.next_btn)
        self.set_btn_visible()

        self.playlists_menu.model().rowsInserted.connect(self.set_btn_visible)
        self.playlists_menu.model().rowsRemoved.connect(self.set_btn_visible)

        self.add_btn = QPushButton()
        self.add_btn.setText("Создать")
        self.add_btn.setFixedSize(80, 40)
        self.add_btn.clicked.connect(self.create_dialog)
        self.add_btn.setStyleSheet(TRANSPARENT_BUTTON_SMALL)
        self.frame_layout_2.addWidget(self.add_btn)

        self.pop_btn = QPushButton()
        self.pop_btn.setText("Удалить")
        self.pop_btn.setFixedSize(80, 40)
        self.pop_btn.clicked.connect(self.delete_dialog)
        self.pop_btn.setStyleSheet(TRANSPARENT_BUTTON_SMALL)
        self.frame_layout_2.addWidget(self.pop_btn)

        self.settings_btn = QPushButton()
        self.settings_btn.setText("Настройки")
        self.settings_btn.setFixedSize(80, 40)
        self.settings_btn.clicked.connect(self.settings_dialog)
        self.settings_btn.setStyleSheet(TRANSPARENT_BUTTON_SMALL)
        self.frame_layout_2.addWidget(self.settings_btn)

        self.back_btn.setToolTip("Прокрутить влево")
        self.next_btn.setToolTip("Прокрутить вправо")
        self.add_btn.setToolTip("Создать новый плейлист")
        self.pop_btn.setToolTip("Удалить выбранный плейлист")
        self.settings_btn.setToolTip("Настройки")
    
    def get_current_text(self) -> Optional[str]:
        """Возвращает имя текущего выбранного плейлиста.
        
        Returns:
            Имя плейлиста или None, если ничего не выбрано.
        """
        idx = self.playlists_menu.currentRow()
        if 0 <= idx < len(self.playlists):
            return self.playlists[idx]["name"]
        return None

    def on_item_clicked(self):
        """Обработчик двойного клика по плейлисту.
        
        Загружает поджанры (sublist) и список треков плейлиста (без
        обновления UI плеера - играющий трек продолжает играть).
        Сохраняет current и music в JSON. Двойной клик используется 
        вместо одиночного, чтобы случайный клик не переключал плейлист.
        """
        idx = self.playlists_menu.currentRow()
        if not (0 <= idx < len(self.playlists)):
            return
        entry = self.playlists[idx]
        path_to_playlist = self.app.PATH_TO_PLAYLISTS / entry["name"]
        self.app.PATH_TO_SUBGENRES = path_to_playlist

        self.app.frontend.sublist_menu.add_items_to_list(path_to_playlist)

        self.app.load_tracks(str(path_to_playlist), update_ui=False)

        data = self.app.json_manager.load_file()
        data["current"] = entry["name"]
        data["music"] = str(path_to_playlist)
        self.app.json_manager.save_file(data)
    
    def clear_selection(self):
        """Снимает выделение с плейлиста (setCurrentRow(-1))."""
        self.playlists_menu.clearSelection()
        self.playlists_menu.setCurrentRow(-1)
    
    def scroll_left(self):
        """Прокручивает список плейлистов на один элемент влево."""
        current = self.playlists_menu.currentRow()
        if current > 0:
            self.playlists_menu.setCurrentRow(current - 1)
            self.playlists_menu.scrollToItem(self.playlists_menu.currentItem())
    
    def scroll_right(self):
        """Прокручивает список плейлистов на один элемент вправо."""
        current = self.playlists_menu.currentRow()
        if current < self.playlists_menu.count() - 1:
            self.playlists_menu.setCurrentRow(current + 1)
            self.playlists_menu.scrollToItem(self.playlists_menu.currentItem())

    def set_btn_visible(self, *args):
        """Показывает/скрывает стрелки прокрутки.
        
        Если плейлистов нет - стрелки не нужны, скрываем. Аргумент *args
        принимает служебные параметры от Qt-сигналов (rowsInserted/rowsRemoved
        передают три числа).

        Args:
            *args: Параметры сигналов Qt, игнорируются.
        """
        count = self.playlists_menu.count() > 0
        self.back_btn.setVisible(count)
        self.next_btn.setVisible(count)
    
    def add_items_to_list(self):
        """Пересобирает список плейлистов из файловой системы.
        
        Сканирует Playlists через Application.scan_playlists(), 
        заполняет QListWidget с иконками, восстанавливает выделение
        по current из JSON.

        try/except IndexError - защита от гонок, когда scan_playlists
        вернул список короче, чем ожидалось.
        """
        try:
            self.playlists_menu.clear()
            self.playlists = self.app.scan_playlists()

            for entry in self.playlists:
                icon = QIcon(entry["icon"]) if entry["icon"] else QIcon()
                item = QListWidgetItem(icon, entry["name"])
                self.playlists_menu.addItem(item)
            
            data = self.app.json_manager.load_file()
            current_name = data.get("current", "")
            index = next(
                (i for i, e in enumerate(self.playlists) 
                if e["name"] == current_name), 0,
            )
            self.playlists_menu.setCurrentRow(index)
            self.playlists_menu.setFocus()
        except IndexError as e:
            log.warning(f"IndexError при пересборке списка: {e}")
    
    def create_dialog(self):
        """Открывает диалог создания плейлиста (модально)."""
        dialog = CreateDialog(
            parent=self.app.parent, 
            create_func=self.create_playlist
        )
        dialog.exec_()
    
    def create_playlist(self, name: str, icon_path: Optional[str] = None):
        """Создаёт новый плейлист (папку + иконку).

        Проверяет валидность имени, отсутствие дубликата. Создаёт папку
        в Playlists, копирует иконку (если указана), обновляет список.

        Args:
            name: Имя нового плейлиста.
            icon_path: Путь к PNG-иконке (или имя файла из ICONS).
        """
        if not self.app.settings_core.is_valid_name(name):
            msg = 'Имя не должно содержать: < > : " / \\ | ? *'
            MessageBox(parent=self.app.parent, message=msg).exec_()
            return
        
        new_path = self.app.PATH_TO_PLAYLISTS / name
        if new_path.exists():
            MessageBox(parent=self.app.parent, 
                message=f"Плейлист {name} уже существует").exec_()
            return
        
        try:
            new_path.mkdir(parents=True)
        except OSError as e:
            MessageBox(parent=self.app.parent, 
                message=f"Не удалось создать: {e}").exec_()
            return
        
        if icon_path:
            self._copy_icon(name, icon_path)
        
        self.add_items_to_list()
    
    def _copy_icon(self, playlist_name: str, icon_source: str):
        """Копирует иконку плейлиста в icons/playlists/<name>.png. 
        
        icon_source может быть: 
            - полным путём к png-файлу на диске
            - именем файла из icons/playlists/ (например, 'pop-icon.png')
        
        Если файл не найден - тихо игнорируется (плейлист получит дефолтную иконку).

        Args:
            playlist_name: Имя плейлиста (станет именем PNG).
            icon_source: Путь к исходной иконке или имя файла.
        """
        src = Path(icon_source)

        if not src.is_absolute():
            candidate = self.app.ICONS / icon_source
            if candidate.exists():
                src = candidate
        
        if not src.exists() or not src.is_file():
            return
        
        dst = self.app.ICONS / f"{playlist_name}.png"
        try:
            shutil.copy(str(src), str(dst))
        except OSError as e:
            log.error(f"Не удалось скопировать иконку: {e}")

    def get_selected_entry(self) -> Optional[dict]:
        """Возвращает текущий выбранный плейлист.
        
        Returns:
            Словарь {name, path, icon} или None, если ничего не выбрано.
        """
        idx = self.playlists_menu.currentRow()
        if 0 <= idx < len(self.playlists):
            return self.playlists[idx]
        return None

    def delete_dialog(self):
        """Открывает диалог подтверждения удаления плейлиста.
        
        Считает количество файлов и подпапок внутри (через rglob)
        и показывает это в тексте подтверждения. Если внутри пусто - 
        предупреждение короче.
        """
        idx = self.playlists_menu.currentRow()
        if not (0 <= idx < len(self.playlists)):
            return
        
        entry = self.playlists[idx]
        name = entry["name"]
        path = self.app.PATH_TO_PLAYLISTS / name

        files_count = 0
        dirs_count = 0
        if path.exists():
            for item in path.rglob("*"):
                if item.is_file():
                    files_count += 1
                elif item.is_dir():
                    dirs_count += 1
        
        msg = f"Удалить плейлист '{name}' без возможности восстановления?\n\n"
        if files_count or dirs_count:
            msg += f"Внутри: файлов - {files_count}, папок - {dirs_count}.\n\n"
        msg += "Продолжить?"

        dialog = DeleteDialog(
            parent=self.app.parent, 
            message=msg, 
            delete_func=self.delete_playlist
        )
        dialog.exec_()
    
    def delete_playlist(self):
        """Удаляет текущий плейлист и обновляет состояние.
        
        Удаляет папку рекурсивно, иконку, обновляет JSON (если
        удалённый был current - переключается на первый доступный).
        Обновляет UI: список плейлистов, sublist, стрелки.
        """
        idx = self.playlists_menu.currentRow()
        if not (0 <= idx < len(self.playlists)):
            return
        
        entry = self.playlists[idx]
        path = self.app.PATH_TO_PLAYLISTS / entry["name"]
        if path.exists():
            try:
                shutil.rmtree(str(path))
            except OSError as e:
                MessageBox(parent=self.app.parent, 
                    message=f"Не удалось удалить: {e}").exec_()
                return
        
        icon_file = self.app.ICONS / f"{entry['name']}.png"
        if icon_file.exists():
            try:
                icon_file.unlink()
            except OSError:
                pass
        
        MessageBox(parent=self.app.parent, 
            message=f"Плейлист {entry['name']} удалён").exec_()
        
        data = self.app.json_manager.load_file()
        if data.get("current") == entry["name"]:
            remaining = self.app.scan_playlists()
            if remaining:
                new_current = remaining[0]["name"]
                self.app.PATH_TO_SUBGENRES = remaining[0]["path"]
                data["current"] = new_current
                data["music"] = str(remaining[0]["path"])
            else:
                self.app.PATH_TO_SUBGENRES = None
                data["current"] = ""
                data["music"] = ""
            self.app.json_manager.save_file(data)
        
        self.add_items_to_list()
        self.app.frontend.sublist_menu.add_items_to_list(
            self.app.PATH_TO_SUBGENRES)
    
    def settings_dialog(self):
        """Открывает диалог настроек (модально)."""
        dialog = SettingsDialog(
            parent=self.app.parent, 
            settings=self.app.settings_core
        )
        dialog.exec_()

    def load_current_playlist(self):
        """Восстанавливает состояние плейлиста при старте приложения.
        
        Читает current из JSON:
            - если пусто - сбрасывает sublist, ничего не выделяет
            - если число (старый формат) - конвертирует в имя
            - если имя не найдено - берёт первый плейлист из scan_playlists
        
        Загружает sublist для выбранного плейлиста.
        """
        data = self.app.json_manager.load_file()
        current = data.get("current", "")

        if not current:
            self.clear_selection()
            self.app.PATH_TO_SUBGENRES = None
            self.app.frontend.sublist_menu.add_items_to_list(None)
            return

        if isinstance(current, int):
            names = [g["name"] for g in self.app.genres_data]
            current_name = names[current] if 0 <= current < len(names) else ""
        else:
            current_name = str(current)
        
        path_to_playlist = (
            self.app.PATH_TO_PLAYLISTS / current_name 
            if current_name else None
        )

        if not path_to_playlist or not path_to_playlist.exists():
            playlists = self.app.scan_playlists()
            if not playlists:
                return
            path_to_playlist = playlists[0]["path"]
        
        self.app.PATH_TO_SUBGENRES = path_to_playlist
        self.app.frontend.sublist_menu.add_items_to_list(path_to_playlist)
