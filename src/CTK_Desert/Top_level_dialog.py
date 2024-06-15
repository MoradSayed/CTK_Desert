import customtkinter as ctk
from ctypes import byref, c_int, sizeof, windll
from typing import Callable 
import os, random
from PIL import Image, ImageTk
from .Theme import *
from .utils import hvr_clr_g

class Dialog(ctk.CTkToplevel):
    def __init__(self, parent):
        backgroundColor = "#000000"
        self.dialog_color = "#8E908F"
        self.ugliest_color = "#4A412A"
        super().__init__(parent, fg_color=backgroundColor)

        self.scaleFactor = windll.shcore.GetScaleFactorForDevice(0) / 100
        self.parent = parent
        self.dialogs = {}
        self.images = {}
        self.current_dialog = None

        self.title("")
        self.resizable(False, False)
        self.transient(parent)
        self.attributes('-toolwindow', True)
        # self.protocol("WM_DELETE_WINDOW", self._hide)
        self.attributes('-alpha', 0.98)
        self.attributes('-transparentcolor', self.ugliest_color)
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

    def new(self, tag: str, 
            text: str = "Are you sure?", icon: str = None, font: tuple = (FONT_B, 20), 
            button_text: str = "Confirm", button_font = (FONT, 18), button_color: str | tuple = (LIGHT_MODE["accent"], DARK_MODE["accent"]), button_function: Callable = lambda: None):

        frame = ctk.CTkFrame(self.parent, fg_color=self.dialog_color, corner_radius=10, border_width=2)    # the border grows inwards, so we don't need to account for it later on
        
        #^ icon
        if icon != None:
            icon_size = (font[1]+10, font[1]+10)
            icon_exist = 1
            if type(icon) == str:
                if icon not in ICONS:
                    raise ValueError(f"{icon} not a valid icon name")
                button_color = (LIGHT_MODE[icon], DARK_MODE[icon])
                frame.configure(border_color = button_color)
                if icon not in self.images:
                    image = ICONS[icon]()
                    self.images[icon]=((ImageTk.PhotoImage(image[0].resize(icon_size)), ImageTk.PhotoImage(image[1].resize(icon_size))))  #! need to add dynamic modes (Light and Dark modes)
            
            canvas = ctk.CTkCanvas(frame, bg=frame._fg_color, bd=0, highlightthickness=0, relief='ridge', width=icon_size[0], height=icon_size[1])
            canvas.create_image(0, 0, anchor="nw", image=self.images[icon][0 if ctk.get_appearance_mode() == "light" else 1])
            canvas.grid(row = 0, column = 0, sticky = "ew", pady = 20, padx=(25, 15))
        else:
            icon_exist = 0
            frame.configure(border_color = button_color)


        #^ Label
        label = ctk.CTkLabel(frame, text=text, font=font, wraplength=450, anchor="w", justify="left")
        label.grid(row = 0, column = icon_exist, sticky = "nsw", pady = 20, padx=(25*(not icon_exist), 20), ipadx = 18)

        #^ Buttons
        buttons_frame = ctk.CTkFrame(frame, fg_color= "transparent")
        cancel_button = ctk.CTkButton(buttons_frame, text="Cancel", command=self._hide, font=button_font,
                                      fg_color=(LIGHT_MODE["primary"], DARK_MODE["primary"]), hover_color=(hvr_clr_g(LIGHT_MODE["primary"], "l"), hvr_clr_g(DARK_MODE["primary"], "d")))
        cancel_button.pack(expand=True, side="left", padx=10)
        Confirm_button = ctk.CTkButton(buttons_frame, text=button_text, command=lambda func = button_function: self._button_function(func), font=button_font,
                                       fg_color=button_color, hover_color=(hvr_clr_g(button_color[0], "l", 10), hvr_clr_g(button_color[1], "d", 10)))
        Confirm_button.pack(expand=True, side="right", padx=10)
        buttons_frame.grid(row = 1, column = icon_exist, sticky = "ne", pady = (2, 15), padx = 10)

        frame.update()
        _frame_cutout = ctk.CTkFrame(self, fg_color=self.ugliest_color, width = frame.winfo_reqwidth()/self.scaleFactor, height = frame.winfo_reqheight()/self.scaleFactor, corner_radius=10)   # the border grows inwards, so we don't need to account for it
        if tag != None:
            self.dialogs[tag] = (frame, _frame_cutout)

    def _button_function(self, func: Callable):
        func()
        self._hide()

    def show(self, dialog):
        # self.parent.wm_attributes("-disabled", 1)
        self.geometry(f"{int(self.parent.winfo_width()/self.scaleFactor)}x{int(self.parent.winfo_height()/self.scaleFactor)}+{self.parent.winfo_x()}+{self.parent.winfo_y()}")
        
        self.deiconify()
        self.bind("<Configure>", self.move_me)
        self.current_dialog = dialog
        self.dialogs[dialog][0].place(relx = 0.5, rely = 0.45, anchor="center")
        self.dialogs[dialog][1].place(relx = 0.5, rely = 0.45, anchor="center")

    def _hide(self):
        self.dialogs[self.current_dialog][0].place_forget()
        self.dialogs[self.current_dialog][1].place_forget()
        self.update()
        self.unbind("<Configure>")
        # self.parent.wm_attributes("-disabled", 0)
        self.withdraw()
        self.current_dialog = None
        
        