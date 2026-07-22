# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

import mutagen
from pathlib import Path
from typing import Optional, Union
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QBitmap, QPainter, QCloseEvent, QColor
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QFrame, QSizePolicy, QWidget
from core.tmp.tmp_manager import TempManager
from core.ui.widgets.labels.info_label import InfoTrackLabel


class CoverSongLabel(QLabel):
    """
    QLabel с автоматическим масштабированием изображения 
    с сохранением пропорций и сглаживанием. Протестировано: 11.07.2026
    """
    def __init__(self, parent=None, radius=10):
        super().__init__(parent)
        self.radius = radius
        self.original_pixmap = None
        self.setScaledContents(False)  # отключаем встроенное масштабирование
        self.setFixedSize(150, 150)  # минимальный размер, чтобы было видно
        self.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 10px;
            }
        """)

    def set_pixmap(self, pixmap):
        """Сохраняет оригинальное изображение и обновляет отображение."""
        self.original_pixmap = pixmap
        self.update_pixmap()
    
    def set_radius(self, radius):
        self.radius = radius
        self.update_mask()

    def resizeEvent(self, event):
        """При изменении размера метки пересчитываем масштаб."""
        self.update_pixmap()
        self.update_mask()
        super().resizeEvent(event)

    def update_pixmap(self):
        """Масштабирует изображение под текущий размер метки."""
        if self.original_pixmap is None or self.original_pixmap.isNull():
            return

        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        # Масштабируем с сохранением пропорций и сглаживанием
        scaled = self.original_pixmap.scaled(
            w, h,
            Qt.KeepAspectRatio,        # вписываем в размеры
            Qt.SmoothTransformation    # сглаживание
        )
        self.setPixmap(scaled)
    
    def update_mask(self):
        if self.width() <= 0 or self.height() <= 0:
            return
        
        mask = QBitmap(self.size())
        mask.fill(Qt.white)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.black)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.end()
        self.setMask(mask)


class CoverLabel(QWidget):
    def __init__(self):
        super().__init__()
        self.temp_manager = TempManager()

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setFixedWidth(170)
        self.frame.setStyleSheet("""
            QFrame {
                background: #FFFFFF; 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout()
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)
        self.frame.setLayout(self.frame_layout_2)

        # Создаём метку для обложки
        self.cover_lbl = CoverSongLabel(radius=10)
        self.frame_layout_2.addWidget(self.cover_lbl, alignment=Qt.AlignCenter)

        self.labels = InfoTrackLabel()
        self.frame_layout_2.addWidget(self.labels.title_lbl)
        self.frame_layout_2.addWidget(self.labels.album_lbl)
        self.frame_layout_2.addWidget(self.labels.artist_lbl)
        self.frame_layout_2.addWidget(self.labels.duration_lbl)
        self.frame_layout_2.addWidget(self.labels.year_lbl)

    def load_track(self, track_path: Union[Path, str]):
        track_path = (str(track_path) 
            if isinstance(track_path, Path) else track_path)
        # Загружаем обложку трека
        audio = mutagen.File(track_path)
        pixmap = self.extract_cover(audio)
        data = self.get_track_info(track_path)
        self.labels.set_track_info(data)

        if pixmap and not pixmap.isNull():
            cover_path = self.temp_manager.save_cover(track_path, pixmap)
            self.cover_lbl.set_pixmap(QPixmap(cover_path))
        else:
            # Если файла нет — создаём заглушку
            dummy = QPixmap(300, 300)
            dummy.fill(QColor(100, 100, 150))
            painter = QPainter(dummy)
            painter.setPen(Qt.white)
            painter.drawText(dummy.rect(), Qt.AlignCenter, "No Image")
            painter.end()
            self.cover_lbl.set_pixmap(dummy)

    def closeEvent(self, event: Optional[QCloseEvent] = None) -> None:
        self.temp_manager.clear_temp()
        event.accept()
    
    def extract_cover(self, audio):
        cover_data = None
        if audio is None:
            return None

        if hasattr(audio, 'tags') and audio.tags is not None:
            for key in audio.tags.keys():
                if key.startswith('APIC') or key.startswith('PIC'):
                    cover_data = audio.tags[key].data
                    break

        if cover_data is None and hasattr(audio, 'pictures') and audio.pictures:
            cover_data = audio.pictures[0].data

        if cover_data is None:
            return None

        pixmap = QPixmap()
        pixmap.loadFromData(cover_data)
        return pixmap

    def get_track_info(self, file_path: str) -> dict:
        try:
            audio = mutagen.File(file_path)
            if audio is None:
                return {}

            info = {}
            tags = audio.tags if hasattr(audio, 'tags') else {}

            info['title'] = tags.get('TIT2', ['Неизвестно'])[0] if 'TIT2' in tags else 'Неизвестно'
            info['artist'] = tags.get('TPE1', ['Неизвестно'])[0] if 'TPE1' in tags else 'Неизвестно'
            info['album'] = tags.get('TALB', ['Неизвестно'])[0] if 'TALB' in tags else 'Неизвестно'
            info['duration'] = int(audio.info.length) if hasattr(audio.info, 'length') else 0

            year_keys = ('TDRC', 'TYER', 'TDRC:', 'TYER:', 'date')
            year = 'Неизвестно'
            for key in year_keys:
                if key in tags.keys():
                    year_str = str(tags[key][0])
                    if year_str:
                        year = year_str[:4]
                        break
            info['year'] = year

            return info
        except TypeError as e:
            print(e)
