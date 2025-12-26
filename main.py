import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from gui.login import Login

if __name__ == "__main__":
    app = ttk.Window(themename="flatly")
    app.title("Gym Management System")
    app.geometry("1000x600")
    app.position_center()
    app.resizable(False, False)

    Login(app)

    app.mainloop()
