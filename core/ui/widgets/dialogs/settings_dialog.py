# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Диалог настроек плеера.

Центральное место для операций над плейлистами и поджанрами: 
сканирование устройства, добавление/удаление треков из поджанров, 
создание/удаление поджанров, удаление треков. Каждая строка - 
пара 'метка + кнопка', создаётся через helper _make_row.
"""

from typing import Callable, Optional, Tuple
from PyQt5.QtWidgets import (QDialog, QFrame, QLabel, QMainWindow, 
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt
from core.settings.settings_core import SettingsCore
from core.ui.style.styles import (DIALOG_FRAME, DIALOG_LABEL, PRIMARY_BUTTON, 
    TRANSPARENT_BUTTON, apply_shadow)


class SettingsDialog(QDialog):
    """Модальный диалог настроек и управления плейлистами.
    
    Показывает семь строк с действиями. Все действия делегируются в
    SettingsCore - диалог только собирает UI и связывает кнопки с методами.
    
    Attributes:
        settings: Ссылка на SettingsCore с методами-обработчиками.
    """

    def __init__(self, 
                    settings: Optional[SettingsCore] = None, 
                    parent: Optional[QMainWindow] = None):
        """Создаёт диалог настроек.
        
        Args:
            settings: Экземпляр SettingsCore, чьи методы будут вызываться
                при нажатии кнопок.
            parent: Родительское окно (обычно MainWindow).
        """
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.settings = settings

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(20, 20, 30, 30)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(DIALOG_FRAME)
        apply_shadow(self.frame)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel()
        self.title_label.setText("Настройки:")
        self.title_label.setFixedHeight(40)
        self.title_label.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_3.addWidget(self.title_label)

        self.close_btn = QPushButton()
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setText("Закрыть")
        self.close_btn.setFixedSize(80, 40)
        self.close_btn.setStyleSheet(TRANSPARENT_BUTTON)
        self.frame_layout_3.addWidget(self.close_btn)

        self.frame_layout_4 = QHBoxLayout()
        self.frame_layout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_layout_4.setSpacing(60)
        self.search_label, self.search_btn = self._make_row(
            self.frame_layout_4, 
            "Сканировать устройство", 
            "Поиск", 
            self.settings.search_music,
        )

        self.frame_layout_5 = QHBoxLayout()
        self.frame_layout_5.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_5.setSpacing(60)
        self.label_1, self.button_1 = self._make_row(
            self.frame_layout_5, 
            "Добавить в поджанр", 
            "Добавить", 
            self.settings.add_track_to_sublist,
        )

        self.frame_layout_6 = QHBoxLayout()
        self.frame_layout_6.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_6.setSpacing(60)
        self.label_2, self.button_2 = self._make_row(
            self.frame_layout_6, 
            "Удалить из поджанра", 
            "Удалить", 
            self.settings.delete_track_from_sublist,
        )

        self.frame_layout_7 = QHBoxLayout()
        self.frame_layout_7.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_7.setSpacing(60)
        self.label_3, self.button_3 = self._make_row(
            self.frame_layout_7, 
            "Добавить поджанр", 
            "Добавить", 
            self.settings.create_dialog,
        )

        self.frame_layout_8 = QHBoxLayout()
        self.frame_layout_8.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_8.setSpacing(60)
        self.label_4, self.button_4 = self._make_row(
            self.frame_layout_8, 
            "Удалить поджанр", 
            "Удалить", 
            self.settings.delete_dialog,
        )

        self.frame_layout_9 = QHBoxLayout()
        self.frame_layout_9.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_9.setSpacing(60)
        self.label_5, self.button_5 = self._make_row(
            self.frame_layout_9, 
            "Удалить трек", 
            "Удалить", 
            self.settings.delete_track_from_list,
        )

        self.frame_layout_2.addLayout(self.frame_layout_3)
        self.frame_layout_2.addLayout(self.frame_layout_4)
        self.frame_layout_2.addLayout(self.frame_layout_5)
        self.frame_layout_2.addLayout(self.frame_layout_6)
        self.frame_layout_2.addLayout(self.frame_layout_7)
        self.frame_layout_2.addLayout(self.frame_layout_8)
        self.frame_layout_2.addLayout(self.frame_layout_9)
    
    def _make_row(self, 
                    layout: QHBoxLayout, 
                    label_text: str, 
                    button_text: str, 
                    callback: Callable[[], None]) -> Tuple[QLabel, QPushButton]:
        """Создаёт пару 'метка + кнопка' и добавляет её в layout.
        
        Helper для сокращения дублирования: все семь строк в диалоге
        устроены одинаково - слева метка, справа кнопка, обе прижаты вправо
        за счёт растяжения layout'а.
        
        Args:
            layout: Куда добавить готовую пару.
            label_text: Текст метки (описание действия).
            button_text: Текст кнопки ('Поиск', 'Добавить', 'Удалить').
            callback: Функция без аргументов, вызывается при нажатии.
        
        Returns:
            Кортеж (label, button) - на случай, если понадобится доработать
            элементы после создания.
        """
        label = QLabel()
        label.setText(label_text)
        label.setFixedHeight(40)
        label.setStyleSheet(DIALOG_LABEL)
        layout.addWidget(label)

        btn = QPushButton()
        btn.clicked.connect(callback)
        btn.setText(button_text)
        btn.setFixedSize(80, 40)
        btn.setStyleSheet(PRIMARY_BUTTON)
        layout.addWidget(btn)

        return label, btn
