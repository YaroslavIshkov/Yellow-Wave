from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont


class TransitionButton(QWidget):
    """Кнопки переключения треков (вперёд/назад). Протестировано: 09.07.2026"""
    def __init__(self, font_family: str, main):
        super().__init__()
        self.main = main
        self.icon_font = QFont(font_family, 16)
        self.previous_button = QPushButton()
        self.previous_button.clicked.connect(self.to_previous)
        self.previous_button.setFont(self.icon_font)
        self.previous_button.setText("\uf048")
        self.previous_button.setStyleSheet("""
            QPushButton {
                background: #9B69B5; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF;
            }
        """)
        self.previous_button.setFixedSize(32, 32)

        self.next_button = QPushButton()
        self.next_button.clicked.connect(self.to_next)
        self.next_button.setFont(self.icon_font)
        self.next_button.setText("\uf051")
        self.next_button.setStyleSheet("""
            QPushButton {
                background: #9B69B5; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF;
            }
        """)
        self.next_button.setFixedSize(32, 32)

    def to_previous(self):
        self.main.to_previous()

    def to_next(self):
        self.main.to_next()
