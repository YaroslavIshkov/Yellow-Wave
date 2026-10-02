# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Менеджер JSON-состояния приложения.

Читает и записывает config/arguments.json - хранилище состояния
плеера (текущая папка, избранное, флаг загрузки). Запись атомарная: 
сначала во временный файл, потом подмена через os.replace, чтобы
при сбое не потерять старые данные.
"""

import os
import json
import logging
from pathlib import Path

log = logging.getLogger("YellowWave")


class JsonManager:
    """Управляет чтением и записью JSON-состояния.
    
    Все ошибки логируются и не бросаются наружу - методы возвращают
    безопасные значения (пустой словарь при чтении, ничего при записи).
    Это позволяет приложению запускаться даже при повреждённом JSON.
    
    Attributes:
        config_path: Путь к папке config.
        file_path: Путь к файлу arguments.json.
    """

    def __init__(self):
        """Определяет пути к config/arguments.json относительно проекта."""
        self.config_path = Path(__file__).parents[2] / "config"
        self.file_path = self.config_path / "arguments.json"
    
    def create_file(self, data: dict):
        """Создаётся JSON-файл с начальными данными, если его нет.
        
        Если папка config отсутствует - создаёт. Если файл уже есть - 
        ничего не делает (не перезаписывает существующее состояние).
        
        Args:
            data: Начальная структура JSON.
        """
        try:
            if not self.config_path.exists():
                self.config_path.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                self.save_file(data)
        except Exception as e:
            log.error(f"Не удалось создать {self.file_path}: {e}")
    
    def load_file(self) -> dict:
        """Читает JSON-файл.
        
        При любой ошибке (нет файла, битый JSON, проблемы с доступом)
        возвращает пустой словарь - вызывающий код должен использовать
        .get() с дефолтами.
        
        Returns:
            Словарь с состоянием или {} при ошибке.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            log.error(f"JSON повреждён: {e}")
            return {}
        except OSError as e:
            log.error(f"Ошибка чтения {self.file_path}: {e}")
            return {}
    
    def save_file(self, data: dict):
        """Атомарно записывает данные в JSON.
        
        Сначала пишет во временный файл .json.tmp, потом заменяет
        оригинал через os.replace. Если что-то упадёт между - старый
        файл останется целым.
        
        Args:
            data: Словарь для сохранения.
        """
        try:
            if not self.config_path.exists():
                self.config_path.mkdir(parents=True, exist_ok=True)
            
            tmp_path = self.file_path.with_suffix(".json.tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            os.replace(tmp_path, self.file_path)
        except OSError as e:
            log.error(f"Ошибка записи {self.file_path}: {e}")
