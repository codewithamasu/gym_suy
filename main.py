from tkinter import PhotoImage
import ttkbootstrap as ttk
from gui.login import Login
from utils.ui import set_app_icon
import os

if __name__ == "__main__":
    app = ttk.Window(themename="cosmo")
    app.title("Gym Management System")
    app.geometry("1000x800")
    set_app_icon(app)

    app.position_center()
    app.resizable(False, False)

    Login(app)
    app.mainloop()
