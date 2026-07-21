import os
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, QLabel, 
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer


class LoadDialog(QDialog):
    def __init__(self, 
                    app=None, 
                    message: str = "", 
                    parent: QMainWindow = None):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.app = app
        self.message = message
        self.cancel = False

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame(self)
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1E0A30, stop:0.5 #3D1A5E, stop:1 #121212
                ); 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout()
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)
        self.frame.setLayout(self.frame_layout_2)

        self.message_lbl = QLabel()
        self.message_lbl.setText(self.message)
        self.message_lbl.setFixedHeight(40)
        self.message_lbl.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_2.addWidget(self.message_lbl)

        self.progress_lbl = QLabel()
        self.progress_lbl.setText("Поиск файлов...")
        self.progress_lbl.setFixedHeight(40)
        self.progress_lbl.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_2.addWidget(self.progress_lbl)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_layout_3.setSpacing(10)
        self.frame_layout_3.addStretch()
        
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(self.close_window)
        self.next_btn.setText("Далее")
        self.next_btn.setEnabled(False)
        self.next_btn.setFixedSize(80, 40)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: #D6B4FF; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QPushButton::hover {
                background: #E8D0F0;
            }
        """)
        self.frame_layout_3.addWidget(self.next_btn)
        
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.cancel_window)
        self.cancel_btn.setText("Отмена")
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setFixedSize(80, 40)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #D6B4FF; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QPushButton::hover {
                background: #E8D0F0;
            }
        """)
        self.frame_layout_3.addWidget(self.cancel_btn)
        
        self.frame_layout_2.addLayout(self.frame_layout_3)

        QTimer.singleShot(0, self.search_music)

    def search_music(self):
        self.progress_lbl.setText("Поиск файлов...")
        QApplication.processEvents()
        self.app.absolute.clear()
        self.app.relative.clear()

        for dirname, _, filenames in os.walk(self.app.ROOT_PATH):
            for filename in filenames:
                absolute_path = Path(dirname) / filename
                if absolute_path.name.endswith(self.app.FORMATS):
                    self.progress_lbl.setText(f"{absolute_path.name}")
                    parent_path = Path(absolute_path.parent.name)
                    self.app.absolute.append(absolute_path.parent)
                    self.app.relative.append(parent_path)
                    QApplication.processEvents()
            if self.cancel:
                break

        self.app.absolute = sorted(set(self.app.absolute), key=lambda p: p.name)
        self.app.relative = sorted(set(self.app.relative), key=lambda p: p.name)
        self.progress_lbl.setText("Сканирование завершено!")
        self.next_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QApplication.processEvents()
    
    def close_window(self):
        self.accept()
        self.app.select_dialog()
    
    def cancel_window(self):
        self.cancel = True
        self.accept()
