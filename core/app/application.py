# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Центральный контроллер приложения.

Класс Application связывает вместе UI, работу с файловой системой, 
JSON-состоянием и настройками. Предоставляет ленивую инициализацию
подсистем (frontend, json_manager, settings_core) и методы для
загрузки треков, сканирования плейлистов и управления состоянием.
"""

import sys
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
from functools import cached_property
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSettings
from core.init.load_dialog import LoadDialog
from core.select.select_folder import SelectDialog

if TYPE_CHECKING:
    from core.ui.main.frontend import Frontend
    from core.json.json_manager import JsonManager
    from core.settings.settings_core import SettingsCore


class Application:
    """Центральный контроллер приложения.
    
    Хранит пути к ресурсам, состояние загрузки загрузки, 
    список жанров и настройки. Создаёт UI через Frontend
    и управляет загрузкой треков и плейлистов.
    
    Attributes:
        parent: Родительское окно (MainWindow).
        PROJECT_ROOT: Корень проекта (папка с main.py).
        PARENT_PATH: Алиас PROJECT_ROOT, используется для путей.
        MUSIC_PATH: Пользовательская папка Music.
        ICONS: Папка с иконками плейлистов.
        PATH_TO_PLAYLISTS: Внутренняя папка Playlists.
        PATH_TO_SUBGENRES: Текущий выбранный плейлист (или None).
        PATH_TO_FAVORITES: Папка Favorites в Music.
        FORMATS: Поддерживаемые аудио-расширения.
        genres_data: Список словарей {name, icon} для базовых жанров.
        loaded: Флаг, что треки были загружены хотя бы раз.
        favorites: Список имён избранных треков (кэш).
        folders: Результат сканирования Music (папки с треками).
        data: Начальная структура JSON-состояния.
        settings: QSettings для сохранения настроек подключения.
    """

    def __init__(self, parent: Optional[QMainWindow] = None):
        """Инициализирует контроллер.
        
        Args:
            parent: Родительское окно (обычно MainWindow).
        """
        self.parent = parent

        self.PROJECT_ROOT = self._find_project_root()
        self.PARENT_PATH = self.PROJECT_ROOT
        self.MUSIC_PATH = Path.home() / "Music"
        self.ICONS = self.PARENT_PATH / "icons" / "playlists"
        self.PATH_TO_PLAYLISTS = self.PARENT_PATH / "Playlists"
        self.PATH_TO_SUBGENRES = None
        self.PATH_TO_FAVORITES = self.MUSIC_PATH / "Favorites"
        self.FORMATS = (".wav", ".mp3", ".ogg", ".flac", ".m4a")

        self.genres_data = [
            {
                "name": name, 
                "icon": str(self.ICONS / f"{i}-{name.lower()}.png"), 
            }
            for i, name in enumerate(
                ["Pop", "Rock", "Metal", "Classic", "Jazz", "EDM", "Disco"], start=1
            )
        ]

        self.loaded = False
        self.favorites = []
        self.folders = []

        self.data = {
            "loaded": False, 
            "music": "", 
            "favorites": [], 
            "current": "",
        }
        self.json_manager.create_file(self.data)

        self.settings = QSettings(
            str(self.PARENT_PATH / "config" / "settings.ini"), 
            QSettings.IniFormat,
        )
    
    @staticmethod
    def _find_project_root() -> Optional[Path]:
        """Ищет корень проекта по маркеру main.py.
        
        Поднимается от текущего файла вверх по дереву директорий, 
        пока не найдёт папку с main.py. Если не нашёл - возвращает путь
        на 3 уровня выше (fallback).
        
        Returns:
            Путь к корню проекта.
        """
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parent
        
        current = Path(__file__).resolve()
        for parent in [current, *current.parents]:
            if (parent / "main.py").exists():
                return parent
        
        return Path(__file__).resolve().parents[2]

    def start(self):
        """Запускает приложение: создаёт UI, папки и загружает плейлист.
        
        Вызывается один раз при старте MainWindow.
        """
        self.frontend.init_ui()
        self.create_directory()
        self.frontend.playlist_menu.load_current_playlist()

    @cached_property
    def frontend(self) -> "Frontend":
        """Ленивая инициализация Frontend (всё UI приложения).
        
        Импорт внутри свойства - чтобы избежать циклических 
        зависимостей при старте.
        """
        from core.ui.main.frontend import Frontend
        return Frontend(app=self)
    
    @cached_property
    def json_manager(self) -> "JsonManager":
        """Ленивая инициализация JsonManager (работа с JSON)."""
        from core.json.json_manager import JsonManager
        return JsonManager()
    
    @cached_property
    def settings_core(self) -> "SettingsCore":
        """Ленивая инициализация SettingsCore (управление плейлистами)."""
        from core.settings.settings_core import SettingsCore
        return SettingsCore(app=self)
    
    def create_directory(self):
        """Создаёт папки Playlists, Favorites и подпапки жанров.
        
        Идемпотентна - если папка уже есть, ничего не делает.
        """
        if not self.PATH_TO_PLAYLISTS.exists():
            self.PATH_TO_PLAYLISTS.mkdir(parents=True, exist_ok=True)
        if not self.PATH_TO_FAVORITES.exists():
            self.PATH_TO_FAVORITES.mkdir(parents=True, exist_ok=True)

        for entry in self.genres_data:
            path = self.PATH_TO_PLAYLISTS / entry["name"]
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
    
    def load_dialog(self):
        """Открывает диалог сканирования Music (модальный)."""
        msg = "Выполняется сканирование устройства. Не закрывайте приложение."
        dialog = LoadDialog(app=self, message=msg, parent=self.parent)
        dialog.exec_()
    
    def select_dialog(self):
        """Открывает диалог выбора папки с треками (модальный)."""
        dialog = SelectDialog(app=self, parent=self.parent)
        dialog.exec_()
    
    def load_tracks(self, path: str, update_ui: bool = True):
        """Загружает треки из папки и обновляет UI плеера.
        
        Args:
            path: Путь к папке с треками.
            update_ui: Если True - обновляет обложку, метаданные и
                слайдер под первый трек. Если False - только наполняет
                список треков, не трогая играющий трек (используется
                при переключении плейлистов во время воспроизведения).
        """
        self.set_music_path(path)
        self.frontend.play_menu.sound.load_tracks(path, update_ui)

        if not self.frontend.play_menu.sound.tracks:
            self.frontend.play_menu.sound.reset_ui()
    
    def set_music_path(self, path: str):
        """Сохраняет путь к текущей папке с треками в JSON.
        
        Args:
            path: Путь к папке.
        """
        data = self.json_manager.load_file()
        self.loaded = True
        data["music"] = str(path)
        data["loaded"] = self.loaded
        self.json_manager.save_file(data)
    
    def scan_playlists(self) -> List[dict]:
        """Возвращает список плейлистов из папки Playlists.
        
        Сканирует файловую систему, а не JSON - так список
        всегда актуален, даже если папку создали вручную.
        
        Returns:
            Список словарей вида {name, path, icon}.
        """
        if not self.PATH_TO_PLAYLISTS.exists():
            return []
        result = []
        for folder in sorted(self.PATH_TO_PLAYLISTS.iterdir()):
            if not folder.is_dir():
                continue
            result.append({
                "name": folder.name, 
                "path": folder, 
                "icon": self._find_icon_for(folder.name),
            })
        return result
    
    def _find_icon_for(self, name: str) -> Optional[str]:
        """Ищет иконку плейлиста по имени.
        
        Сначала проверяет точное совпадение <name>.png
        (для пользовательских плейлистов), потом встроенные жанры 
        вида N-<name>.png. Если ничего нет - возвращает дефолтную.
        
        Args:
            name: Имя плейлиста.
        
        Returns:
            Путь к иконке или None, если даже дефолтной нет.
        """
        if not self.ICONS.exists():
            return None
        
        exact = self.ICONS / f"{name}.png"
        if exact.exists():
            return str(exact)
        
        for icon in sorted(self.ICONS.iterdir()):
            if icon.suffix != ".png":
                continue
            if icon.stem.split("-", 1)[-1].lower() == name.lower():
                return str(icon)
        
        default = self.ICONS.parent / "other" / "Folder.png"
        return str(default) if default.exists() else None
    
    def reset_playlist_state(self):
        """Сбрасывает состояние плейлиста: подсветку, 
        sublist, current в JSON.
        
        Вызывается при выборе папки через SelectDialog - чтобы UI 
        не показывал старый плейлист.
        """
        self.frontend.playlist_menu.clear_selection()
        self.frontend.sublist_menu.add_items_to_list(None)
        self.PATH_TO_SUBGENRES = None

        data = self.json_manager.load_file()
        data["current"] = ""
        self.json_manager.save_file(data)

