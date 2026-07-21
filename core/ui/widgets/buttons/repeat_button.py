from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont


class RepeatButton(QWidget):
    """Кнопка переключения режима воспроизведения треков. Протестировано: 09.07.2026"""
    def __init__(self, font_family: str, sound=None, menu=None):
        super().__init__()
        self.sound = sound
        self.menu = menu
        self.icon_font = QFont(font_family, 16)
        self.repeat_shuffle_button = QPushButton()
        self.repeat_shuffle_button.clicked.connect(self.set_mode)
        self.repeat_shuffle_button.setFont(self.icon_font)
        self.repeat_shuffle_button.setText("--")
        self.repeat_shuffle_button.setStyleSheet("""
            QPushButton {
                background: #9B69B5; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF;
            }
        """)
        self.repeat_shuffle_button.setFixedSize(32, 32)

    def set_mode(self):
        if self.sound.mode < 3:
            self.sound.mode += 1
        else:
            self.sound.mode = 0
        self.set_button_icon()
        self.set_button_bg()
        self.set_text()

    def set_button_icon(self):
        icons = {
            0: lambda: self.repeat_shuffle_button.setText("--"), 
            1: lambda: self.repeat_shuffle_button.setText("\uf01e"), 
            2: lambda: self.repeat_shuffle_button.setText("\uf01e"), 
            3: lambda: self.repeat_shuffle_button.setText("\uf074")
        }
        icons[self.sound.mode]()

    def set_button_bg(self):
        if self.sound.mode > 0:
            self.repeat_shuffle_button.setStyleSheet("""
                QPushButton {
                    background: #9B69B5; 
                    border: none; 
                    border-radius: 5px; 
                    color: #FFFFFF;
                }
            """)
        else:
            self.repeat_shuffle_button.setStyleSheet("""
                QPushButton {
                    background: #9B69B5; 
                    border: none; 
                    border-radius: 5px; 
                    color: #FFFFFF;
                }
            """)
    
    def set_text(self):
        functions = {
            0: self.standart, 
            1: self.repeat_all, 
            2: self.repeat_one, 
            3: self.shuffle
        }
        functions[self.sound.mode]()
    
    def standart(self):
        self.menu.state_label.set_text("Порядок")

    def repeat_all(self):
        self.menu.state_label.set_text("Повтор")

    def repeat_one(self):
        self.menu.state_label.set_text("Повтор трека")

    def shuffle(self):
        self.menu.state_label.set_text("Перемешать")
