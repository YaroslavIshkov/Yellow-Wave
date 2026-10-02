# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Правая панель с метаданными текущего трека.

Показывает пять полей: название, альбом, исполнитель, длительность и год.
Данные приходят из cover_label.get_track_info() - там используется mutagen
и универсальный доступ к тегам (ID3, Vorbis, MP4). Длинные строки обрезаются
через textwrap.shorten().
"""

import textwrap
from typing import Any, Optional
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QSizePolicy
from core.ui.style.styles import WHITE_FRAME, INFO_LABEL


class InfoTrackLabel(QWidget):
    """Панель метаданных трека.
    
    Вертикальный список из пяти QLabel на белом фоне QFrame. Все метки имеют
    одинаковый стиль (INFO_LABEL) и высоту 40px.
    Данные обновляются одним вызовом set_track_info().

    Attributes:
        central_layout: Внешний layout виджета.
        frame: Белый QFrame с закруглёнными углами.
        frame_layout: Внутренний layout с метками.
        title_lbl: Название трека.
        album_lbl: Альбом.
        artist_lbl: Исполнитель.
        duration_lbl: Длительность в формате MM:SS.
        year_lbl: Год выпуска.
    """

    def __init__(self):
        """Создаёт панель с пятью пустыми метками."""
        super().__init__()
        self.central_layout = QVBoxLayout(self)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(WHITE_FRAME)
        self.central_layout.addWidget(self.frame)

        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(3)

        self.title_lbl = QLabel()
        self.title_lbl.setText("Название: Неизвестно")
        self.title_lbl.setFixedHeight(40)
        self.title_lbl.setStyleSheet(INFO_LABEL)
        self.frame_layout.addWidget(self.title_lbl)

        self.album_lbl = QLabel()
        self.album_lbl.setText("Альбом: Неизвестно")
        self.album_lbl.setFixedHeight(40)
        self.album_lbl.setStyleSheet(INFO_LABEL)
        self.frame_layout.addWidget(self.album_lbl)

        self.artist_lbl = QLabel()
        self.artist_lbl.setText("Исполнитель: Неизвестно")
        self.artist_lbl.setFixedHeight(40)
        self.artist_lbl.setStyleSheet(INFO_LABEL)
        self.frame_layout.addWidget(self.artist_lbl)

        self.duration_lbl = QLabel()
        self.duration_lbl.setText("Длительность: Неизвестно")
        self.duration_lbl.setFixedHeight(40)
        self.duration_lbl.setStyleSheet(INFO_LABEL)
        self.frame_layout.addWidget(self.duration_lbl)

        self.year_lbl = QLabel()
        self.year_lbl.setText("Год: Неизвестно")
        self.year_lbl.setFixedHeight(40)
        self.year_lbl.setStyleSheet(INFO_LABEL)
        self.frame_layout.addWidget(self.year_lbl)

    def set_track_info(self, track_info: dict, width: int = 20):
        """Обновляет метки данными из словаря track_info.
        
        Все строки (кроме duration и year) обрезаются через textwrap.shorten()
        до указанной ширины, чтобы не вылезать за границы панели. Длительность
        форматируется в MM:SS.

        Args:
            track_info: Словарь с ключами title, album, artist, duration (секунды),
                year. Пустой словарь игнорируется.
            width: Максимальная длина строк для обрезки.
        """
        if not track_info:
            return
        short_title = textwrap.shorten(
            track_info.get('title', 'Неизвестно'), 
            width=width, 
            placeholder='...'
        )
        short_album = textwrap.shorten(
            track_info.get('album', 'Неизвестно'), 
            width=width, 
            placeholder='...'
        )
        short_artist = textwrap.shorten(
            track_info.get('artist', 'Неизвестно'), 
            width=width, 
            placeholder='...'
        )
        duration = self.format_time(track_info.get('duration', 'Неизвестно'))
        self.title_lbl.setText(f"Название: {short_title}")
        self.album_lbl.setText(f"Альбом: {short_album}")
        self.artist_lbl.setText(f"Исполнитель: {short_artist}")
        self.duration_lbl.setText(f"Длительность: {duration}")
        self.year_lbl.setText(f"Год: {track_info.get('year', 'Неизвестно')}")

    def format_time(self, seconds: int) -> str:
        """Форматирует секунды в MM:SS.
        
        Args:
            seconds: Количество секунд.
        
        Returns:
            Строка вида '03:22'.
        """
        if seconds < 0:
            seconds = 0
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
