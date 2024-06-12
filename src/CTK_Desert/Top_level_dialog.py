import customtkinter as ctk
from ctypes import byref, c_int, sizeof, windll
from typing import Callable 
import os, random
from .Theme import *
from .utils import hvr_clr_g

class Dialog(ctk.CTkToplevel):
    def __init__(self, parent):
        backgroundColor = "#000000"
        self.dialog_color = "#8E908F"
        super().__init__(parent, fg_color=backgroundColor)

        self.parent = parent
        self.dialogs = {}
        self.current_dialog = None

        self.title("")
        self.resizable(False, False)
        self.transient(parent)
        self.attributes('-toolwindow', True)
        self.protocol("WM_DELETE_WINDOW", self._hide)
        self.attributes('-alpha', 0.98)
        windll.dwmapi.DwmSetWindowAttribute(windll.user32.GetParent(self.winfo_id()), 35, byref(c_int(hex_to_0x(backgroundColor))), sizeof(c_int))
        self.iconbitmap(os.path.join(os.path.dirname(__file__), "images/empty.ico"))

        GWL_STYLE = -16
        WS_SYSMENU = 0x80000
        
        hwnd = windll.user32.GetParent(self.winfo_id())
        current_style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        new_style = current_style & ~WS_SYSMENU
        windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
        windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x27)  # Update the window to apply the changes
        
        self.withdraw()
        
    def move_me(self, _):
        self.parent.geometry(f'+{self.winfo_x()}+{self.winfo_y()}')

    def new(self, tag: str = None, text: str = "Are you sure?", font: tuple = (FONT_B, 20), button_text: str = "Confirm", button_color: str | tuple = (LIGHT_MODE["accent"], DARK_MODE["accent"]), button_function: Callable = lambda: None):

        frame = ctk.CTkFrame(self, fg_color=self.dialog_color, width = 600, height = 400, corner_radius=15, border_width=2, border_color=button_color)
        #^ Label
        label = ctk.CTkLabel(frame, text=text, font=font, wraplength=0.8*600)
        label.place(relx = 0.1, rely=0.1, relwidth=0.8, relheight=0.64)
        
        #^ Buttons
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cancel_button = ctk.CTkButton(buttons_frame, text="Cancel", command=self._hide, font=font, fg_color=(LIGHT_MODE["primary"], DARK_MODE["primary"]), hover_color=(hvr_clr_g(LIGHT_MODE["primary"], "l"), hvr_clr_g(DARK_MODE["primary"], "d")))
        cancel_button.pack(expand=True, side="left", padx=10)
        Confirm_button = ctk.CTkButton(buttons_frame, text=button_text, command=lambda func = button_function: self._button_function(func), font=font, 
                                       fg_color=button_color, hover_color=(hvr_clr_g(button_color[0], "l", 10), hvr_clr_g(button_color[1], "d", )))
        Confirm_button.pack(expand=True, side="right", padx=10)
        buttons_frame.place(relx = 0.1, rely=0.64, relwidth=0.8, relheight=0.26)

        if tag != None:
            self.dialogs[tag] = frame

    def _button_function(self, func: Callable):
        func()
        self._hide()

    def show(self, dialog):
        self.parent.wm_attributes("-disabled", 1)
        scaleFactor = windll.shcore.GetScaleFactorForDevice(0) / 100
        self.geometry(f"{int(self.parent.winfo_width()/scaleFactor)}x{int(self.parent.winfo_height()/scaleFactor)}+{self.parent.winfo_x()}+{self.parent.winfo_y()}")
        
        self.deiconify()
        self.bind("<Configure>", self.move_me)
        self.current_dialog = dialog
        self.dialogs[dialog].place(relx = 0.5, rely = 0.45, anchor="center")

    def _hide(self):
        self.dialogs[self.current_dialog].place_forget()
        self.update()
        self.unbind("<Configure>")
        self.parent.wm_attributes("-disabled", 0)
        self.withdraw()
        self.current_dialog = None
        
        