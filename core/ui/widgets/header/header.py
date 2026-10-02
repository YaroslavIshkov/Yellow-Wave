# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Шапка (header) главного окна.

Содержит иконку приложения, название и кнопку закрытия.
Использует frameless-режим, поэтому перетаскивания окна за шапку
организует Qt (через MainWindow).
"""

from typing import Optional
from PyQt5.QtWidgets import (QFrame, QLabel, QHBoxLayout, 
    QPushButton, QSizePolicy, QVBoxLayout, QWidget, QApplication)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from core.app.application import Application
from core.ui.style.styles import (TRANSPARENT_FRAME, TRANSPARENT_LABEL, 
    DIALOG_LABEL, TRANSPARENT_BUTTON)


class AppIcon:
    """Загрузчик иконки приложение.
    
    Отдельный класс нужен, чтобы единообразно маштабировать иконки
    с сохранением пропорций (без искажений).
    
    Attributes:
        path: Путь к файлу иконки.
    """

    def __init__(self, path: str):
        """Создаёт загрузчик икноки.
        
        Args:
            path: Путь к PNG/ICO-файлу.
        """
        self.path = path

    def icon(self, w: int, h: int) -> QPixmap:
        """Загружает иконку и маштабирует её под заданный размер.
        
        Args:
            w: Ширина в пикселях.
            h: Высота в пикселях.
        
        Returns:
            Готовый QPixmap с сохранением пропорций.
        """
        return QPixmap(self.path).scaled(
            w, h, 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        )


class ButtonIcon:
    """Загрузчик иконки для кнопки (возвращает QIcon, не QPixmap).
    
    QPushButton принимает именно QIcon, поэтому оборачиваем QPixmap.
    
    Attributes:
        path: Путь к файлу иконки.
    """

    def __init__(self, path: str):
        """Создаёт загрузчик иконки для кнопки.
        
        Args:
            path: Путь к PNG/ICO-файлу.
        """
        self.path = path
    
    def icon(self, w: int, h: int) -> QIcon:
        """Загружает иконку и масштабирует её, возвращает как QIcon.
        
        Args:
            w: Ширина в пикселях.
            h: Высота в пикселях.
        
        Returns:
            QIcon, готовый для setIcon().
        """
        return QIcon(
            QPixmap(self.path).scaled(
                w, h, 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
        )


class AppWindowHeader(QWidget):
    """Шапка главного окна приложения.
    
    Композиция: слева иконка и название, справа - кнопка закрытия.
    Сама шапка прозрачная, реальный фон рисует QFrame внутри.
    
    Attributes:
        app: Ссылка на Application (оттуда берутся PROJECT_ROOT и app).
        app_icon: Путь к иконке приложения.
        btn_icon: Путь к иконке кнопки закрытия.
        app_name: Название приложения, отображаемое в шапке.
    """

    def __init__(self, app: Optional[Application] = None):
        """Создаёт шапку.
        
        Args:
            app: Экземпляр Application. Если None - упадёт при
                обращении к PROJECT_ROOT (предпологается, что всегда
                передаётся).
        """
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.app = app

        self.app_icon = self.app.PROJECT_ROOT / "icon.ico"
        self.btn_icon = self.app.PROJECT_ROOT / "close.ico"
        self.app_name = "Yellow Wave Music Player (RU)"

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(TRANSPARENT_FRAME)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QHBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)

        pixmap = AppIcon(str(self.app_icon)).icon(64, 64)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(QSize(64, 64))
        self.icon_label.setStyleSheet(TRANSPARENT_LABEL)
        self.frame_layout_2.addWidget(self.icon_label)

        self.name_label = QLabel()
        self.name_label.setText(self.app_name)
        self.name_label.setFixedHeight(40)
        self.name_label.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_2.addWidget(self.name_label)

        self.frame_layout_2.addStretch()

        btn_pixmap = ButtonIcon(str(self.btn_icon)).icon(64, 64)

        self.close_button = QPushButton()
        self.close_button.clicked.connect(QApplication.quit)
        self.close_button.setIcon(btn_pixmap)
        self.close_button.setIconSize(QSize(70, 70))
        self.close_button.setToolTip("Закрыть приложение")
        self.close_button.setStyleSheet(TRANSPARENT_BUTTON)
        self.frame_layout_2.addWidget(self.close_button)
