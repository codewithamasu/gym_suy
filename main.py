from tkinter import PhotoImage
import ttkbootstrap as ttk
from gui.login import Login
import os

if __name__ == "__main__":
    app = ttk.Window(themename="cosmo")
    app.title("Gym Management System")
    app.geometry("1000x600")

    icon_path = os.path.join("assets", "app-icon.png")
    app.iconphoto(True, PhotoImage(file=icon_path))

    app.position_center()
    app.resizable(False, False)

    Login(app)
    app.mainloop()
