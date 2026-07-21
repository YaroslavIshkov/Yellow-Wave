from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt


class VolumeLabel(QWidget):
    """
        Метка для отображения уровня громкости звука в процентах. 
        Протестировано: 09.07.2026
    """
    def __init__(self, sound=None):
        super().__init__()
        self.sound = sound
        self.percent_lbl = QLabel()
        self.percent_lbl.setText(str(self.sound.last_volume) + " %")
        self.percent_lbl.setAlignment(Qt.AlignCenter)
        self.percent_lbl.setStyleSheet("""
            QLabel {
                background: #D9D9D9; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 15px;
            }
        """)
        self.percent_lbl.setFixedSize(50, 32)
