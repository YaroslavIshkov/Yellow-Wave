# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Панель с обложкой и метаданными трека.

Содержит два класса:
    CoverSongLabel - QLabel с авто-маштабированием и скруглением
    CoverLabel - контейнер (обложка + метаданные + кэш)

Данные приходят из mutagen. Поддерживаются ID3 (MP3), Vorbis
(FLAC, OGG), MP4 (M4A) и WAV. Если обложки нет - рисуется заглушка
'No Image' на фиолетовом фоне.
"""

import base64
import mutagen
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QCloseEvent, QColor, QPainterPath
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QFrame, QSizePolicy, QWidget
from core.tmp.tmp_manager import TempManager
from core.ui.widgets.labels.info_label import InfoTrackLabel
from core.ui.style.styles import TRANSPARENT_LABEL, WHITE_FRAME

log = logging.getLogger("YellowWave")


class CoverSongLabel(QLabel):
    """QLabel с автомасштабированием изображения и скруглением углов.
    
    Отключает встроенный scaledContents и вручную пересчитывает
    pixmap под текущий размер виджета. Скругление делается через
    QPainterPath + clipPath - так края получаются сглаженными, 
    в отличии от QBitmap-маски.

    Attributes:
        radius: Радиус скругления углов в пикселях.
        original_pixmap: Исходная обложка (до масшабирования).
    """

    def __init__(self, radius: int = 10):
        """Создаёт метку для обложки.
        
        Args:
            radius: Радиус скругления углов.
        """
        super().__init__()
        self.radius = radius
        self.original_pixmap = None
        self.setScaledContents(False)  # отключаем встроенное масштабирование
        self.setFixedSize(150, 150)  # минимальный размер, чтобы было видно
        self.setStyleSheet(TRANSPARENT_LABEL)

    def set_pixmap(self, pixmap: QPixmap):
        """Сохраняет оригинал и обновляет отображение.
        
        Args:
            pixmap: Исходная обложка.
        """
        self.original_pixmap = pixmap
        self.update_pixmap()
    
    def set_radius(self, radius: int):
        """Меняет радиус скругления.
        
        Args:
            radius: Новый радиус в пикселях.
        """
        self.radius = radius

    def resizeEvent(self, event: Optional[QEvent]):
        """Пересчитывает масштаб при изменении размера виджета.
        
        Args:
            event: Событие изменения размера от Qt.
        """
        self.update_pixmap()
        super().resizeEvent(event)

    def update_pixmap(self):
        """Масштабирует обложку под текущий размер и скругляет углы.
        
        Использует KeepAspectRatioByExpanding - картинка заполняет
        весь квадрат, лишнее обрезается по центру. Результат рисуется
        на прозрачном QPixmap через clipPath с Antialiasing.
        """
        if self.original_pixmap is None or self.original_pixmap.isNull():
            return

        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        # Масштабируем с сохранением пропорций и сглаживанием
        scaled = self.original_pixmap.scaled(
            w, h,
            Qt.KeepAspectRatioByExpanding,    # вписываем в размеры
            Qt.SmoothTransformation    # сглаживание
        )

        x_offset = (scaled.width() - w) // 2
        y_offset = (scaled.height() - h) // 2

        result = QPixmap(w, h)
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(-x_offset, -y_offset, scaled)
        painter.end()

        self.setPixmap(result)


class CoverLabel(QWidget):
    """Панель с обложкой и метаданными текущего трека.
    
    Вертикальный стек: сверху обложка (CoverSongLabel), снизу - 
    метаднные (InfoTrackLabel). При загрузке трека: 
        1. Читает теги через mutagen
        2. Извлекает обложку (если есть)
        3. Кэширует обложку во временный PNG
        4. Обновляет и метку обложки, и метаданные
    
    Attributes:
        temp_manager: Кэш обложек во временной папке ОС.
        cover_lbl: QLabel с обложкой.
        labels: InfoTrackLabel с пятью строками метаданных.
    """

    def __init__(self):
        """Создаёт панель с пустой обложкой и метаданными."""
        super().__init__()
        self.temp_manager = TempManager()

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(WHITE_FRAME)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)

        # Создаём метку для обложки
        self.cover_lbl = CoverSongLabel(radius=10)
        self.frame_layout_2.addWidget(self.cover_lbl, alignment=Qt.AlignCenter)

        self.labels = InfoTrackLabel()
        self.frame_layout_2.addWidget(self.labels)

    def load_track(self, track_path: Union[Path, str]):
        """Загружает обложку и метаданные трека.
        
        Открывает файл через mutagen (с fallback на явные классы), 
        извлекает обложку, кэширует её и обновляет UI. Если обложки
        нет - рисует заглушку 'No Image'.

        Args:
            track_path: Путь к аудиофайлу (Path или str).
        """
        track_path = (str(track_path) 
            if isinstance(track_path, Path) else track_path)
        
        # Загружаем обложку трека
        try:
            audio = mutagen.File(track_path)
            if audio is None:
                audio = self._try_open_audio(track_path)
        except Exception as e:
            log.error(f"Не удалось открыть {track_path}: {e}")
            audio = None
        
        pixmap = self.extract_cover(audio)
        data = self.get_track_info(track_path)
        self.labels.set_track_info(data)

        if pixmap and not pixmap.isNull():
            cover_path = self.temp_manager.save_cover(track_path, pixmap)
            self.cover_lbl.set_pixmap(QPixmap(cover_path))
        else:
            # Если файла нет — создаём заглушку
            self._make_dummy_cover()
    
    def clear(self):
        """Сбрасывает обложку и метаданные в состояние по умолчанию.
        
        Рисует заглушку 'No Image' и выставляет все поля метаданных
        в 'Неизвестно'. Вызывается например, при удалении текущего
        поджанра.
        """
        self._make_dummy_cover()

        self.labels.set_track_info(
            {
                'title': 'Неизвестно', 
                'artist': 'Неизвестно', 
                'album': 'Неизвестно', 
                'duration': 0, 
                'year': 'Неизвестно',
            }
        )
    
    def _make_dummy_cover(self):
        """Создаёт заглушку для обложки трека, если нет картинки."""
        dummy = QPixmap(300, 300)
        dummy.fill(QColor(100, 100, 150))
        painter = QPainter(dummy)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        font = painter.font()
        font.setPointSize(28)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(230, 230, 255))
        painter.drawText(dummy.rect(), Qt.AlignCenter, "No Image")
        painter.end()

        self.cover_lbl.set_pixmap(dummy)

    def closeEvent(self, event: Optional[QCloseEvent] = None):
        """Удаляет временные файлы обложек при закрытии приложения.
        
        Args:
            event: Событие закрытия от Qt.
        """
        self.temp_manager.clear_temp()
        event.accept()
    
    def extract_cover(self, audio: Optional[Any] = None) -> Optional[QPixmap]:
        """Извлекает обложку из тегов аудиофайла.
        
        Поддерживает четыре источника (по порядку):
            1. ID3 (MP3) - ключи APIC / PIC
            2. FLAC - audio.pictures
            3. OGG Vorbis - metadata_block_picture / COVERART (base64)
            4. MP4 (M4A) - covr
        
        Args:
            audio: Объект mutagen.File или None.
        
        Returns:
            QPixmap с обложкой или None, если обложки нет.
        """
        if audio is None:
            return None
        
        cover_data = None
        tags = getattr(audio, 'tags', None)

        if tags is not None:
            for key in tags.keys():
                if key.startswith('APIC') or key.startswith('PIC'):
                    cover_data = tags[key].data
                    break

        if cover_data is None and hasattr(audio, 'pictures') and audio.pictures:
            cover_data = audio.pictures[0].data
        
        if cover_data is None and tags is not None:
            for key in ('metadata_block_picture', 'COVERART'):
                if key in tags:
                    try:
                        value = tags[key][0] if isinstance(tags[key], list) else tags[key]
                        cover_data = base64.b64decode(value)
                        break
                    except Exception:
                        pass
        
        if cover_data is None and tags is not None and 'covr' in tags:
            cover_data = bytes(tags['covr'][0])

        if cover_data is None:
            return None

        pixmap = QPixmap()
        pixmap.loadFromData(cover_data)
        return pixmap
    
    def _get_tag(self, 
                    tags: dict, 
                    keys: tuple, 
                    default: str = 'Неизвестно') -> str:
        """Универсальный доступ к тегам разных форматов.
        
        ID3 (MP3) возвращает списки, Vorbis (FLAC, OGG) - строки, 
        MP4 (M4A) - тоже списки. Метод приводит всё к строке и
        возвращает первое найденное значение.

        Args:
            tags: Словарь тегов (audio.tags) или None.
            keys: Кортеж возможных имён ключей для перебора.
            default: Что вернуть, если ничего не найдено.
        
        Returns:
            Значение тега как строка или default.
        """
        if tags is None:
            return default
        for key in keys:
            if key in tags:
                value = tags[key]
                if isinstance(value, list):
                    value = value[0] if value else ''
                else:
                    value = str(value)
                if value:
                    return str(value)
        return default

    def get_track_info(self, file_path: str) -> dict:
        """Извлекает метаданные трека и возвращает словарь.
        
        Ключи: title, artist, album, duration, year. Если тег не
        найден - 'Неизвестно'. Если название пустое - берётся имя
        файла (с парсингом 'Artist - Title').

        Args:
            file_path: Путь к аудиофайлу.
        
        Returns:
            Словарь с пятью ключами (всегда заполнен).
        """
        try:
            audio = mutagen.File(file_path)

            if audio is None:
                audio = self._try_open_audio(file_path)
            
            if audio is None:
                return self._empty_info()
            
            tags = getattr(audio, 'tags', None)

            info = {
                'title': self._get_tag(tags, ('TIT2', 'title', '\xa9nam')), 
                'artist': self._get_tag(tags, ('TPE1', 'artist', '\xa9ART')), 
                'album': self._get_tag(tags, ('TALB', 'album', '\xa9alb')),
            }

            year_str = self._get_tag(tags, 
                ('TDRC', 'TYER', 'date', 'year', '\xa9day'), 
                default='Неизвестно')
            info['year'] = (year_str[:4] 
                if year_str != 'Неизвестно' else 'Неизвестно')
            
            info['duration'] = (int(audio.info.length) 
                if hasattr(audio, 'info') and audio.info else 0)
            
            if info['title'] == 'Неизвестно':
                stem = Path(file_path).stem
                if ' - ' in stem:
                    artist, _, title = stem.partition(' - ')
                    info['artist'] = artist.strip()
                    info['title'] = title.strip()
                else:
                    info['title'] = stem

            return info
        except Exception as e:
            log.error(f"Ошибка чтения тегов {file_path}: {e}")
            return self._empty_info()
    
    def _try_open_audio(self, file_path: str) -> Any:
        """Пробует открыть файл явным классом mutagen.
        
        Используется, когда mutagen.File() не смог определить формат
        автоматически (sniffing по заголовку не сработал).

        Args:
            file_path: Путь к аудиофайлу.
        
        Returns:
            Объект mutagen соответствующего класса или None при ошибке.
        """
        ext = Path(file_path).suffix.lower()

        if ext == '.wav':
            try:
                from mutagen.wave import WAVE
                return WAVE(file_path)
            except Exception:
                return None
        
        if ext == '.flac':
            try:
                from mutagen.flac import FLAC
                return FLAC(file_path)
            except Exception:
                return None
        
        if ext == '.ogg':
            try:
                from mutagen.oggvorbis import OggVorbis
                return OggVorbis(file_path)
            except Exception:
                return None
        
        if ext == '.mp3':
            try:
                from mutagen.mp3 import MP3
                return MP3(file_path)
            except Exception:
                return None
        
        if ext == '.m4a':
            try:
                from mutagen.m4a import M4A
                return M4A(file_path)
            except Exception:
                return None
        
        return None
    
    def _empty_info(self) -> Dict[str, Union[str, int]]:
        """Пустая структура с дефолтами - чтобы не падать в UI.
        
        Returns:
            Словарь с пятью ключами, все значения 'Неизвестно' или 0.
        """
        return {
            'title': 'Неизвестно', 
            'artist': 'Неизвестно', 
            'album': 'Неизвестно', 
            'duration': 0, 
            'year': 'Неизвестно',
        }
