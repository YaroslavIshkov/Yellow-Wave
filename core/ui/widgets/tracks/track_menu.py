from PyQt5.QtWidgets import (QWidget, QListWidget, QFrame, QVBoxLayout, 
    QSizePolicy)
from PyQt5.QtCore import Qt
from core.app.application import Application


class TrackMenu(QWidget):
    """Список треков. Протестировано: 09.07.2026"""
    def __init__(self, main: Application = None):
        super().__init__()
        self.main = main

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet("""
            QFrame {
                background: transparent; 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QVBoxLayout()
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(self.frame_layout_2)

        self.current_track = None
        self.track_list = QListWidget(self)
        self.track_list.doubleClicked.connect(self.on_item_clicked)
        self.track_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.track_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.track_list.setStyleSheet("""
            QListWidget {
                background: #FFFFFF; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 12pt; 
                outline: 0;
            }

            QListWidget::item {
                background: transparent; 
                border-radius: 5px;
            }

            QListWidget::item:hover {
                background: #E8D0F0;
            }

            QListWidget::item:selected {
                background: #D6B4FF; 
                color: #3D3D3D;
            }
        """)
        self.frame_layout_2.addWidget(self.track_list)

    def on_item_clicked(self):
        selected_index = self.track_list.currentRow()
        if selected_index >= 0:
            self.main.frontend.play_menu.sound.current = selected_index
            self.main.frontend.play_menu.sound.update_track_info(selected_index)
            self.main.frontend.play_menu.sound.stop()
            self.main.frontend.play_menu.sound.toggle_play()
            self.main.frontend.play_menu.play_button.update_icon()
    
    def get_current_index(self):
        self.track_list.setFocus()
        selected_index = self.track_list.currentRow()
        if selected_index >= 0:
            return selected_index
