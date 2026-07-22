# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pygame
import mutagen
from pathlib import Path
from typing import Union
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QSlider, QFrame, QVBoxLayout, 
    QHBoxLayout, QWidget, QSizePolicy)
from core.ui.widgets.labels.duration_label import DurationLabel
from core.ui.widgets.buttons.heart_button import HeartButton
from core.app.application import Application

class TrackSlider(QWidget):
    """Ползунок для прокрутки треков. Протестировано: 09.07.2026"""
    def __init__(self, 
                    parent=None, 
                    counter: DurationLabel = None, 
                    main: Application = None):
        super().__init__(parent)
        self.counter = counter
        self.main = main
        self.track = None
        self.current_sec = 0
        self.duration_sec = 0
        self.start_pos = 0
        self.is_sliding = False
        self.is_seeking = False

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_time)

        self.track_sld = QSlider(Qt.Horizontal, self)
        self.track_sld.setRange(0, self.duration_sec)
        self.track_sld.setFocusPolicy(Qt.NoFocus)
        self.track_sld.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.track_sld.setMinimumWidth(1115)
        self.track_sld.setStyleSheet("""
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
                background: #9B59B6; 
                width: 14px; 
                height: 14px; 
                margin: -4px 0; 
                border-radius: 7px;
            }

            QSlider::handle:horizontal:hover {
                background: #7D3C98;
            }

            QSlider::sub-page:horizontal {
                background: #9B59B6; 
                border-radius: 3px;
            }
        """)

        self.track_sld.sliderPressed.connect(self.slider_pressed)
        self.track_sld.sliderReleased.connect(self.slider_released)
        self.track_sld.valueChanged[int].connect(self.update_label)
    
    def update_duration_sec(self):
        self.duration_sec = self.get_track_duration(self.track)
        self.track_sld.setRange(0, self.duration_sec)
    
    def reset_start_pos(self, pos: int = 0):
        self.start_pos = pos
    
    def start_countdown(self):
        if not self.timer.isActive():
            self.timer.start()
            self.update_time()
    
    def stop_countdown(self):
        if self.timer.isActive():
            self.timer.stop()
            self.update_time()
    
    def reset_countdown(self):
        self.timer.stop()
        self.start_pos = 0
        self.current_sec = 0
        reset_duration = self.format_time(self.current_sec)
        track_duration = self.get_track_duration(self.track)
        formatted = self.format_time(track_duration)
        self.counter.duration_lbl.setText(f"{reset_duration}/{formatted}")
        self.track_sld.setSliderPosition(self.current_sec)

    def slider_pressed(self):
        self.stop_countdown()
        self.is_sliding = True
        self.is_seeking = True

    def slider_released(self):
        self.start_countdown()
        self.is_sliding = False
        new_pos = self.track_sld.value()
        self.main.frontend.play_menu.sound.set_position(new_pos)
        self.update_display(new_pos)
        self.track_sld.setSliderPosition(new_pos)
        if not self.timer.isActive():
            self.timer.start()
            self.update_time()
    
    def update_time(self):
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms == -1:
            return
        current_sec = self.start_pos + pos_ms // 1000
        if current_sec >= self.duration_sec:
            self.timer.stop()
            self.update_display(current_sec)
            self.track_sld.setSliderPosition(current_sec)
            return

        self.current_sec = current_sec
        if not self.is_sliding:
            self.track_sld.setSliderPosition(current_sec)
        self.update_display(current_sec)

    def update_display(self, current_sec):
        formatted_current = self.format_time(current_sec)
        formatted_total = self.format_time(self.duration_sec)
        self.counter.duration_lbl.setText(f"{formatted_current}/{formatted_total}")
    
    def update_label(self, value):
        if self.is_sliding:
            current = self.format_time(value)
            total = self.format_time(self.duration_sec)
            self.counter.duration_lbl.setText(f"{current}/{total}")

    def format_time(self, seconds: int) -> str:
        if seconds < 0:
            seconds = 0
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def get_track_duration(self, file_path: Union[Path, str]):
        if not file_path:
            return 0
        file_path = (str(file_path) 
            if isinstance(file_path, Path) else file_path)
        audio = mutagen.File(file_path)
        if audio is not None and audio.info is not None:
            return int(audio.info.length)
        return 0


class MusicSlider(QWidget):
    def __init__(self, main: Application = None):
        super().__init__()
        self.main = main

        self.frame_layout_1 = QVBoxLayout()
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.frame_layout_1)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.frame.setFixedHeight(60)
        self.frame.setStyleSheet("""
            QFrame {
                background: #FFFFFF; 
                border: none; 
                border-radius: 5px;
            }
        """)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QHBoxLayout()
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(self.frame_layout_2)

        self.duration_lbl = DurationLabel()
        self.frame_layout_2.addWidget(self.duration_lbl.duration_lbl)

        self.track_sld = TrackSlider(None, self.duration_lbl, self.main)
        self.frame_layout_2.addWidget(self.track_sld.track_sld)

        self.heart_btn = HeartButton(parent=None, app=self.main)
        self.frame_layout_2.addWidget(self.heart_btn.heart_btn)
