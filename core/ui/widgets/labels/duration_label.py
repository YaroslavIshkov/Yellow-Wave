from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt

class DurationLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.duration_lbl = QLabel("00:00/00:00", self)
        self.duration_lbl.setStyleSheet("""
            QLabel {
                background: transparent; 
                border: none; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 15pt;
            }
        """)
        self.duration_lbl.setFixedWidth(130)
        self.duration_lbl.setFixedHeight(50)
        self.duration_lbl.setAlignment(Qt.AlignCenter)