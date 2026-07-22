# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

import shutil
import hashlib
import tempfile
from pathlib import Path
from PyQt5.QtGui import QPixmap

class TempManager:
    """Класс реализующий хранилище для временных файлов. Протестировано: 09.07.2026"""
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "covers"
        self.temp_dir.mkdir(exist_ok=True)

    def save_cover(self, track_path: str, pixmap: QPixmap) -> str:
        hash_name = hashlib.md5(track_path.encode()).hexdigest()
        cover_path = self.temp_dir / f"{hash_name}.png"

        if not cover_path.exists():
            pixmap.save(str(cover_path), "PNG")

        return str(cover_path)

    def clear_temp(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)