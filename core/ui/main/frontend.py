# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Сборка главного окна плеера.

Класс Frontend создаёт всё UI: фон с тенью, шапку, панель плейлистов, 
sublist, список треков, обложку, слайдер и панель управления воспроизведением.
Все виджеты собираются в один вертикальный стек внутри QFrame с градиентным фоном.

Application.start() вызывает init_ui() один раз при запуске.
"""

from typing import Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QSizePolicy)
from core.app.application import Application
from core.ui.widgets.header.header import AppWindowHeader
from core.ui.widgets.playlists.playlist_menu import PlayListMenu
from core.ui.widgets.sublists.sublist_menu import SubListMenu
from core.ui.widgets.tracks.track_menu import TrackMenu
from core.ui.widgets.labels.cover_label import CoverLabel
from core.ui.widgets.sliders.track_slider import MusicSlider
from core.ui.widgets.menu.main_menu import MainPlayMenu
from core.ui.style.styles import MAIN_GRADIENT, apply_shadow


class Frontend:
    """Сборщик главного окна.
    
    Создаёт всю иерархию виджетов и расставляет их в layout'ах.
    Не содержит логики - только композицию. Все обработчики и состояние - 
    в самих виджетах.

    Attributes:
        app: Ссылка на Application (центральный контроллер).
        central: Центральный QWidget окна.
        frame: QFrame с градиентом и тенью.
        header: Шапка (иконка + название + кнопка закрытия).
        playlist_menu: Панель плейлистов.
        sublist_menu: Список поджанров.
        track_menu: Список треков.
        cover_label: Панель обложки + метаданных.
        track_slider: Слайдер перемотки.
        play_menu: Панель управления воспроизведением.
    """

    def __init__(self, app: Optional[Application] = None):
        """Создаёт сборщик UI.
        
        Args:
            app: Экземпляр Application - даёт доступ к frontend-виджетам
                и общему состоянию.
        """
        self.app = app
    
    def init_ui(self):
        """Создаёт всю иерархию виджетов.
        
        Вызывается один раз из Application.start(). После создания всех
        элементов ничего не возвращает - виджеты доступны через атрибуты
        Frontend.

        Структура (сверху вниз):
            1. header - шапка
            2. playlist_menu - панель плейлистов
            3. sublist_menu + track_menu + cover_label (горизонтально)
            4. track_slider - полоса перемотки
            5. play_menu - кнопки управления
        """
        self.central = QWidget()
        self.app.parent.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(20, 20, 30, 30)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(MAIN_GRADIENT)
        apply_shadow(
            self.frame, 
            blur=30, 
            offset_x=8, 
            offset_y=8, 
            color=(155, 105, 181, 140)
        )
        self.main_layout.addWidget(self.frame)

        self.frame_layout_1 = QVBoxLayout(self.frame)
        self.frame_layout_1.setContentsMargins(10, 10, 10, 10)

        self.frame_layout_2 = QVBoxLayout()
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)

        self.header = AppWindowHeader(app=self.app)
        self.frame_layout_2.addWidget(self.header.frame)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 0, 0, 0)

        self.playlist_menu = PlayListMenu(app=self.app)
        self.frame_layout_3.addWidget(self.playlist_menu.frame)

        self.frame_layout_4 = QHBoxLayout()
        self.frame_layout_4.setContentsMargins(0, 5, 0, 0)

        self.sublist_menu = SubListMenu(app=self.app)
        self.frame_layout_4.addWidget(self.sublist_menu.frame)

        self.track_menu = TrackMenu(app=self.app)
        self.frame_layout_4.addWidget(self.track_menu.frame)

        self.cover_label = CoverLabel()
        self.frame_layout_4.addWidget(self.cover_label.frame)

        self.frame_layout_5 = QVBoxLayout()
        self.frame_layout_5.setContentsMargins(0, 0, 0, 0)

        self.track_slider = MusicSlider(app=self.app)
        self.frame_layout_5.addWidget(self.track_slider.frame)

        self.frame_layout_6 = QVBoxLayout()
        self.frame_layout_6.setContentsMargins(0, 0, 0, 0)

        self.play_menu = MainPlayMenu(
            slider=self.track_slider.track_sld, 
            track_menu=self.track_menu, 
            app=self.app
        )
        self.frame_layout_6.addWidget(self.play_menu.frame)

        self.frame_layout_1.addLayout(self.frame_layout_2)
        self.frame_layout_1.addLayout(self.frame_layout_3)
        self.frame_layout_1.addLayout(self.frame_layout_4)
        self.frame_layout_1.addLayout(self.frame_layout_5)
        self.frame_layout_1.addLayout(self.frame_layout_6)
