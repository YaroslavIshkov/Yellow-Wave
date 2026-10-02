# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Движок воспроизведения и панель управления плеером.

Содержит два класса:
    SoundEngine - управление pygame.mixer: загрузка, play/pause/stop, 
        seek, громкость, режимы (Порядок/Повтор/Перемешать)
    MainPlayMenu - панель с кнопками и обработка горячих клавиш

Также инициализирует pygame.mixer на уровне модуля (один раз при импорте).
"""

import pygame
import random
import logging
from pathlib import Path
from typing import Any, Optional, Union
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, 
    QWidget, QApplication, QLineEdit)
from PyQt5.QtGui import QFontDatabase
from core.ui.widgets.buttons.play_button import PlayButton
from core.ui.widgets.buttons.transition_button import TransitionButton
from core.ui.widgets.buttons.seek_button import SeekButton
from core.ui.widgets.buttons.stop_button import StopButton
from core.ui.widgets.buttons.repeat_button import RepeatButton
from core.ui.widgets.labels.state_label import StateLabel
from core.ui.widgets.sliders.volume_slider import VolumeSlider
from core.ui.widgets.labels.volume_label import VolumeLabel
from core.ui.widgets.buttons.mute_button import MuteButton
from core.ui.widgets.sliders.track_slider import TrackSlider
from core.ui.widgets.tracks.track_menu import TrackMenu
from core.app.application import Application
from core.ui.style.styles import WHITE_FRAME

log = logging.getLogger("YellowWave")

pygame.init()
pygame.mixer.init()


class SoundEngine:
    """Движок воспроизведения треков через pygame.mixer.
    
    Хранит список треков текущей папки, индекс текущего, режим воспроизведения.
    Управляет play/pause/stop/seek, громкость и mute. Сохраняет состояние (volume, 
    muted, mode) в QSettings.

    Attributes:
        slider: Ссылка на TrackSlider (для синхронизации прогресса).
        track_menu: Ссылка на TrackMenu (для выделения трека в списке).
        app: Ссылка на Application.
        timer: QTimer для резервной проверки статуса воспроизведения.
        MUSIC_END_EVENT: Событие pygame для детекта конца трека.
        started: True, если трек играет прямо сейчас.
        paused: True, если трек на паузе.
        FORMATS: Поддерживаемые расширения аудио.
        tracks: Список Path-объектов валидных аудиофайлов.
        shorts: Список имён файлов (для UI).
        current: Индекс текущего трека в self.tracks.
        volume: Текущая громкость (0-100).
        last_volume: Громкость до включения mute.
        muted: Флаг mute.
        mode: Режим воспроизведения (0-3).
        pending_seek: Отложенная позиция seek (применяется при unpause).
    """

    def __init__(self, 
                    slider: Optional[TrackSlider] = None, 
                    track_menu: Optional[TrackMenu] = None, 
                    app: Optional[Application] = None):
        """Создаёт движок воспроизведения.
        
        Args:
            slider: Виджет TrackSlider для синхронизации прогресса.
            track_menu: Виджет TrackMenu для выделения трека.
            app: Экземпляр Application.
        """
        self.slider = slider
        self.track_menu = track_menu
        self.app = app

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_music_status)

        self.MUSIC_END_EVENT = pygame.USEREVENT + 1

        self.started = False
        self.paused = False
        self.FORMATS = (".wav", ".mp3", ".ogg", ".flac", ".m4a")
        self.tracks = []
        self.shorts = []
        self.current = 0

        s = self.app.settings
        self.volume = int(s.value("volume", 50))
        self.last_volume = int(s.value("last_volume", 50))
        self.muted = s.value("muted", False, type=bool)
        self.mode = int(s.value("mode", 0))
        self.pending_seek = None

        if not 0 <= self.mode <= 3:
            self.mode = 0
        
        self.set_volume(self.volume)

    def load_tracks(self, 
                        path: Union[Path, str] = None, 
                        update_ui: bool = True):
        """Загружает треки из папки и обновляет UI.
        
        Собирает все аудиофайлы в папке, фильтрует битые через _is_valid_audio, 
        сортирует по имени. Обновляет список в UI, загружает первый трек в панель
        обложки и метаданных.

        Args:
            path: Путь к папке с треками (Path или str).
            update_ui: Если True - обновляет UI под первый трек
                (обложка, метаданные, слайдер). Если False - 
                только наполняет список tracks/shorts, не трогая
                играющий трек и UI плеера. Используется при навигации
                по папкам, чтобы не сбрасывать воспроизведение.
        """
        if path is None:
            return
        
        path = Path(path) if isinstance(path, str) else path
        if not path.exists() or not path.is_dir():
            return
        
        candidates = sorted(
            (p for p in path.iterdir() 
            if p.is_file() and p.name.lower().endswith(self.FORMATS)), 
            key=lambda p: p.name.lower(),
        )

        self.tracks = [p for p in candidates if self._is_valid_audio(p)]
        self.shorts = [p.name for p in self.tracks]
        self.current = 0

        if not self.tracks:
            self.track_menu.track_list.clear()
            return
        
        self.track_menu.track_list.clear()
        self.track_menu.track_list.addItems(self.shorts)

        if not update_ui:
            return
        
        self.app.frontend.cover_label.load_track(self.tracks[0])
        self.app.frontend.track_slider.heart_btn.liked()
        self.update_track_info(0)
    
    def _is_valid_audio(self, path: Path) -> bool:
        """Проверяет, что файл реально открывается mutagen как аудио.
        
        Отсеивает переименованные картинки и битые файлы до того, 
        как они попадут в список.

        Args:
            path: Путь к файлу.
        
        Returns:
            True, если mutagen смог прочитать файл и его длительность > 0.
        """
        try:
            import mutagen
            audio = mutagen.File(str(path))
            if audio is None or not getattr(audio, 'info', None):
                return False
            return audio.info.length > 0
        except Exception:
            return False
    
    def reset_ui(self):
        """Полный сброс UI плеера.
        
        Обнуляет состояние и очищает обложку, метаданные, прогресс, 
        иконку кнопки Play. Используется при удалении текущего поджанра или
        плейлиста.
        """
        if self.timer.isActive():
            self.timer.stop()
        
        self.started = False
        self.paused = False
        self.tracks = []
        self.shorts = []
        self.current = 0

        try:
            self.app.frontend.cover_label.clear()
        except Exception:
            pass

        try:
            self.slider.track = None
            self.slider.reset_countdown()
            self.slider.reset_start_pos(0)
        except Exception:
            pass

        try:
            self.app.frontend.play_menu.play_button.update_icon()
        except Exception:
            pass

        try:
            self.app.frontend.track_slider.heart_btn.liked()
        except Exception:
            pass
    
    def update_track_info(self, index: int = 0):
        """Обновляет UI под трек с указанным индексом.
        
        Загружает обложку и метаданные, обновляет позицию слайдера, 
        выделяет трек в списке, ставит фокус, обновляет сердечко.

        Args:
            index: Индекс трека в self.tracks.
        """
        if not self.tracks:
            return
        if not (0 <= index < len(self.tracks)):
            return
        track = self.tracks[index]
        self.app.frontend.cover_label.load_track(track)
        self.slider.track = track
        self.slider.reset_countdown()
        self.slider.update_duration_sec()
        self.app.frontend.play_menu.play_button.update_icon()
        self.track_menu.track_list.setCurrentRow(index)
        self.track_menu.track_list.setFocus()
        self.app.frontend.track_slider.heart_btn.liked()

    def toggle_play(self):
        """Переключает Play/Pause/Stop в зависимости от состояния.
        
        Три состояния:
            - не started -> начать воспроизведение
            - paused -> снять паузу
            - играет -> поставить на паузу
        """
        if not self.tracks:
            return
        
        if not self.started:
            self.slider.start_countdown()
            self.play_music(self.current)
            self.started = True
        elif self.paused:
            self.unpause_music()
            self.paused = False
        else:
            self.pause_music()
            self.paused = True

    def stop(self):
        """Полная остановка: сбрасывает started/paused и вызывает stop_music."""
        self.started = False
        self.paused = False
        self.stop_music()

    def play_music(self, track: int = 0):
        """Загружает и запускает трек по индексу.
        
        При ошибке pygame логирует и сбрасывает started/paused.

        Args:
            track: Индекс трека в self.tracks.
        """
        if not self.tracks:
            return
        if not (0 <= track < len(self.tracks)):
            return
        
        try:
            pygame.mixer.music.load(str(self.tracks[track]))
            pygame.mixer.music.play()
        except pygame.error as e:
            log.error(f"Не удалось воспроизвести {self.tracks[track].name}: {e}")
            self.started = False
            self.paused = False
            return
        
        self.slider.reset_start_pos(0)
        self.slider.start_countdown()

    def pause_music(self):
        """Ставит pygame.mixer на паузу, останавливает timer и слайдер."""
        pygame.mixer.music.pause()
        self.timer.stop()
        self.slider.stop_countdown()

    def unpause_music(self):
        """Снимает паузу.
        
        Если был pending_seek (перемотка на паузе) - применяет его
        через play(start=...), иначе обычный unpause.
        """
        if self.pending_seek is not None:
            try:
                pygame.mixer.music.play(start=float(self.pending_seek))
                self.slider.reset_start_pos(self.pending_seek)
            except pygame.error as e:
                log.error(f"Не удалось перемотать: {e}")
            self.pending_seek = None
        else:
            pygame.mixer.music.unpause()
        self.slider.start_countdown()

    def stop_music(self):
        """Останавливает pygame.mixer, timer и слайдер."""
        try:
            pygame.mixer.music.stop()
            self.timer.stop()
            self.slider.reset_countdown()
            self.slider.reset_start_pos(0)
        except pygame.error as e:
            log.error(f"Не удалось остановить: {e}")

    def set_volume(self, volume: int):
        """Устанавливает громкость и сохраняет в QSettings.
        
        Применяется к микшеру только если трек играет.

        Args:
            volume: Громкость 0-100.
        """
        self.volume = volume
        if self.started:
            pygame.mixer.music.set_volume(volume / 100)
        self.app.settings.setValue("volume", volume)

    def set_position(self, seconds: int):
        """Перематывает трек на указанную позицию.
        
        Если трек на паузе - запоминает pending_seek (применится при unpause).
        Иначе сразу вызывает play(start=seconds).

        Args:
            seconds: Позиция в секундах.
        """
        if not self.tracks:
            return
        
        if self.paused:
            self.pending_seek = seconds
            self.slider.reset_start_pos(seconds)
            return
        
        self.pending_seek = None
        try:
            pygame.mixer.music.play(start=float(seconds))
            self.slider.reset_start_pos(seconds)
        except pygame.error as e:
            log.error(f"Не удалось перемотать: {e}")

    def to_previous(self):
        """Переключает на предыдущий трек и запускает его.
        
        В режиме 'Повтор трека' (mode=2) остаётся на текущем.
        На первом треке - переходит к последнему (зацикливание).
        """
        if not self.tracks:
            return
        
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
        """Переключает на следующий трек и запускает его.
        
        В режиме 'Повтор трека' (mode=2) остаётся на текущем.
        На последнем треке - возвращается к первому.
        """
        if not self.tracks:
            return
        
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
        """Резервная проверка конца трека через get_busy().
        
        Вызывается по timer (сейчас не запускается - основную работу
        делает TrackSlider.update_time). Оставлено на случай сбоя ручного счётчика.
        """
        if not self.tracks or not self.started or self.paused:
            return
        
        if not pygame.mixer.music.get_busy():
            slider = self.slider
            if (slider.duration_sec > 0 and 
                slider.current_sec < slider.duration_sec - 2):
                self.on_track_end()
    
    def on_track_end(self):
        """Обрабатывает окончание трека с учётом режима воспроизведения.
        
        Режимы:
            0 (Порядок) - следующий трек или стоп, если последний
            1 (Повтор) - зацикливает весь плейлист
            2 (Повтор трека) - играет тот же трек заново
            3 (Перемешать) - случайный трек, не тот же самый
        """
        if not self.started:
            return
        if not self.tracks:
            return
        
        if self.mode == 0:
            if self.current + 1 < len(self.tracks):
                self.current += 1
                self.update_track_info(self.current)
                self.play_music(self.current)
            else:
                self.stop_music()
                self.started = False
                self.app.frontend.play_menu.play_button.update_icon()
            
        elif self.mode == 1:
            self.current = (self.current + 1) % len(self.tracks)
            self.update_track_info(self.current)
            self.play_music(self.current)
        
        elif self.mode == 2:
            self.play_music(self.current)
        
        elif self.mode == 3:
            if len(self.tracks) > 1:
                next_idx = self.current
                while next_idx == self.current:
                    next_idx = random.randint(0, len(self.tracks) - 1)
                self.current = next_idx
            else:
                self.current = 0
            self.update_track_info(self.current)
            self.play_music(self.current)


class MainPlayMenu(QWidget):
    """Панель управления воспроизведением.
    
    Собирает в одну горизонтальную строку кнопки:
    repeat, seek back, prev, play/pause, next, seek forward, stop.
    Справа - state_label, проценты громкости, слайдер и кнопка Mute.

    Также устанавливает глобальный eventFilter для горячих клавиш
    (Space, стрелки, M, L, R, S, F2, Ctrl+O).

    Attributes:
        slider: Ссылка на TrackSlider.
        track_menu: Ссылка на TrackMenu.
        app: Ссылка на Application.
        font_family: Семейство шрифта Font Awesome.
        sound: Экземпляр SoundEngine.
        repeat_button: Кнопка режима воспроизведения.
        seek: Кнопки перемотки +-5 секунд.
        transition: Кнопки prev/next трека.
        play_button: Кнопка Play/Pause.
        stop_button: Кнопка Stop.
        state_label: Метка режима.
        percent_lbl: Метка громкости.
        volume_sld: Слайдер громкости.
        mute_button: Кнопка Mute.
    """

    def __init__(self, 
                    slider: Optional[TrackSlider] = None, 
                    track_menu: Optional[TrackMenu] = None, 
                    app: Optional[Application] = None):
        """Создаёт панель управления.
        
        Args:
            slider: Виджет TrackSlider (для перемотки).
            track_menu: Виджет TrackMenu (для синхронизации выделения).
            app: Экземпляр Application.
        """
        super().__init__()
        self.slider = slider
        self.track_menu = track_menu
        self.app = app

        self.fonts = self.app.PROJECT_ROOT / "fonts"
        self.font_path = self.fonts / "Font Awesome 6 Free-Solid-900.otf"
        self.font_id = QFontDatabase.addApplicationFont(str(self.font_path))
        
        if self.font_id == -1:
            log.warning(f"Не удалось загрузить шрифт: {self.font_path}")
            self.font = "Arial"
        else:
            self.font = QFontDatabase.applicationFontFamilies(self.font_id)[0]
        
        self.sound = SoundEngine(
            slider=self.slider, 
            track_menu=self.track_menu, 
            app=self.app
        )

        self.frame_layout_1 = QVBoxLayout(self)
        self.frame_layout_1.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame.setStyleSheet(WHITE_FRAME)
        self.frame_layout_1.addWidget(self.frame)

        self.frame_layout_2 = QHBoxLayout(self.frame)
        self.frame_layout_2.setContentsMargins(10, 10, 10, 10)
        self.frame_layout_2.setSpacing(50)

        self.repeat_button = RepeatButton(
            font=self.font, 
            sound=self.sound, 
            menu=self
        )
        self.frame_layout_2.addWidget(self.repeat_button.repeat_shuffle_button)

        self.seek_buttons = SeekButton(font=self.font, menu=self)
        self.frame_layout_2.addWidget(self.seek_buttons.back_seek_button)

        self.transition_buttons = TransitionButton(font=self.font, menu=self)
        self.frame_layout_2.addWidget(self.transition_buttons.previous_button)

        self.play_button = PlayButton(font=self.font, sound=self.sound)
        self.frame_layout_2.addWidget(self.play_button.play_button)

        self.frame_layout_2.addWidget(self.transition_buttons.next_button)
        self.frame_layout_2.addWidget(self.seek_buttons.next_seek_button)

        self.stop_button = StopButton(font=self.font, menu=self)
        self.frame_layout_2.addWidget(self.stop_button.stop_button)
        self.frame_layout_2.addStretch()

        self.state_label = StateLabel()
        self.frame_layout_2.addWidget(self.state_label.state_label)
        self.repeat_button.set_button_icon()
        self.repeat_button.set_button_bg()
        self.repeat_button.set_text()

        self.percent_lbl = VolumeLabel(sound=self.sound)
        self.frame_layout_2.addWidget(self.percent_lbl.percent_lbl)

        self.volume_sld = VolumeSlider(
            label=self.percent_lbl.percent_lbl, 
            sound=self.sound
        )
        self.frame_layout_2.addWidget(self.volume_sld.volume_sld)

        self.mute_button = MuteButton(
            font=self.font, 
            sound=self.sound, 
            slider=self.volume_sld
        )
        self.frame_layout_2.addWidget(self.mute_button.mute_button)

        self._setup_hotkeys()
    
    def _setup_hotkeys(self):
        """Настраивает глобальные горячие клавиши плеера.
        
        Снимает фокус с кнопок (иначе Space нажмёт кнопку) и устанавливает
        eventFilter на QApplication.
        """
        for btn in (
            self.play_button.play_button, 
            self.stop_button.stop_button, 
            self.transition_buttons.previous_button, 
            self.transition_buttons.next_button, 
            self.repeat_button.repeat_shuffle_button, 
            self.mute_button.mute_button,
        ):
            btn.setFocusPolicy(Qt.NoFocus)
        
        QApplication.instance().installEventFilter(self)
    
    def eventFilter(self, obj: Any, event: Optional[QEvent]) -> bool:
        """Перехватывает горячие клавиши до того, как их получит виджет.
        
        Игнорирует нажатия, когда фокус в QLineEdit (диалоги ввода).
        Обрабатывает: Space, Ctrl+<-/->, <-/->, Up/Down, M, L, R, S, F2, Ctrl+O.

        Args:
            obj: Объект, которому адресовано событие.
            event: Событие Qt.
        
        Returns:
            True, если событие поглощено, иначе - результат super().
        """
        if event.type() != QEvent.KeyPress:
            return super().eventFilter(obj, event)
        
        if isinstance(QApplication.focusWidget(), QLineEdit):
            return super().eventFilter(obj, event)
        
        key = event.key()
        mods = event.modifiers()
        ctrl = bool(mods & Qt.ControlModifier)

        if key == Qt.Key_Space and not mods:
            self._hotkey_play()
            return True
        
        if key == Qt.Key_Left and ctrl:
            self._hotkey_prev()
            return True
        if key == Qt.Key_Right and ctrl:
            self._hotkey_next()
            return True
        
        if key == Qt.Key_Left and not mods:
            self._hotkey_seek(-5)
            return True
        if key == Qt.Key_Right and not mods:
            self._hotkey_seek(+5)
            return True
        
        if key == Qt.Key_Up and not mods:
            self._hotkey_volume(+5)
            return True
        if key == Qt.Key_Down and not mods:
            self._hotkey_volume(-5)
            return True
        
        if key == Qt.Key_M and not mods:
            self._hotkey_mute()
            return True
        if key == Qt.Key_L and not mods:
            self._hotkey_like()
            return True
        if key == Qt.Key_R and not mods:
            self._hotkey_repeat()
            return True
        if key == Qt.Key_S and not mods:
            self._hotkey_stop()
            return True
        
        if key == Qt.Key_O and ctrl:
            self.app.load_dialog()
            return True
        
        if key == Qt.Key_Q and ctrl:
            QApplication.quit()
            return True
        
        if key == Qt.Key_F2 and not mods:
            self.app.settings_core.rename_track_dialog()
            return True
        
        return super().eventFilter(obj, event)
    
    def _hotkey_play(self):
        """Space - Play/Pause."""
        self.sound.toggle_play()
        self.play_button.update_icon()
    
    def _hotkey_prev(self):
        """Ctrl+<- - предыдущий трек."""
        self.sound.to_previous()
        self.play_button.update_icon()
    
    def _hotkey_next(self):
        """Ctrl+-> - следующий трек."""
        self.sound.to_next()
        self.play_button.update_icon()
    
    def _hotkey_seek(self, delta: int):
        """Перемотка на delta секунд (обычно +-5).
        
        Args:
            delta: Смещение в секундах (положительное вперёд).
        """
        self.seek(delta)
    
    def _hotkey_volume(self, delta: int):
        """Изменяет громкость на delta (+-5).
        
        Args:
            delta: Смещение громкости.
        """
        new_vol = self.sound.volume + delta
        new_vol = max(0, min(new_vol, 100))
        self.sound.set_volume(new_vol)
        self.volume_sld.volume_sld.setSliderPosition(new_vol)
        self.percent_lbl.percent_lbl.setText(f"{new_vol} %")
    
    def _hotkey_mute(self):
        """M - переключить mute."""
        self.mute_button.set_button_state()
    
    def _hotkey_like(self):
        """L - добавить/убрать из Favorites."""
        self.app.frontend.track_slider.heart_btn.on_button_clicked()
    
    def _hotkey_repeat(self):
        """R - переключить режим воспроизведения."""
        self.repeat_button.set_mode()
    
    def _hotkey_stop(self):
        """S - полная остановка."""
        self.sound.stop()
        self.play_button.update_icon()
    
    def stop(self):
        """Останавливает воспроизведение (для StopButton)."""
        self.sound.stop()
        self.play_button.update_icon()

    def to_previous(self):
        """Переход к предыдущему треку (для TransitionButton)."""
        self.sound.to_previous()
        self.play_button.update_icon()

    def to_next(self):
        """Переход к следующему треку (для TransitionButton)."""
        self.sound.to_next()
        self.play_button.update_icon()
    
    def seek(self, delta: int):
        """Перемотка на delta секунд (обычно +-5) (для SeekButton).
        
        Args:
            delta: Смещение в секундах (положительное вперёд).
        """
        if not self.sound.started or not self.sound.tracks:
            return
        slider = self.slider
        new_pos = slider.current_sec + delta
        new_pos = max(0, min(new_pos, slider.duration_sec))
        self.sound.set_position(new_pos)
        slider.track_sld.setSliderPosition(new_pos)
        slider.update_display(new_pos)
