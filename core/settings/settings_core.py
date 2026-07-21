import os
import shutil
from pathlib import Path
from core.app.application import Application
from core.messages.message_box import MessageBox
from core.ui.widgets.dialogs.enter_dialog import EnterNameDialog
from core.ui.widgets.dialogs.delete_dialog import DeleteDialog


class SettingsCore:
    def __init__(self, app: Application = None):
        self.app = app
        self.DEVICE_PATH = Path(__file__).parents[3]
    
    def search_music(self):
        data = self.app.json_manager.load_file()
        data["loaded"] = self.app.loaded
        self.app.json_manager.save_file(data)
        self.app.load_dialog()
    
    def add_track_to_sublist(self):
        track_index = self.get_track_index()
        sublist_index = self.get_subgenre_index()
        path_to_track = self.app.frontend.play_menu.sound.tracks[track_index]
        path_to_subgenre = self.app.frontend.sublist_menu.sublists[sublist_index]
        new_path_to_track = path_to_subgenre / path_to_track.name

        data = self.app.json_manager.load_file()
        data["copied"].append(str(new_path_to_track))
        self.app.json_manager.save_file(data)

        shutil.copy(str(path_to_track), str(new_path_to_track))

        msg = f"Добавлено в {path_to_subgenre.name}: {path_to_track.name}"
        message_box = MessageBox(parent=self.app.parent, message=msg)
        message_box.exec_()
    
    def delete_track_from_sublist(self):
        sublist_index = self.get_track_index()
        if not sublist_index:
            msg = "Выберите объект для удаления"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()
            return
        data = self.app.json_manager.load_file()
        path_to_track = data["copied"][sublist_index]
        track_index = data["copied"].index(path_to_track)
        data["copied"].pop(track_index)
        self.app.json_manager.save_file(data)

        os.remove(str(path_to_track))

        msg = f"Удалено: {path_to_track}"
        message_box = MessageBox(parent=self.app.parent, message=msg)
        message_box.exec_()
    
    def get_track_index(self):
        selected_index = self.app.frontend.track_menu.track_list.currentRow()
        if selected_index >= 0:
            return selected_index
    
    def get_subgenre_index(self):
        selected_index = self.app.frontend.sublist_menu.sublists_menu.currentRow()
        if selected_index >= 0:
            return selected_index
    
    def create_dialog(self):
        dialog = EnterNameDialog(
            parent=self.app.parent, 
            ok_func=self.add_subgenre
        )
        dialog.exec_()
    
    def add_subgenre(self, name: str):
        path_to_subgenre = self.app.PATH_TO_SUBGENRES / name
        genre = self.app.frontend.playlist_menu.get_current_text()
        if not path_to_subgenre.exists():
            path_to_subgenre.mkdir(parents=True)
        
        msg = f"Поджанр {name} добавлен в плейлист {genre}!"
        message_box = MessageBox(parent=self.app.parent, message=msg)
        message_box.exec_()

        self.app.frontend.sublist_menu.add_items_to_list(self.app.PATH_TO_SUBGENRES)
    
    def delete_dialog(self):
        subgenre_index = self.get_subgenre_index()
        if not subgenre_index:
            msg = "Выберите объект для удаления"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()
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
        try:
            subgenre_index = self.get_subgenre_index()
            path_to_subgenre = self.app.frontend.sublist_menu.sublists[subgenre_index]

            shutil.rmtree(str(path_to_subgenre))

            genre = self.app.frontend.playlist_menu.get_current_text()
            msg = f"Поджанр {path_to_subgenre.name} удалён из плейлиста {genre}"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()

            self.app.frontend.sublist_menu.add_items_to_list(self.app.PATH_TO_SUBGENRES)
        except PermissionError:
            msg = "Перейдите в другую папку перед удалением!"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()
    
    def delete_track_from_list(self):
        track_index = self.get_track_index()
        if not track_index:
            msg = "Выберите объект для удаления"
            message_box = MessageBox(parent=self.app.parent, message=msg)
            message_box.exec_()
            return
        path_to_track = self.app.frontend.play_menu.sound.tracks[track_index]

        os.remove(str(path_to_track))

        msg = f"{path_to_track.name} удалён из плейлиста {path_to_track.parent}"
        message_box = MessageBox(parent=self.app.parent, message=msg)
        message_box.exec_()

        data = self.app.json_manager.load_file()
        music = Path(data.get("music", ""))
        self.app.frontend.play_menu.sound.load_tracks(music)
