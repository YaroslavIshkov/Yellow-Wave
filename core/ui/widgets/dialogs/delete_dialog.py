# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Диалог потверждения удаления.

Универсальный диалог для опасных действий: удаление трека, 
поджанра, плейлиста. Показывает текст с вопросом и две кнопки - 
'Удалить' (вызывает callback) и 'Отмена' (просто закрывает).
"""

from typing import Callable, Optional
from PyQt5.QtWidgets import (QDialog, QFrame, QLabel, QMainWindow, 
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt
from core.ui.style.styles import (DIALOG_FRAME, DIALOG_LABEL, PRIMARY_BUTTON, 
    apply_shadow)


class DeleteDialog(QDialog):
    """Модальный диалог потверждения удаления.
    
    Не выполняет удаление сам - только спрашивает. Реальное действие
    передаётся как callback и вызывается при нажатии 'Удалить'.
    
    Attributes:
        message: Текст с вопросом (например, 'Удалить файл X?').
        delete_func: Callback без аргументов, вызывается при потверждении.
    """

    def __init__(self, 
                    parent: QMainWindow = None, 
                    message: str = "", 
                    delete_func: Optional[Callable[[], None]] = None):
        """Создаёт диалог потверждения.
        
        Args:
            parent: Родительское окно.
            message: Текст вопроса для пользователя.
            delete_func: Функция, которая будет вызвана при нажатии
                'Удалить'. Если None - кнопка ничего не делает
                (но такое использование не предпологается).
        """
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.message = message
        self.delete_func = delete_func

        self.central_layout = QVBoxLayout(self)
        self.central_layout.setContentsMargins(20, 20, 30, 30)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(DIALOG_FRAME)
        apply_shadow(self.frame)
        self.central_layout.addWidget(self.frame)

        self.frame_layout_1 = QVBoxLayout(self.frame)
        self.frame_layout_1.setContentsMargins(10, 10, 10, 10)

        self.message_lbl = QLabel()
        self.message_lbl.setText(self.message)
        self.message_lbl.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_1.addWidget(self.message_lbl)

        self.frame_layout_2 = QHBoxLayout()
        self.frame_layout_2.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_2.setSpacing(10)
        self.frame_layout_2.addStretch()

        self.delete_btn = QPushButton()
        self.delete_btn.clicked.connect(self.close_window)
        self.delete_btn.setText("Удалить")
        self.delete_btn.setFixedSize(80, 40)
        self.delete_btn.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_2.addWidget(self.delete_btn)

        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.accept)
        self.cancel_btn.setText("Отмена")
        self.cancel_btn.setFixedSize(80, 40)
        self.cancel_btn.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_2.addWidget(self.cancel_btn)

        self.frame_layout_1.addLayout(self.frame_layout_2)
    
    def close_window(self):
        """Вызывает delete_func и закрывает диалог с потверждением."""
        if self.delete_func:
            self.delete_func()
        self.accept()
