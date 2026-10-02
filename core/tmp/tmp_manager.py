# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Временное хранилище для обложек треков.

Обложки извлекаются из тегов аудиофайлов и сохраняются как PNG
во временную папку ОС. Имя файла - MD5-хэш от пути в треку, что
исключает повторную запись одной и той же обложки.
"""

import shutil
import hashlib
import tempfile
from pathlib import Path
from PyQt5.QtGui import QPixmap

class TempManager:
    """Управляет временными PNG-файлами обложек.
    
    Все обложки складываются в <tempdir>/<covers>/. Имя каждого файла - 
    MD5-хэш от пути к треку. Это гарантирует уникальность имён даже
    для треков с одинаковыми названиями в разных папках.
    
    Attributes:
        temp_dir: Путь к папке с обложками во временной директории ОС.
    """

    def __init__(self):
        """Сохраняет папку для обложек, если её ещё нет."""
        self.temp_dir = Path(tempfile.gettempdir()) / "covers"
        self.temp_dir.mkdir(exist_ok=True)

    def save_cover(self, track_path: str, pixmap: QPixmap) -> str:
        """Сохраняет обложку трека во временный файл.
        
        Имя файла - MD5-хэш от пути к треку. Если файл уже существует,
        повторно не сохраняется (экономия I/O при повторном открытии
        того же трека).
        
        Args:
            track_path: Путь к аудиофайлу (используется для хэша).
            pixmap: Обложка в виде QPixmap.
        
        Returns:
            Абсолютный путь к сохранённому PNG-файлу.
        """
        hash_name = hashlib.md5(track_path.encode()).hexdigest()
        cover_path = self.temp_dir / f"{hash_name}.png"

        if not cover_path.exists():
            pixmap.save(str(cover_path), "PNG")

        return str(cover_path)

    def clear_temp(self):
        """Удаляет всю папку с обложками.
        
        Вызывается при закрытии приложения, чтобы не оставлять мусор
        во временной папке ОС.
        """
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
