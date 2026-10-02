# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Слайдер перемотки трека и связанные виджеты.

Содержит три класса:
    ClickableSlider - QSlider с реакцией на клик по всей полосе
    TrackSlider - логика перемотки (timer, seek, пауза, конец трека)
    MusicSlider - контейнер (слайдер + метка времени + сердечко)

Время считается вручную через QTimer (100 мс за тик), а не через
pygame.mixer.music.get_pos() - последний сбрасывается в 0 после seek
на MP3-файлах. Конец трека определяется по достижении duration_sec.
"""

import mutagen
import logging
from pathlib import Path
from typing import Optional, Union
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import (QSlider, QFrame, QVBoxLayout, 
    QHBoxLayout, QWidget, QSizePolicy, QStyle)
from core.ui.widgets.labels.duration_label import DurationLabel
from core.ui.widgets.buttons.heart_button import HeartButton
from core.app.application import Application
from core.ui.style.styles import SLIDER_TRACK, WHITE_FRAME

log = logging.getLogger("YellowWave")


class ClickableSlider(QSlider):
    """QSlider, реагирующий на клик по всей полосе, а не только по бегунку.
    
    Стандартный QSlider двигает бегунок только при захвате, клик по желобку
    вызывает jump. Здесь поведение другое: клик в любую точку эмулирует
    sliderPressed + sliderReleased - то есть полноценный seek, как при
    перетаскивании.

    Attributes:
        _dragging: Флаг активного перетаскивания (мышь зажата).
    """

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self._dragging = False
    
    def _set_value_from_pos(self, x: int):
        """Вычисляет значение слайдера по координате курсора.
        
        Учитывает ширину бегунка, чтобы центр бегунка оказывался точно
        под курсором.

        Args:
            x: Координата курсора по X относительно виджета.
        """
        handle_w = self.style().pixelMetric(QStyle.PM_SliderLength, None, self)
        span = max(1, self.width() - handle_w)
        x_corrected = x - handle_w // 2
        val = QStyle.sliderValueFromPosition(
            self.minimum(), self.maximum(), 
            x_corrected, span
        )
        self.setValue(val)

    def mousePressEvent(self, event: QMouseEvent):
        """Обрабатывает нажатие: ставит значение + эмитит sliderPressed.
        
        Args:
            event: Событие мыши от Qt.
        """
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._set_value_from_pos(event.x())
            self.sliderPressed.emit()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Обрабатывает движение мыши при зажатой ЛКМ - обновляет значение.
        
        Args:
            event: Событие мыши от Qt.
        """
        if self._dragging:
            self._set_value_from_pos(event.x())
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обрабатывает отпускание: эмитит sliderReleased.
        
        Args:
            event: Событие мыши от Qt.
        """
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self.sliderReleased.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class TrackSlider(QWidget):
    """Логика перемотки трека и отсчёта времени.
    
    Ведёт счётчик времени вручную (self.current_sec + timer), обновляет
    положение слайдера и метку DurationLabel. Определяет конец трека
    и сообщает SoundEngine через on_track_end().

    Attributes:
        app: Ссылка на Application.
        counter: Виджет DurationLabel для отображения времени.
        current_sec: Текущая позиция в секундах (float, для точности).
        start_pos: Позиция, с которой стартовало воспроизведение.
        is_sliding: True, пока пользователь тащит бегунок.
        timer: QTimer для обновления позиции (интервал 100 мс).
    """

    def __init__(self, 
                    counter: Optional[DurationLabel] = None, 
                    app: Optional[Application] = None):
        """Создаёт слайдер перемотки.
        
        Args:
            app: Ссылка на Application.
            counter: Метка DurationLabel для отображения времени.
        """
        super().__init__()
        self.counter = counter
        self.app = app

        self.track = None
        self.current_sec = 0
        self.duration_sec = 0
        self.start_pos = 0
        self.is_sliding = False

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_time)

        self.track_sld = ClickableSlider(Qt.Horizontal)
        self.track_sld.setRange(0, self.duration_sec)
        self.track_sld.setFocusPolicy(Qt.NoFocus)
        self.track_sld.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.track_sld.setStyleSheet(SLIDER_TRACK)
        self.track_sld.setToolTip("Перемотка (\u2190 / \u2192)")

        self.track_sld.sliderPressed.connect(self.slider_pressed)
        self.track_sld.sliderReleased.connect(self.slider_released)
        self.track_sld.valueChanged[int].connect(self.update_label)
    
    def update_duration_sec(self):
        """Читает длительность трека через mutagen и ставит диапазон слайдера."""
        self.duration_sec = self.get_track_duration(self.track)
        self.track_sld.setRange(0, self.duration_sec)
    
    def reset_start_pos(self, pos: int = 0):
        """Сбрасывает позицию слайдера и стартовую точку отсчёта.
        
        Args:
            pos: Позиция в секундах.
        """
        self.start_pos = pos
        self.current_sec = pos
    
    def start_countdown(self):
        """Запускает timer, если он ещё не активен."""
        if not self.timer.isActive():
            self.timer.start()
            self.update_time()
    
    def stop_countdown(self):
        """Останавливает timer, если он активен."""
        if self.timer.isActive():
            self.timer.stop()
    
    def reset_countdown(self):
        """Сбрасывает позицию, время и метку в начальное состояние."""
        self.timer.stop()
        self.current_sec = 0
        self.start_pos = 0
        reset_duration = self.format_time(0)
        track_duration = self.get_track_duration(self.track)
        formatted = self.format_time(track_duration)
        self.counter.duration_lbl.setText(f"{reset_duration}/{formatted}")
        self.track_sld.setSliderPosition(0)

    def slider_pressed(self):
        """Обработчик захвата бегунка - останавливает timer и ставит флаг."""
        self.is_sliding = True
        self.stop_countdown()

    def slider_released(self):
        """Обработчик отпускания бегунка - применяет seek.
        
        Читает новую позицию, обновляет UI. Если трек не на паузе - 
        возобновляет отсчёт.
        """
        new_pos = self.track_sld.value()
        self.is_sliding = False
        self.current_sec = float(new_pos)

        sound = self.app.frontend.play_menu.sound
        sound.set_position(new_pos)
        self.update_display(new_pos)
        self.track_sld.setSliderPosition(new_pos)

        if not sound.paused:
            self.start_countdown()
    
    def update_time(self):
        """Тик timer: увеличивает позицию, обновляет UI, ловит конец трека.
        
        Вручную считает время (timer.interval / 1000) вместо get_pos() - 
        pygame сбрасывает счётчик после seek. При достижении duration_sec
        вызывает SoundEngine.on_track_end().
        """
        if not self.is_sliding:
            self.current_sec += self.timer.interval() / 1000.0
            if self.current_sec > self.duration_sec:
                self.current_sec = self.duration_sec
            self.track_sld.setSliderPosition(int(self.current_sec))
        
        self.update_display(int(self.current_sec))

        if self.duration_sec > 0 and self.current_sec >= self.duration_sec:
            self.timer.stop()
            self.app.frontend.play_menu.sound.on_track_end()

    def update_display(self, current_sec: Union[int, float]):
        """Обновляет текст DurationLabel: текущее время / общее.
        
        Args:
            current_sec: Текущая позиция в секундах.
        """
        formatted_current = self.format_time(current_sec)
        formatted_total = self.format_time(self.duration_sec)
        self.counter.duration_lbl.setText(f"{formatted_current}/{formatted_total}")
    
    def update_label(self, value: Union[int, float]):
        """Обновляет метку во время перетаскивания бегунка.
        
        Вызывается только когда is_sliding=True - иначе метку перезапишет
        update_display на следующем тике.

        Args:
            value: Новая позиция слайдера (в секундах).
        """
        if self.is_sliding:
            current = self.format_time(value)
            total = self.format_time(self.duration_sec)
            self.counter.duration_lbl.setText(f"{current}/{total}")

    def format_time(self, seconds: Union[int, float]) -> str:
        """Форматирует секунды в MM:SS.
        
        Args:
            seconds: Количество секунд (может быть float - округляется).

        Returns:
            Строка вида '03:22'.
        """
        if seconds < 0:
            seconds = 0
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def get_track_duration(self, file_path: Union[Path, str]) -> int:
        """Читает длительность трека через mutagen.
        
        Работает с любыми форматами, которые понимает mutagen (MP3, 
        FLAC, OGG, WAV, M4A). При ошибке логирует и возвращает 0.

        Args:
            file_path: Путь к треку (Path или str).
        
        Returns:
            Длительность в секундах (int) или 0 при ошибке.
        """
        if not file_path:
            return 0
        file_path = (str(file_path) 
            if isinstance(file_path, Path) else file_path)
        try:
            audio = mutagen.File(file_path)
            if audio is not None and getattr(audio, 'info', None) is not None:
                return int(audio.info.length)
        except Exception as e:
            log.error(f"Не удалось прочитать длительность {file_path}: {e}")
        return 0


class MusicSlider(QWidget):
    """Контейнер: слайдер перемотки + метка времени + кнопка 'Избранное'.
    
    Собирает всё, что связанно с управлением текущим треком: время, 
    полоса перемотки, сердечко для добавления в Favorites.

    Attributes:
        app: Ссылка на Application.
        duration_lbl: Метка '00:00/00:00'.
        track_sld: Слайдер перемотки TrackSlider.
        heart_btn: Кнопка-сердечко HeartButton.
    """

    def __init__(self, app: Optional[Application] = None):
        """Создаёт контейнер.
        
        Args:
            app: Ссылка на Application.
        """
        super().__init__()
        self.app = app

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.frame.setFixedHeight(60)
        self.frame.setStyleSheet(WHITE_FRAME)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QHBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(0, 0, 0, 0)

        self.duration_lbl = DurationLabel()
        self.frame_layout_2.addWidget(self.duration_lbl.duration_lbl)

        self.track_sld = TrackSlider(counter=self.duration_lbl, app=self.app)
        self.frame_layout_2.addWidget(self.track_sld.track_sld)

        self.heart_btn = HeartButton(app=self.app)
        self.frame_layout_2.addWidget(self.heart_btn.heart_btn)
