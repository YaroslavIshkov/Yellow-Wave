# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Утилиты для работы с экраном.

Пока - только центрирование окна с возможностью смещения от центра.
Смещение (padx, pady) задаётся относительно центра экрана, что
позволяет 'прижать' окно к нужной части монитора без вычисления координат.
"""

from typing import Optional
from PyQt5.QtWidgets import QApplication, QMainWindow


class Screen:
    """Работа с геометрией экрана и позиционированием окна."""
    def __init__(self):
        """Создаёт объект-обёртку для работы с экраном."""
        pass
    
    def center_window(self, 
                        window: Optional[QMainWindow] = None, 
                        width: int = 1200, 
                        height: int = 600, 
                        padx: int = 0, 
                        pady: int = 20):
        """Центрирует окно на экране с возможностью смещения.
        
        Координаты считаются от центра рабочей области монитора:
            win_x = центр_экрана - половина_ширины - padx
            win_y = центр_экрана - половина_высоты - pady
        Знаки padx/pady: положительное значение сдвигает окно
        влево/вверх от центра, отрицательное - вправо/вниз.
        
        Args:
            window: Окно для позиционирования. Если None - метод упадёт
                при вызове setGeometry.
            width: Ширина окна в пикселях.
            height: Высота окна в пикселях.
            padx: Горизонтальное смещение от центра (см. выше).
            pady: Вертикальное смещение от центра (см. выше).
        """
        screen_num = QApplication.desktop().screenNumber(window)
        screen_rect = QApplication.desktop().availableGeometry(screen_num)
        monitor_width = screen_rect.width()
        monitor_height = screen_rect.height()
        win_x = screen_rect.x() + (monitor_width - width) // 2 + padx
        win_y = screen_rect.y() + (monitor_height - height) // 2 + pady
        window.setGeometry(win_x, win_y, width, height)
