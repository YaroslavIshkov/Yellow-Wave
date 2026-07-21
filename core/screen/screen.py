from typing import Optional
from PyQt5.QtWidgets import QApplication, QMainWindow


class Screen:
    def __init__(self, app: Optional[QApplication] = None):
        self.app = app
    
    def center_window(self, 
                        window: Optional[QMainWindow] = None, 
                        width: int = 1200, 
                        height: int = 600, 
                        padx: int = 0, 
                        pady: int = 20):
        screen_num = QApplication.desktop().screenNumber(window)
        screen_rect = QApplication.desktop().availableGeometry(screen_num)
        monitor_width = screen_rect.width()
        monitor_height = screen_rect.height()
        win_x = screen_rect.x() + (monitor_width // 2 - width) - padx
        win_y = screen_rect.y() + (monitor_height // 2 - height) - pady
        window.setGeometry(win_x, win_y, width, height)
