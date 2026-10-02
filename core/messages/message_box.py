# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Универсальный диалог-сообщение.

Используется для уведомлений пользователя: 'Добавлено в избранное', 
'Ошибка операции', 'Файл не найден' и т.п. Frameless-окно с
градиентным фоном, тенью и одной кнопкой 'ОК'.
"""

from typing import Optional
from PyQt5.QtWidgets import (QDialog, QFrame, QLabel, QMainWindow, 
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt
from core.ui.style.styles import (DIALOG_FRAME, DIALOG_LABEL, PRIMARY_BUTTON, 
    apply_shadow)


class MessageBox(QDialog):
    """Модальный диалог с сообщением и единственной кнопкой ОК.
    
    Открывается через .exec_() - блокирует родительское окно, пока
    пользователь не закроет. Используется для кратких уведомлений
    без выбора действия.
    
    Attributes:
        message: Текст сообщения, отображаемый в диалоге.
    """

    def __init__(self, 
                    parent: Optional[QMainWindow] = None, 
                    message: str = ""):
        """Создаёт диалог с указанным сообщением.
        
        Args:
            parent: Родительское окно (обычно MainWindow).
            message: Текст, который увидит пользователь.
        """
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.message = message

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(20, 20, 30, 30)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(DIALOG_FRAME)
        apply_shadow(self.frame)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)

        self.message_lbl = QLabel()
        self.message_lbl.setText(self.message)
        self.message_lbl.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_2.addWidget(self.message_lbl)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_3.addStretch()

        self.ok_btn = QPushButton()
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setText("OK")
        self.ok_btn.setFixedSize(80, 40)
        self.ok_btn.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_3.addWidget(self.ok_btn)

        self.frame_layout_2.addLayout(self.frame_layout_3)
