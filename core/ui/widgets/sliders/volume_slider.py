from PyQt5.QtWidgets import QWidget, QLabel, QSlider, QSizePolicy
from PyQt5.QtCore import Qt


class VolumeSlider(QWidget):
    """Ползунок для регулировки громкости звука. Протестировано: 09.07.2026"""
    def __init__(self, label: QLabel, sound=None):
        super().__init__()
        self.label = label
        self.sound = sound
        self.volume_sld = QSlider(Qt.Horizontal, self)
        self.volume_sld.setRange(0, 100)
        self.volume_sld.setFocusPolicy(Qt.NoFocus)
        self.volume_sld.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.volume_sld.setSliderPosition(self.sound.last_volume)
        self.volume_sld.setFixedWidth(100)
        self.volume_sld.setStyleSheet("""
            QSlider {
                background: transparent; 
                border: none;
            }

            QSlider::groove:horizontal {
                background: #DCDCDC; 
                height: 6px; 
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #9B69B5; 
                width: 14px; 
                height: 14px; 
                margin: -4px 0; 
                border-radius: 7px;
            }

            QSlider::handle:horizontal:hover {
                background: #7D3C98;
            }

            QSlider::sub-page:horizontal {
                background: #9B69B5; 
                border-radius: 3px;
            }
        """)

        self.volume_sld.valueChanged[int].connect(self.update_level)

    def update_level(self, value: int):
        self.label.setText(str(value) + " %")
        if not self.sound.muted:
            self.sound.set_volume(value)
        else:
            self.sound.last_volume = value
