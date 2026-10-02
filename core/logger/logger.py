# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Настройка логирования для всего приложения.

Создаёт logger с ротацией файлов (1 МБ х 4 файла) и выводом
в консоль. Плюс - перехватчик необработанных исключений, который
пишет их в лог вместо тихого падения.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType
from typing import Optional, Type


def setup_logger(project_root: Path) -> logging.Logger:
    """Настраивает и возвращает логгер приложения. 
    
    Логи пишутся в <project_root>/logs/player.log с ротацией:
    при достижении 1 МБ файл переименовывается в .1, старый .1 -> .2, 
    и так до .3. Всего хранится 4 файла (~4 МБ максимум).

    В консоль выводятся только INFO и выше - чтобы DEBUG не спамил.
    В файл пишется всё, включая DEBUG.

    Повторный вызов очищает старые handlers - защита от дублирования
    сообщений, если setup_logger вызван дважды.

    Args:
        project_root: Корень проекта, где будет создана папка logs.
    
    Returns:
        Настроенный logging.Logger с именем "YellowWave".
    """
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("YellowWave")
    logger.setLevel(logging.DEBUG)

    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_dir / "player.log", 
        maxBytes=1_000_000, 
        backupCount=3, 
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    if sys.stdout is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(fmt)
        logger.addHandler(console_handler)

    return logger

def install_excepthook(logger: logging.Logger):
    """Устанавливает глобальный перехватчик необработанных исключений.
    
    Заменяет sys.excepthook на функцию, которая логирует исключение
    через logger.critical с полным трейсбеком, а потом вызывает
    оригинальный хук (чтобы traceback всё равно вывелся в консоль).
    
    KeyboardInterrupt (Ctrl+C) не логируется - это нормальный выход, 
    а не ошибка.
    
    Args:
        logger: Логгер, в который писать критические ошибки.
    """
    def handler(
        exc_type: Type[BaseException], 
        exc_value: BaseException, 
        exc_tb: Optional[TracebackType],
    ):
        """Внутренний обработчик для sys.excepthook.
        
        Args:
            exc_type: Тип исключения.
            exc_value: Экземпляр исключения.
            exc_tb: Traceback исключения.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.critical(
            "Необработанное исключение", 
            exc_info=(exc_type, exc_value, exc_tb),
        )
        sys.__excepthook__(exc_type, exc_value, exc_tb)
    
    sys.excepthook = handler
