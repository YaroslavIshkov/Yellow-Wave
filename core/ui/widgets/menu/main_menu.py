import pygame
import random
from pathlib import Path
from typing import Union
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, 
    QWidget)
from PyQt5.QtGui import QFontDatabase
from core.ui.widgets.buttons.play_button import PlayButton
from core.ui.widgets.buttons.transition_button import TransitionButton
from core.ui.widgets.buttons.stop_button import StopButton
from core.ui.widgets.buttons.repeat_button import RepeatButton
from core.ui.widgets.labels.state_label import StateLabel
from core.ui.widgets.sliders.volume_slider import VolumeSlider
from core.ui.widgets.labels.volume_label import VolumeLabel
from core.ui.widgets.buttons.mute_button import MuteButton
from core.ui.widgets.sliders.track_slider import TrackSlider
from core.ui.widgets.tracks.track_menu import TrackMenu
from core.app.application import Application

pygame.init()
pygame.mixer.init()


class SoundEngine:
    """Главный класс отвечающий за воспроизведение треков. Протестировано: 09.07.2026"""
    def __init__(self, 
                    slider: TrackSlider = None, 
                    track_menu: TrackMenu = None, 
                    main: Application = None):
        super().__init__()
        self.slider = slider
        self.track_menu = track_menu
        self.main = main
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_music_status)
        self.started = False
        self.paused = False
        self.muted = False
        self.current = 0
        self.mode = 0
        self.tracks = []
        self.shorts = []
        self.volume = 50
        self.last_volume = 50
        self.FORMATS = (".wav", ".mp3", ".ogg", ".flac")
        self.set_volume(self.volume)

    def load_tracks(self, path: Union[Path, str] = None):
        path = Path(path) if isinstance(path, str) else path
        self.tracks = [path for path in path.iterdir() 
            if path and path.name.endswith(self.FORMATS)]
        self.shorts = [path.name for path in self.tracks if path]
        if len(self.tracks) > 0:
            self.main.frontend.cover_label.load_track(self.tracks[self.current])
            self.track_menu.track_list.clear()
            self.track_menu.track_list.addItems(self.shorts)
            self.main.frontend.track_slider.heart_btn.liked()
            self.update_track_info(0)
    
    def update_track_info(self, index: int = 0):
        track = self.tracks[index]
        self.main.frontend.cover_label.load_track(track)
        self.slider.track = track
        self.slider.reset_countdown()
        self.slider.update_duration_sec()
        self.main.frontend.play_menu.play_button.update_icon()
        self.track_menu.track_list.setCurrentRow(index)
        self.track_menu.track_list.setFocus()
        self.main.frontend.track_slider.heart_btn.liked()

    def toggle_play(self):
        if not self.started:
            self.slider.start_countdown()
            self.play_music(self.current)
            self.started = True
            self.timer.start(1000)
        elif self.paused:
            self.unpause_music()
            self.paused = False
        else:
            self.pause_music()
            self.paused = True

    def stop(self):
        self.started = False
        self.paused = False
        self.stop_music()

    def play_music(self, track: int = 0):
        pygame.mixer.music.load(str(self.tracks[track]))
        pygame.mixer.music.play()
        self.slider.reset_start_pos(0)
        self.slider.start_countdown()

    def pause_music(self):
        pygame.mixer.music.pause()
        self.timer.stop()
        self.slider.stop_countdown()

    def unpause_music(self):
        pygame.mixer.music.unpause()
        self.slider.start_countdown()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.timer.stop()
        self.slider.reset_countdown()
        self.slider.reset_start_pos(0)

    def set_volume(self, volume: int):
        if self.started:
            pygame.mixer.music.set_volume(volume / 100)

    def set_position(self, seconds: int):
        if self.started:
            pygame.mixer.music.play(start=float(seconds))
            self.slider.reset_start_pos(seconds)

    def to_previous(self):
        if self.mode != 2:
            if self.current > 0:
                self.current -= 1
            else:
                self.current = len(self.tracks) - 1
        self.update_track_info(self.current)
        self.play_music(self.current)
        self.paused = False
        self.started = True

    def to_next(self):
        if self.mode != 2:
            if self.current < len(self.tracks) - 1:
                self.current += 1
            else:
                self.current = 0
        self.update_track_info(self.current)
        self.play_music(self.current)
        self.paused = False
        self.started = True

    def check_music_status(self):
        if not pygame.mixer.music.get_busy():
            self.on_track_end()
    
    def on_track_end(self):
        if not self.started:
            return
        
        if self.mode == 0:
            if self.current + 1 < len(self.tracks):
                self.current += 1
                self.update_track_info(self.current)
                self.play_music(self.current)
            else:
                self.stop_music()
                self.started = False
                self.main.frontend.play_menu.play_button.update_icon()
            
        elif self.mode == 1:
            self.current = (self.current + 1) % len(self.tracks)
            self.update_track_info(self.current)
            self.play_music(self.current)
        
        elif self.mode == 2:
            self.play_music(self.current)
        
        elif self.mode == 3:
            if self.current + 1 < len(self.tracks):
                self.current = random.randint(0, len(self.tracks) - 1)
            else:
                self.current = 0
            self.update_track_info(self.current)
            self.play_music(self.current)


class MainPlayMenu(QWidget):
    def __init__(self, 
                    slider: TrackSlider = None, 
                    track_menu: TrackMenu = None, 
                    main: Application = None):
        super().__init__()
        self.slider = slider
        self.track_menu = track_menu
        self.main = main
        self.font_path = Path(__file__).parents[4] / "fonts" / "Font Awesome 6 Free-Solid-900.otf"
        self.font_id = QFontDatabase.addApplicationFont(str(self.font_path))
        if self.font_id == -1:
            pass
        else:
            self.font_family = QFontDatabase.applicationFontFamilies(self.font_id)[0]
        self.sound = SoundEngine(self.slider, self.track_menu, self.main)

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet("""
            QFrame {
                background: #FFFFFF; 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QHBoxLayout()
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)
        self.frame.setLayout(self.frame_layout_2)
        self.frame_layout_2.setSpacing(50)

        self.repeat_button = RepeatButton(self.font_family, self.sound, self)
        self.frame_layout_2.addWidget(self.repeat_button.repeat_shuffle_button)

        self.transition = TransitionButton(self.font_family, self)
        self.frame_layout_2.addWidget(self.transition.previous_button)

        self.play_button = PlayButton(self.font_family, self.sound)
        self.frame_layout_2.addWidget(self.play_button.play_button)

        self.frame_layout_2.addWidget(self.transition.next_button)

        self.stop_button = StopButton(self.font_family, self)
        self.frame_layout_2.addWidget(self.stop_button.stop_button)
        self.frame_layout_2.addStretch()

        self.state_label = StateLabel()
        self.frame_layout_2.addWidget(self.state_label.state_label)
        self.repeat_button.standart()

        self.percent_lbl = VolumeLabel(self.sound)
        self.frame_layout_2.addWidget(self.percent_lbl.percent_lbl)

        self.volume_sld = VolumeSlider(self.percent_lbl.percent_lbl, self.sound)
        self.frame_layout_2.addWidget(self.volume_sld.volume_sld)

        self.mute_button = MuteButton(self.font_family, self.sound, self.volume_sld)
        self.frame_layout_2.addWidget(self.mute_button.mute_button)
    
    def stop(self):
        self.sound.stop()
        self.play_button.update_icon()

    def to_previous(self):
        self.sound.to_previous()
        self.play_button.update_icon()

    def to_next(self):
        self.sound.to_next()
        self.play_button.update_icon()
