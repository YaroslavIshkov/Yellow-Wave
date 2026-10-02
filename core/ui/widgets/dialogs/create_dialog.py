# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Диалог создания нового плейлиста.

Запрашивает имя плейлиста и путь к иконке. Имя валидируется через
QRegExp (запрет < > : " / \\ | ? *), оба поля показательны. По нажатию
'Далее' вызывает переданный callback с двумя аргументами.
"""

from typing import Callable, Optional
from PyQt5.QtWidgets import (QMainWindow, QDialog, QFrame, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QLabel, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from core.ui.style.styles import (DIALOG_FRAME, DIALOG_LABEL, PRIMARY_BUTTON, 
    LINE_EDIT, apply_shadow)


class CreateDialog(QDialog):
    """Модальный диалог создания плейлиста.
    
    Два поля: имя плейлиста и путь к PNG-иконке.
    Кнопка 'Далее' активируется только когда оба поля заполнены.
    Реальное создание плейлиста выполняет callback, переданный в
    create_func.
    
    Attribites:
        create_func: Callback(name, icon_path), вызывается при
            потверждении. Создаёт папку плейлиста и копирует иконку.
    """

    def __init__(self, 
                    parent: Optional[QMainWindow] = None, 
                    create_func: Optional[Callable[[str, str], None]] = None):
        """Создаёт диалог.
        
        Args:
            parent: Родительское окно.
            create_func: Функция-обработчик (name, path), которая
                вызывается при нажатии 'Далее'.
        """
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.create_func = create_func

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(20, 20, 30, 30)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(DIALOG_FRAME)
        apply_shadow(self.frame)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)

        self.title_1 = QLabel()
        self.title_1.setText("Название:")
        self.title_1.setFixedHeight(40)
        self.title_1.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_2.addWidget(self.title_1)

        rx = QRegExp(r'[^<>:"/\\|?*]+')
        self.entry_1 = QLineEdit()
        self.entry_1.textChanged.connect(self.check_characters)
        self.entry_1.setValidator(QRegExpValidator(rx, self))
        self.entry_1.setPlaceholderText("Например: Pop")
        self.entry_1.setFixedWidth(350)
        self.entry_1.setStyleSheet(LINE_EDIT)
        self.frame_layout_2.addWidget(self.entry_1)

        self.title_2 = QLabel()
        self.title_2.setText("Путь к файлу:")
        self.title_2.setFixedHeight(40)
        self.title_2.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_2.addWidget(self.title_2)

        self.entry_2 = QLineEdit()
        self.entry_2.textChanged.connect(self.check_characters)
        self.entry_2.setPlaceholderText("Например: pop-icon.png")
        self.entry_2.setFixedWidth(350)
        self.entry_2.setStyleSheet(LINE_EDIT)
        self.frame_layout_2.addWidget(self.entry_2)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_3.setSpacing(10)
        self.frame_layout_3.addStretch()

        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(self.close_window)
        self.next_btn.setText("Далее")
        self.next_btn.setEnabled(False)
        self.next_btn.setFixedSize(80, 40)
        self.next_btn.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_3.addWidget(self.next_btn)

        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.accept)
        self.cancel_btn.setText("Отмена")
        self.cancel_btn.setFixedSize(80, 40)
        self.cancel_btn.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_3.addWidget(self.cancel_btn)

        self.frame_layout_2.addLayout(self.frame_layout_3)
    
    def close_window(self):
        """Передаёт введённые данные в create_func и закрывает диалог.
        
        Текст из полей предварительно обрезается через .strip() - 
        чтобы случайные пробелы по краям не попали в имя плейлиста.
        """
        if self.create_func:
            name = self.entry_1.text().strip()
            path = self.entry_2.text().strip()
            self.create_func(name, path)
        self.accept()

    def check_characters(self):
        """Активирует кнопку 'Далее', если оба поля непустые.
        
        .strip() нужен, чтобы одни пробелы не считались за ввод.
        """
        name_ok = bool(self.entry_1.text().strip())
        path_ok = bool(self.entry_2.text().strip())
        self.next_btn.setEnabled(name_ok and path_ok)
