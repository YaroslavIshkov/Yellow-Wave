import sys
from functools import lru_cache
from typing import Optional
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, app: Optional[QApplication] = None):
        super().__init__()
        self.app = app
        self.WIDTH = 1360
        self.HEIGHT = 200
        self.PADX = -680
        self.PADY = 125
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.is_fullscreen = False
        self.normal_geometry = None

        self.screen.center_window(self, 
            self.WIDTH, self.HEIGHT, self.PADX, self.PADY)
        self.application.start()

        self.shortcut = QShortcut(QKeySequence("F11"), self)
        self.shortcut.activated.connect(self.toggle_fullscreen)

    @property
    @lru_cache(maxsize=None)
    def screen(self):
        from core.screen.screen import Screen
        return Screen(app=self.app)
    
    @property
    @lru_cache(maxsize=None)
    def application(self):
        from core.app.application import Application
        return Application(app=self.app, parent=self)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_fullscreen = False
        else:
            self.normal_geometry = self.geometry()
            self.showFullScreen()
            self.is_fullscreen = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    data = window.application.json_manager.load_file()
    loaded = data["loaded"]
    if not loaded:
        window.application.load_dialog()
    else:
        music = data["music"]
        window.application.load_tracks(music)
    sys.exit(app.exec_())
