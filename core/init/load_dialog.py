# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Диалог сканирования папки Music.

Рекурсивно обходит Music, ищет аудиофайлы по расширениям из 
Application.FORMATS и собирает список уникальных папок с треками. 
Результат сохраняется в Application.folders и передаётся в SelectDialog.
"""

import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, QLabel, 
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from core.ui.style.styles import (DIALOG_FRAME, DIALOG_LABEL, PRIMARY_BUTTON, 
    apply_shadow)

if TYPE_CHECKING:
    from core.app.application import Application


class LoadDialog(QDialog):
    """Модальный диалог сканирования пользовательской папки Music.
    
    Обходит папку через os.walk, собирает пути к папкам с аудио, 
    показывает прогресс (текущий файл, счётчики). По завершении 
    пользователь может нажать 'Далее' и перейти к выбору папки.
    
    Attributes:
        app: Ссылка на Application.
        message: Текст-подсказка в шапке диалога.
        cancel: Флаг отмены сканирования 
            (устанавливается кнопкой 'Отмена').
        """
    
    def __init__(self, 
                    app: Optional["Application"] = None, 
                    message: str = "", 
                    parent: Optional[QMainWindow] = None):
        """Создаёт диалог сканирования. 
        
        Args:
            app: Экземпляр Application (даёт доступ к MUSIC_PATH, 
                FORMATS, folders).
            message: Текст-подсказка для пользователя.
            parent: Родительское окно.
        """
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.app = app
        self.message = message
        self.cancel = False

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
        self.message_lbl.setFixedHeight(40)
        self.message_lbl.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_2.addWidget(self.message_lbl)

        self.progress_lbl = QLabel()
        self.progress_lbl.setText("Поиск файлов...")
        self.progress_lbl.setFixedHeight(40)
        self.progress_lbl.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_2.addWidget(self.progress_lbl)

        self.counter_lbl = QLabel()
        self.counter_lbl.setText("Файлов: 0 | Папок: 0")
        self.counter_lbl.setFixedHeight(40)
        self.counter_lbl.setStyleSheet(DIALOG_LABEL)
        self.frame_layout_2.addWidget(self.counter_lbl)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 0, 0, 0)
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
        self.cancel_btn.clicked.connect(self.cancel_window)
        self.cancel_btn.setText("Отмена")
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setFixedSize(80, 40)
        self.cancel_btn.setStyleSheet(PRIMARY_BUTTON)
        self.frame_layout_3.addWidget(self.cancel_btn)
        
        self.frame_layout_2.addLayout(self.frame_layout_3)

        QTimer.singleShot(0, self.search_music)

    def search_music(self):
        """Рекурсивно сканирует MUSIC_PATH и собирает папки с аудио.
        
        Проходит os.walk по MUSIC_PATH, проверяет расширения файлов
        через Application.FORMATS, складывает родительские папки в
        Application.folders. Дубликаты удаляются через set, результат
        сортируется по полному пути.
        
        UI обновляется каждые 10 папок (а не на каждой итерации - 
        иначе сканирование тормозит). Прерывается флагом self.cancel.
        """
        self.progress_lbl.setText("Поиск файлов...")
        QApplication.processEvents()
        self.app.folders.clear()

        files_found = 0
        dirs_scanned = 0

        for dirname, dirs, filenames in os.walk(self.app.MUSIC_PATH):
            dirs_scanned += 1
            for filename in filenames:
                absolute_path = Path(dirname) / filename
                if absolute_path.suffix.lower() in self.app.FORMATS:
                    files_found += 1
                    self.progress_lbl.setText(f"{absolute_path.name}")
                    self.app.folders.append(absolute_path.parent)
            
            if dirs_scanned % 10 == 0:
                self.counter_lbl.setText(
                    f"Файлов: {files_found} | Папок: {dirs_scanned}"
                )
                QApplication.processEvents()
            
            if self.cancel:
                break
        
        self.counter_lbl.setText(f"Файлов: {files_found} | Папок: {dirs_scanned}")

        self.app.folders = sorted(set(self.app.folders), 
            key=lambda p: str(p).lower())
        self.progress_lbl.setText("Сканирование завершено!")
        self.next_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QApplication.processEvents()
    
    def close_window(self):
        """Закрывает диалог и открывает для выбора папки."""
        self.accept()
        self.app.select_dialog()
    
    def cancel_window(self):
        """Отменяет сканирование: ставит флаг и закрывает диалог."""
        self.cancel = True
        self.accept()
