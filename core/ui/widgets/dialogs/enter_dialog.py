from PyQt5.QtWidgets import (QDialog, QFrame, QLabel, QLineEdit, 
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt


class EnterNameDialog(QDialog):
    def __init__(self, parent: QMainWindow = None, ok_func=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ok_func = ok_func

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame()
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

        self.name_lbl = QLabel()
        self.name_lbl.setText("Название:")
        self.name_lbl.setFixedHeight(40)
        self.name_lbl.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }
        """)
        self.frame_layout_2.addWidget(self.name_lbl)

        self.enter_name = QLineEdit()
        self.enter_name.textChanged.connect(self.check_characters)
        self.enter_name.setPlaceholderText("Например: Disco")
        self.enter_name.setFixedWidth(350)
        self.enter_name.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF; 
                border: 3px solid; 
                border-radius: 5px; 
                border-color: #D6B4FF; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt;
            }

            QLineEdit::hover {
                border-color: #E8D0F0;
            }
        """)
        self.frame_layout_2.addWidget(self.enter_name)

        self.frame_layout_3 = QHBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 5, 0, 0)
        self.frame_layout_3.setSpacing(10)
        self.frame_layout_3.addStretch()

        self.next_button = QPushButton()
        self.next_button.clicked.connect(self.close_window)
        self.next_button.setText("Далее")
        self.next_button.setEnabled(False)
        self.next_button.setFixedSize(80, 40)
        self.next_button.setStyleSheet("""
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
        self.frame_layout_3.addWidget(self.next_button)

        self.cancel_button = QPushButton()
        self.cancel_button.clicked.connect(self.accept)
        self.cancel_button.setText("Отмена")
        self.cancel_button.setFixedSize(80, 40)
        self.cancel_button.setStyleSheet("""
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
        self.frame_layout_3.addWidget(self.cancel_button)

        self.frame_layout_2.addLayout(self.frame_layout_3)

    def check_characters(self):
        enabled = True if len(self.enter_name.text()) > 0 else False
        self.next_button.setEnabled(enabled)

    def close_window(self):
        entered = self.enter_name.text()
        self.ok_func(entered)
        self.accept()
