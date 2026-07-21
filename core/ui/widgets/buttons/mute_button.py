from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QFont


class MuteButton(QWidget):
    """Кнопка включения/отключения звука. Протестировано: 09.07.2026"""
    def __init__(self, font: str, sound=None, slider=None):
        super().__init__()
        self.sound = sound
        self.slider = slider
        self.is_enabled = False
        self.icon_font = QFont(font, 16)
        self.mute_button = QPushButton()
        self.mute_button.clicked.connect(self.set_button_state)
        self.mute_button.setFont(self.icon_font)
        self.mute_button.setText("\uf028")
        self.mute_button.setStyleSheet("""
            QPushButton {
                background: #9B69B5; 
                border: none; 
                border-radius: 5px; 
                color: #FFFFFF;
            }
        """)
        self.mute_button.setFixedSize(32, 32)

    def set_button_state(self):
        self.is_enabled = not self.is_enabled
        if self.is_enabled:
            self.mute_button.setText("\uf026")
        else:
            self.mute_button.setText("\uf028")
        self.set_volume_level()

    def set_volume_level(self):
        if self.is_enabled:
            self.sound.muted = True
            self.sound.last_volume = self.sound.volume
            self.sound.volume = 0
        else:
            self.sound.muted = False
            self.sound.volume = self.sound.last_volume
        self.slider.volume_sld.setSliderPosition(self.sound.volume)
        self.sound.set_volume(self.sound.volume)
