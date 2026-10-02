# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Диалог ввода имени.

Используется для создания плейлистов и пожанров, а также для
переименовывания треков. Поле ввода защищено валидатором от
запрещённых символов Windows. Кнопка 'Далее' активируется только
когда введён непустой текст.
"""

from typing import Callable, Optional
from PyQt5.QtWidgets import (QDialog, QFrame, QLabel, QLineEdit, 
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from core.ui.style.styles import (DIALOG_FRAME, DIALOG_LABEL, PRIMARY_BUTTON, 
    LINE_EDIT, apply_shadow)


class EnterNameDialog(QDialog):
    """Модальный диалог для ввода одного имени.
    
    Показывает поле ввода с валидатором (запрет < > : " / \\ ? *).
    Кнопка 'Далее' активируется только когда есть непустой текст.
    Может использоваться для создания плейлистов, поджанров или
    переименовывания треков (через initial_text с предзаполнением).
    
    Attributes:
        ok_func: Callback, который вызывается с введённым именем.
    """

    def __init__(self, 
                    parent: Optional[QMainWindow] = None, 
                    ok_func: Optional[Callable[[str], None]] = None, 
                    initial_text: str = ""):
        """Создаёт диалог ввода имени.
        
        Args:
            parent: Родительское окно.
            ok_func: Функция, которая будет вызвана с введёной строкой
                при нажатии 'Далее'.
            initial_text: Начальный текст в поле ввода. Полезно при
                переименовывании - показывает текущее имя.
        """
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ok_func = ok_func

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(20, 20, 30, 30)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(DIALOG_FRAME)
        apply_shadow(self.frame)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)

        self.name_lbl = QLabel()
        self.name_lbl.setText("Название:")
        self.name_lbl.setFixedHeight(40)
        self.name_lbl.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_2.addWidget(self.name_lbl)

        rx = QRegExp(r'[^<>:"/\\|?*]+')
        self.enter_name = QLineEdit()
        self.enter_name.textChanged.connect(self.check_characters)
        self.enter_name.setPlaceholderText("Например: Disco")
        self.enter_name.setFixedWidth(350)
        self.enter_name.setStyleSheet(LINE_EDIT)
        self.frame_layout_2.addWidget(self.enter_name)
        self.enter_name.setValidator(QRegExpValidator(rx, self))

        # Предзаполнение: полезно при переименовывании
        if initial_text:
            self.enter_name.setText(initial_text)
            self.enter_name.selectAll()

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_3.setSpacing(10)
        self.frame_layout_3.addStretch()

        self.next_button = QPushButton()
        self.next_button.clicked.connect(self.close_window)
        self.next_button.setText("Далее")
        self.next_button.setEnabled(False)
        self.next_button.setFixedSize(80, 40)
        self.next_button.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_3.addWidget(self.next_button)

        self.cancel_button = QPushButton()
        self.cancel_button.clicked.connect(self.accept)
        self.cancel_button.setText("Отмена")
        self.cancel_button.setFixedSize(80, 40)
        self.cancel_button.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_3.addWidget(self.cancel_button)

        self.frame_layout_2.addLayout(self.frame_layout_3)

    def check_characters(self):
        """Активирует кнопку 'Далее' если поле содержит непустой текст."""
        if hasattr(self, 'next_button'):
            self.next_button.setEnabled(bool(self.enter_name.text().strip()))

    def close_window(self):
        """Передаёт введённое имя в ok_func и закрывает диалог."""
        entered = self.enter_name.text()
        self.ok_func(entered)
        self.accept()
