# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Точка входа Yellow Wave Music Player.

Инициализирует QApplication, настраивает шрифт и рендеринг, 
создаёт главное окно и запускает цикл обработки событий Qt.
"""

import io
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from functools import cached_property
from core.logger.logger import setup_logger, install_excepthook

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtCore import Qt

if TYPE_CHECKING:
    from core.screen.screen import Screen
    from core.app.application import Application

if sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', 
        errors='replace')
if sys.stderr is not None:
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', 
        errors='replace')


class MainWindow(QMainWindow):
    """Главное окно приложения.
    
    Frameless-окно с прозрачным фоном. Задаёт размеры, 
    центрирует себя на экране, инициализирует Application и навешивает
    горячую клавишу F11 для переключения полноэкранного режима.
    
    Attributes:
        app: Ссылка на QApplication.
        width: Ширина окна в пикселях.
        height: Высота окна в пикселях.
        padx: Горизонтальное смещение от центра экрана.
        pady: Вертикальное смещение от центра экрана.
        is_fullscreen: Находится ли окно в полноэкранном режиме.
        normal_geometry: Сохранённая геометрия до входа в fullscreen.
    """

    def __init__(self):
        """Создаёт главное окно."""
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.width = 1360
        self.height = 290
        self.padx = 5
        self.pady = -235
        
        self.is_fullscreen = False
        self.normal_geometry = None

        self.screen.center_window(self, 
            self.width, self.height, self.padx, self.pady)
        self.application.start()

        self.shortcut = QShortcut(QKeySequence("F11"), self)
        self.shortcut.activated.connect(self.toggle_fullscreen)

    @cached_property
    def screen(self) -> "Screen":
        """Ленивая инициализация Screen (утилиты для работы с монитором).
        
        Создание выполняется внутри свойства, чтобы избежать циклических
        зависимостей при старте приложения.
        """
        from core.screen.screen import Screen
        return Screen()
    
    @cached_property
    def application(self) -> "Application":
        """Ленивая инициализация Application (центральный контроллер).
        
        Application создаётся при первом обращении, что позволяет
        сначала настроить окно, а потом запустить логику.
        """
        from core.app.application import Application
        return Application(parent=self)

    def toggle_fullscreen(self):
        """Переключает полноэкранный режим.
        
        При входе сохраняет текущую геометрию окна, при выходе
        - восстанавливает её. Привязывается к F11.
        """
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
    log_root = Path(__file__).resolve().parent
    logger = setup_logger(log_root)
    install_excepthook(logger)
    logger.info("Yellow Wave Music Player started")

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    font = app.font()
    font.setStyleStrategy(QFont.PreferAntialias)
    font.setHintingPreference(QFont.PreferNoHinting)
    app.setFont(font)

    app.setStyleSheet("""
        QToolTip {
            background-color: #3D1A5E; 
            color: white; 
            border: 1px solid #9B69B5; 
            border-radius: 3px; 
            padding: 4px 8px; 
            font-family: Segoe UI; 
            font-size: 15px;
        }
    """)

    window = MainWindow()
    window.show()

    data = window.application.json_manager.load_file()
    loaded = data.get("loaded", False)
    music = data.get("music")

    if not loaded or not music:
        window.application.load_dialog()
    else:
        window.application.load_tracks(music)
    
    exit_code = app.exec_()
    logger.info("Yellow Wave Player stopped")
    sys.exit(exit_code)
