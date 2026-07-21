from typing import Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QFrame, QSizePolicy)
from core.app.application import Application
from core.ui.widgets.playlists.playlist_menu import PlayListMenu
from core.ui.widgets.sublists.sublist_menu import SubListMenu
from core.ui.widgets.tracks.track_menu import TrackMenu
from core.ui.widgets.labels.cover_label import CoverLabel
from core.ui.widgets.sliders.track_slider import MusicSlider
from core.ui.widgets.menu.main_menu import MainPlayMenu


class Frontend:
    def __init__(self, 
                    app: Optional[QApplication] = None, 
                    main: Optional[Application] = None, 
                    parent: Optional[QMainWindow] = None):
        self.app = app
        self.main = main
        self.parent = parent
    
    def init_ui(self):
        self.central = QWidget()
        self.central.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1E0A30, stop:0.5 #3D1A5E, stop:1 #121212
                ); 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.parent.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet("""
            QFrame {
                background: transparent; 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.main_layout.addWidget(self.frame)

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(10, 10, 10, 10)
        self.frame.setLayout(self.frame_layout_1)

        self.playlist_menu = PlayListMenu(main=self.main, parent=self.parent, app=self.app)
        self.frame_layout_1.addWidget(self.playlist_menu.frame)

        self.frame_layout_2 = QHBoxLayout()
        self.frame_layout_2.setContentsMargins(0, 5, 0, 0)

        self.sublist_menu = SubListMenu(main=self.main)
        self.frame_layout_2.addWidget(self.sublist_menu.frame)

        self.track_menu = TrackMenu(self.main)
        self.frame_layout_2.addWidget(self.track_menu.frame)

        self.cover_label = CoverLabel()
        self.frame_layout_2.addWidget(self.cover_label.frame)

        self.frame_layout_3 = QVBoxLayout()
        self.frame_layout_3.setContentsMargins(0, 0, 0, 0)

        self.track_slider = MusicSlider(self.main)
        self.frame_layout_3.addWidget(self.track_slider.frame)

        self.frame_layout_4 = QVBoxLayout()
        self.frame_layout_4.setContentsMargins(0, 0, 0, 0)

        self.play_menu = MainPlayMenu(self.track_slider.track_sld, self.track_menu, self.main)
        self.frame_layout_4.addWidget(self.play_menu.frame)

        self.frame_layout_1.addLayout(self.frame_layout_2)
        self.frame_layout_1.addLayout(self.frame_layout_3)
        self.frame_layout_1.addLayout(self.frame_layout_4)
