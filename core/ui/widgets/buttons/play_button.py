from typing import Optional
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont
#from sound_test import SoundEngine


class PlayButton(QWidget):
    """
        Класс реализующий кнопку воспроизведения и приостановки треков.
        Протестировано: 09.07.2026
    """
    def __init__(self, font_family: str, sound = None):
        super().__init__()
        self.sound = sound
        self.icon_font = QFont(font_family, 32)
        self.play_button = QPushButton()
        self.play_button.clicked.connect(self.set_button_state)
        self.play_button.setFont(self.icon_font)
        self.play_button.setText("\uf04b")
        self.play_button.setFixedSize(64, 64)
        self.play_button.setStyleSheet("""
            QPushButton {
                background: #9B69B5; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF;
            }
        """)

    def set_button_state(self):
        self.sound.toggle_play()
        self.update_icon()

    def update_icon(self):
        if self.sound.started and not self.sound.paused:
            self.play_button.setText("\uf04c")
        else:
            self.play_button.setText("\uf04b")
