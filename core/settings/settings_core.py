# SPDX-FileCopyrightText: 2026 YaroslavIshkov
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ядро управления плейлистами и поджанрами.

SettingsCore - центральный класс для операций над плейлистами: 
создание и удаление поджанров, добавление и удаление треков, 
переименовывание файлов, валидация имён. Также содержит логику
работы с Favorites при переименовывании.

Все методы рассчитаны на вызов из UI и самостоятельно показывают
MessageBox с результатом или ошибкой.
"""

import os
import re
import shutil
import pygame
from pathlib import Path
from typing import Optional
from core.app.application import Application
from core.messages.message_box import MessageBox
from core.ui.widgets.dialogs.enter_dialog import EnterNameDialog
from core.ui.widgets.dialogs.delete_dialog import DeleteDialog


class SettingsCore:
    """Ядро управления плейлистами, поджанрами и треками.
    
    Содержит всю логику модификации файловой системы (создание
    папок, копирование, удаление, переименовывание) с проверками
    и обработкой ошибок.
    
    Attributes:
        app: Ссылка на Application.
        INVALID_CHARS: Regex запрещённых символов для имён файлов/папок.
    """

    def __init__(self, app: Optional[Application] = None):
        """Создаёт ядро управления.
        
        Args:
            app: Экземпляр Application (даёт доступ к UI и путям).
        """
        self.app = app
        self.INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1f]'
    
    def is_valid_name(self, name: str) -> bool:
        """Проверяет, допустимо ли имя файла или папки на Windows.
        
        Отклоняет: пустые строки, строки с пробелами по краям, 
        '.', '..', и строки с запрещёнными символами (< > : " / \\ | ? *).
        
        Args:
            name: Проверяемое имя (без расширения).
        
        Returns:
            True, если имя можно использовать.
        """
        if not name or not name.strip():
            return False
        if name.strip() != name:
            return False
        if name in ('.', '..'):
            return False
        if re.search(self.INVALID_CHARS, name):
            return False
        return True
    
    def search_music(self):
        """Открывает диалог повторного сканирования папки Music."""
        self.app.load_dialog()
    
    def add_track_to_sublist(self):
        """Копирует выбранный трек в выбранный поджанр.
        
        Проверяет, что выбраны и трек, и поджанр, что файла с таким
        именем ещё нет. При успехе показывает MessageBox.
        """
        track_index = self.get_track_index()
        sublist_index = self.get_subgenre_index()

        if track_index is None or sublist_index is None:
            MessageBox(parent=self.app.parent, 
                message="Выберите трек и поджанр").exec_()
            return
        
        track = self.app.frontend.play_menu.sound.tracks[track_index]
        sublist = self.app.frontend.sublist_menu.sublists[sublist_index]
        new_path = sublist / track.name

        if new_path.exists():
            MessageBox(parent=self.app.parent, 
                message=f"{track.name} уже есть в {sublist.name}").exec_()
            return
        
        try:
            shutil.copy(str(track), str(new_path))
        except OSError as e:
            MessageBox(parent=self.app.parent, 
                message=f"Не удалось скопировать: {e}").exec_()
            return

        MessageBox(parent=self.app.parent, 
            message=f"Добавлено в {sublist.name}: {track.name}").exec_()
    
    def delete_track_from_sublist(self):
        """Удаляет выбранный трек из текущего поджанра.
        
        Удаляет файл с диска и перезагружает список треков из папки,
        в которой сейчас находится пользователь.
        """
        track_index = self.get_track_index()
        if track_index is None:
            MessageBox(parent=self.app.parent, 
                message="Выберите объект для удаления").exec_()
            return
        
        track = self.app.frontend.play_menu.sound.tracks[track_index]

        try:
            if track.exists():
                os.remove(str(track))
        except OSError as e:
            MessageBox(parent=self.app.parent, 
                message=f"Не удалось удалить: {e}").exec_()
            return

        MessageBox(parent=self.app.parent, 
            message=f"Удалено: {track.name}").exec_()
        
        data = self.app.json_manager.load_file()
        music_path = data.get("music", "")
        if music_path:
            self.app.frontend.play_menu.sound.load_tracks(music_path)
    
    def get_track_index(self) -> Optional[int]:
        """Возвращает индекс выбранного трека в track_menu.
        
        Returns:
            Индекс (int) или None, если ничего не выбрано.
        """
        row = self.app.frontend.track_menu.track_list.currentRow()
        return row if row >= 0 else None
    
    def get_subgenre_index(self) -> Optional[int]:
        """Возвращает индекс выбранного поджанра в sublist_menu.
        
        Returns:
            Индекс (int) или None, если ничего не выбрано.
        """
        row = self.app.frontend.sublist_menu.sublists_menu.currentRow()
        return row if row >= 0 else None
    
    def create_dialog(self):
        """Открывает диалог создания нового поджанра."""
        dialog = EnterNameDialog(
            parent=self.app.parent, 
            ok_func=self.add_subgenre
        )
        dialog.exec_()
    
    def add_subgenre(self, name: str):
        """Создаёт новую папку поджанра внутри текущего плейлиста.
        
        Проверяет валидность имени, наличие плейлиста, отсутствие
        папки с таким именем. После создания обновляет sublist_menu.
        
        Args:
            name: Имя нового поджанра.
        """
        if not self.is_valid_name(name):
            MessageBox(parent=self.app.parent, 
                message='Имя не должно содержать: < > : " / \\ | ? *').exec_()
            return
        
        if not self.app.PATH_TO_SUBGENRES:
            MessageBox(parent=self.app.parent, 
                message="Сначала выберите плейлист").exec_()
            return
        
        path_to_subgenre = self.app.PATH_TO_SUBGENRES / name
        if path_to_subgenre.exists():
            MessageBox(parent=self.app.parent, 
                message=f"Папка {name} уже существует").exec_()
            return
        
        try:
            path_to_subgenre.mkdir(parents=True)
        except OSError as e:
            MessageBox(parent=self.app.parent, 
                message=f"Не удалось создать папку: {e}").exec_()
            return
        
        genre = self.app.frontend.playlist_menu.get_current_text() or "?"
        
        MessageBox(parent=self.app.parent, 
            message=f"Поджанр {name} добавлен в плейлист {genre}!").exec_()

        self.app.frontend.sublist_menu.add_items_to_list(self.app.PATH_TO_SUBGENRES)
    
    def delete_dialog(self):
        """Открывает диалог потверждения удаления поджанра."""
        subgenre_index = self.get_subgenre_index()
        if subgenre_index is None:
            MessageBox(parent=self.app.parent, 
                message="Выберите поджанр для удаления").exec_()
            return
        
        path_to_subgenre = self.app.frontend.sublist_menu.sublists[subgenre_index]
        msg = (
            f"Вы действительно хотите удалить {path_to_subgenre.name} без возможности восстановления?\n\n"
            "Продолжить?"
        )
        dialog = DeleteDialog(
            message=msg, 
            parent=self.app.parent, 
            delete_func=self.delete_subgenre
        )
        dialog.exec_()

    def delete_subgenre(self):
        """Удаляет текущий поджанр рекурсивно.
        
        Если из этого поджанра сейчас играет трек - сначала
        останавливает воспроизведения и сбрасывает UI плеера.
        После удаления обновляет sublist_menu и, при необходимости, 
        перезагружает треки из родительского плейлиста.
        """
        subgenre_index = self.get_subgenre_index()
        if subgenre_index is None:
            return
            
        path_to_subgenre = self.app.frontend.sublist_menu.sublists[subgenre_index]
        deleted_path = str(path_to_subgenre)

        data = self.app.json_manager.load_file()
        current_music = data.get("music", "")
        is_playing_from_here = current_music == deleted_path

        if is_playing_from_here:
            sound = self.app.frontend.play_menu.sound
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass
            sound.reset_ui()
            sound.started = False
            sound.paused = False
            sound.tracks = []
            sound.shorts = []

        try:
            shutil.rmtree(str(path_to_subgenre))
        except OSError as e:
            MessageBox(parent=self.app.parent, 
                message=f"Не удалось удалить: {e}").exec_()
            return

        genre = self.app.frontend.playlist_menu.get_current_text() or "?"
        MessageBox(parent=self.app.parent, 
            message=f"Поджанр {path_to_subgenre.name} удалён из {genre}").exec_()
        
        if is_playing_from_here:
            parent = self.app.PATH_TO_SUBGENRES
            if parent and parent.exists():
                self.app.load_tracks(str(parent))
            else:
                data["music"] = ""
                self.app.json_manager.save_file(data)
                self.app.frontend.track_menu.track_list.clear()
            
        self.app.frontend.sublist_menu.add_items_to_list(
            self.app.PATH_TO_SUBGENRES)
    
    def delete_track_from_list(self):
        """Удаляет выбранный трек из текущего плейлиста.
        
        Если играет именно этот трек - останавливает воспроизведение
        и сбрасывает UI. После удаления перезагружает оставшиеся треки.
        """
        track_index = self.get_track_index()
        if track_index is None:
            MessageBox(parent=self.app.parent, 
                message="Выберите объект для удаления").exec_()
            return

        track = self.app.frontend.play_menu.sound.tracks[track_index]

        sound = self.app.frontend.play_menu.sound
        if sound.started and sound.current == track_index:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass
            sound.reset_ui()

        try:
            if track.exists():
                os.remove(str(track))
        except OSError as e:
            msg = "Не удалось удалить:\n\n"
            msg += f"{e}"
            MessageBox(parent=self.app.parent, 
                message=msg).exec_()
            return

        MessageBox(parent=self.app.parent, 
            message=f"{track.name} удалён").exec_()

        data = self.app.json_manager.load_file()
        music_path = data.get("music", "")
        if music_path and Path(music_path).exists():
            self.app.frontend.play_menu.sound.load_tracks(music_path)
        
        sound.started = False
        sound.paused = False
        self.app.frontend.play_menu.play_button.update_icon()
    
    def rename_track_dialog(self):
        """Открывает диалог переименовывания текущего выбранного трека.
        
        В поле ввода подставляется имя без расширения - так пользователь
        не запутается с форматом файла.
        """
        track_index = self.get_track_index()
        if track_index is None:
            MessageBox(parent=self.app.parent, 
                message="Выберите трек для переименовывания").exec_()
            return
        
        sound = self.app.frontend.play_menu.sound
        if not sound.tracks or track_index >= len(sound.tracks):
            return
        
        current_name = sound.tracks[track_index].name
        stem = Path(current_name).stem

        dialog = EnterNameDialog(
            parent=self.app.parent, 
            ok_func=self.rename_track, 
            initial_text=stem
        )
        dialog.exec_()
    
    def rename_track(self, new_name: str):
        """Переименовывает текущий выбранный трек.
        
        Проверяет валидность имени, отсутствие конфликта, при
        необходимости останавливает воспроизведение. Автоматически
        добавляет исходное расширение, если пользователь его не указал.
        Синхронизирует Favorites и перезагружает список треков.
        
        Args:
            new_name: Новое имя (с расширением или без).
        """
        track_index = self.get_track_index()
        if track_index is None:
            return
        
        sound = self.app.frontend.play_menu.sound
        if not sound.tracks or track_index >= len(sound.tracks):
            return
        
        old_path = sound.tracks[track_index]
        old_name = old_path.name
        old_ext = old_path.suffix

        new_name = new_name.strip()
        if not new_name:
            return
        
        if not Path(new_name).suffix:
            new_name = new_name + old_ext
        
        if new_name == old_name:
            return
        
        stem_only = Path(new_name).stem
        if not self.is_valid_name(stem_only):
            MessageBox(parent=self.app.parent, 
                message='Имя не должно содержать: < > : " / \\ | ? *').exec_()
            return
        
        new_path = old_path.parent / new_name

        if new_path.exists():
            MessageBox(parent=self.app.parent, 
                message=f"Файл с именем {new_name} уже существует").exec_()
            return
        
        was_playing = sound.started and not sound.paused
        was_paused = sound.started and sound.paused
        
        is_playing = sound.started and sound.current == track_index
        if is_playing:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass
            sound.started = False
            sound.paused = False
        
        try:
            old_path.rename(new_path)
        except OSError as e:
            MessageBox(parent=self.app.parent, 
                message=f"Не удалось переименовать: {e}").exec_()
            return
        
        self._update_favorites_after_rename(old_name, new_name)

        self.app.load_tracks(str(old_path.parent))

        if new_name in sound.shorts:
            new_index = sound.shorts.index(new_name)
            sound.current = new_index
            sound.update_track_info(new_index)

            if was_playing:
                sound.play_music(new_index)
                sound.started = True
                sound.paused = False
            elif was_paused:
                sound.started = True
                sound.paused = True
            
            self.app.frontend.play_menu.play_button.update_icon()

        MessageBox(parent=self.app.parent, 
            message=f"Переименовано: {old_name} \u2192 {new_name}").exec_()
    
    def _update_favorites_after_rename(self, old_name: str, new_name: str):
        """Синхронизирует Favorites после переименовывания трека.
        
        Обновляет имя в JSON-списке favorites и переименовывает файл
        в Music/Favorites, если он там есть.
        
        Args:
            old_name: Старое имя файла.
            new_name: Новое имя файла.
        """
        data = self.app.json_manager.load_file()
        favorites = data.get("favorites", [])

        if old_name in favorites:
            idx = favorites.index(old_name)
            favorites[idx] = new_name
            data["favorites"] = favorites
            self.app.json_manager.save_file(data)

            old_fav = self.app.PATH_TO_FAVORITES / old_name
            new_fav = self.app.PATH_TO_FAVORITES / new_name
            if old_fav.exists():
                try:
                    old_fav.rename(new_fav)
                except OSError:
                    pass
