from tkinter import PhotoImage
import os

_APP_ICON = None  # singleton

def set_app_icon(window):
    global _APP_ICON

    if _APP_ICON is None:
        icon_path = os.path.join("assets", "app-icon.png")
        _APP_ICON = PhotoImage(file=icon_path)

    window.iconphoto(True, _APP_ICON)
