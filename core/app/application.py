# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from functools import lru_cache
from typing import Optional
from PyQt5.QtWidgets import QApplication, QMainWindow
from core.init.load_dialog import LoadDialog
from core.select.select_folder import SelectDialog


class Application:
    def __init__(self, 
                    app: Optional[QApplication] = None, 
                    parent: Optional[QMainWindow] = None):
        self.app = app
        self.parent = parent

        self.ROOT_PATH = Path(__file__).parents[3]
        self.PARENT_PATH = self.ROOT_PATH / "YellowWave"
        self.ICONS = self.PARENT_PATH / "icons" / "playlists"
        self.PATH_TO_PLAYLISTS = self.PARENT_PATH / "Playlists"
        self.PATH_TO_SUBGENRES = None
        self.PATH_TO_FAVORITES = self.PARENT_PATH / "Favorites"
        self.FORMATS = (".wav", ".mp3", ".ogg", ".flac")

        self.genres = ["Pop", "Rock", "Metal", "Classic", "Jazz", "EDM", "Disco"]
        self.icons = [str(path) for path in self.ICONS.iterdir()]

        self.loaded = False
        self.copied = []
        self.favorites = []
        self.absolute = []
        self.relative = []
        self.current = 0

        self.data = {}
        self.data["names"] = self.genres
        self.data["paths"] = self.icons
        self.data["loaded"] = self.loaded
        self.data["copied"] = self.copied
        self.data["favorites"] = self.favorites
        self.data["current"] = self.current
        self.json_manager.create_file(self.data)

    def start(self):
        self.frontend.init_ui()
        self.create_directory()
        self.frontend.playlist_menu.load_current_playlist()

    @property
    @lru_cache(maxsize=None)
    def frontend(self):
        from core.ui.main.frontend import Frontend
        return Frontend(app=self.app, main=self, parent=self.parent)
    
    @property
    @lru_cache(maxsize=None)
    def json_manager(self):
        from core.json.json_manager import JsonManager
        return JsonManager()
    
    @property
    @lru_cache(maxsize=None)
    def settings_core(self):
        from core.settings.settings_core import SettingsCore
        return SettingsCore(app=self)
    
    def create_directory(self):
        if not self.PATH_TO_PLAYLISTS.exists():
            self.PATH_TO_PLAYLISTS.mkdir(parents=True, exist_ok=True)
        if not self.PATH_TO_FAVORITES.exists():
            self.PATH_TO_FAVORITES.mkdir(parents=True, exist_ok=True)

        for genre in self.genres:
            path = self.PATH_TO_PLAYLISTS / genre
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
    
    def load_dialog(self):
        msg = "Выполняется сканирование устройства. Не закрывайте приложение."
        dialog = LoadDialog(app=self, message=msg, parent=self.parent)
        dialog.exec_()
    
    def select_dialog(self):
        dialog = SelectDialog(app=self, parent=self.parent)
        dialog.exec_()
    
    def load_tracks(self, path: str):
        self.set_music_path(path)
        self.frontend.play_menu.sound.load_tracks(path)
    
    def set_music_path(self, path: str):
        data = self.json_manager.load_file()
        loaded = data["loaded"]
        if not loaded:
            self.loaded = True
            data["music"] = str(path)
            data["loaded"] = self.loaded
            self.json_manager.save_file(data)

