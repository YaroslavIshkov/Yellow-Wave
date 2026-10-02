# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Список треков текущей папки.

Центральный QListWidget с треками из текущей выбранной папки.
Двойной клик запускает воспроизведение: останавливает текущий
трек, обновляет информацию в панели метаданных и запускает новый.
Ширина фиксирована (500px), высота растягивается.
"""

from typing import Optional
from PyQt5.QtWidgets import (QWidget, QListWidget, QFrame, QVBoxLayout, 
    QSizePolicy)
from PyQt5.QtCore import Qt
from core.app.application import Application
from core.ui.style.styles import TRANSPARENT_FRAME, WHITE_LIST


class TrackMenu(QWidget):
    """Виджет со списком треков текущей папки.
    
    Двойной клик по треку:
        1. Обновляет sound.current на выбранный индекс
        2. Перерисовывает метаданные и обложку (update_track_info)
        3. Останавливает текущее воспроизведение (stop)
        4. Запускает новый трек (toggle_play)
        5. Обновляет иконку кнопки Play (на Pause)
    
    Attributes:
        app: Ссылка на Application.
        track_list: QListWidget с именами файлов.
    """

    def __init__(self, app: Optional[Application] = None):
        """Создаёт виджет с пустым списком треков.
        
        Args:
            app: Экземпляр Application.
        """
        super().__init__()
        self.app = app

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setFixedWidth(500)
        self.frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.frame.setStyleSheet(TRANSPARENT_FRAME)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)

        self.track_list = QListWidget(self)
        self.track_list.doubleClicked.connect(self.on_item_clicked)
        self.track_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.track_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.track_list.setStyleSheet(WHITE_LIST)
        self.frame_layout_2.addWidget(self.track_list)

    def on_item_clicked(self):
        """Обработчик двойного клика по треку - запускает воспроизведение.
        
        Последовательность важна: сначала обновляем состояние SoundEngine
        (current + info), потом останавливаем текущий трек, потом запускаем
        новый. Иначе stop() сбросит только что установленный current.
        """
        selected_index = self.track_list.currentRow()
        if selected_index >= 0:
            sound = self.app.frontend.play_menu.sound
            sound.current = selected_index
            sound.update_track_info(selected_index)
            sound.play_music(selected_index)
            sound.started = True
            sound.paused = False
            self.app.frontend.play_menu.play_button.update_icon()
    
    def get_current_index(self) -> Optional[int]:
        """Возвращает индекс выделенного трека.
        
        Принудительно ставит фокус на список (чтобы выделение было видимым), 
        затем читает currentRow(). Если ничего не выбрано - возвращает None
        (важно: не -1 а именно None).

        Returns:
            Индекс выделенного трека или None.
        """
        self.track_list.setFocus()
        selected_index = self.track_list.currentRow()
        if selected_index >= 0:
            return selected_index
