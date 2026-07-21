import textwrap
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout


class InfoTrackLabel(QWidget):
    def __init__(self):
        super().__init__()

        self.frame_layout = QVBoxLayout()
        self.frame_layout.setContentsMargins(5, 5, 5, 5)

        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background: transparent; 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame.setLayout(self.frame_layout)

        self.title_lbl = QLabel(self)
        self.title_lbl.setText("Название: Неизвестно")
        self.title_lbl.setFixedHeight(40)
        self.title_lbl.setStyleSheet("""
            QLabel {
                background: #E8D0F0; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 7pt; 
                padding-left: 10px;
            }
        """)
        self.frame_layout.addWidget(self.title_lbl)

        self.album_lbl = QLabel(self)
        self.album_lbl.setText("Альбом: Неизвестно")
        self.album_lbl.setFixedHeight(40)
        self.album_lbl.setStyleSheet("""
            QLabel {
                background: #E8D0F0; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 7pt; 
                padding-left: 10px;
            }
        """)
        self.frame_layout.addWidget(self.album_lbl)

        self.artist_lbl = QLabel(self)
        self.artist_lbl.setText("Исполнитель: Неизвестно")
        self.artist_lbl.setFixedHeight(40)
        self.artist_lbl.setStyleSheet("""
            QLabel {
                background: #E8D0F0; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 7pt; 
                padding-left: 10px;
            }
        """)
        self.frame_layout.addWidget(self.artist_lbl)

        self.duration_lbl = QLabel(self)
        self.duration_lbl.setText("Длительность: Неизвестно")
        self.duration_lbl.setFixedHeight(40)
        self.duration_lbl.setStyleSheet("""
            QLabel {
                background: #E8D0F0; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 7pt; 
                padding-left: 10px;
            }
        """)
        self.frame_layout.addWidget(self.duration_lbl)

        self.year_lbl = QLabel(self)
        self.year_lbl.setText("Год: Неизвестно")
        self.year_lbl.setFixedHeight(40)
        self.year_lbl.setStyleSheet("""
            QLabel {
                background: #E8D0F0; 
                border: none; 
                border-radius: 5px; 
                color: #3D3D3D; 
                font-family: SegoeUI; 
                font-size: 7pt; 
                padding-left: 10px;
            }
        """)
        self.frame_layout.addWidget(self.year_lbl)

    def set_track_info(self, track_info: dict):
        if not track_info:
            return
        short_title = textwrap.shorten(
            track_info['title'], 
            width=15, 
            placeholder='...'
        )
        short_album = textwrap.shorten(
            track_info['album'], 
            width=15, 
            placeholder='...'
        )
        short_artist = textwrap.shorten(
            track_info['artist'], 
            width=15, 
            placeholder='...'
        )
        duration = self.format_time(track_info['duration'])
        self.title_lbl.setText(f"Название: {short_title}")
        self.album_lbl.setText(f"Альбом: {short_album}")
        self.artist_lbl.setText(f"Исполнитель: {short_artist}")
        self.duration_lbl.setText(f"Длительность: {duration}")
        self.year_lbl.setText(f"Год: {track_info['year']}")

    def format_time(self, seconds: int) -> str:
        if seconds < 0:
            seconds = 0
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
