import json, os, inspect
import customtkinter as ctk
try:
    from ctypes import byref, c_int, sizeof, windll 
except:
    pass
from .Tab_Page_Frame import Frame
from .Core import userChest as Chest
from .Theme import *

class Desert(ctk.CTk):
    def __init__ (self, assets_dir, page_choise="Settings", spin=False):
        super().__init__(fg_color= (LIGHT_MODE["background"], DARK_MODE["background"]))
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module is not None:
            if os.path.samefile(os.path.dirname(os.path.abspath(caller_module.__file__)), os.getcwd()):
                pass                        
            else:
                os.chdir(os.path.dirname(os.path.abspath(caller_module.__file__)))
                
        if os.path.isdir(assets_dir):
            pass
        else:
            raise FileNotFoundError(f"Directory '{assets_dir}' not found")
        
        self.title("")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scaleFactor = windll.shcore.GetScaleFactorForDevice(0) / 100
        self.geometry(f'1200x800+{int((screen_width*scaleFactor/2)-(1200*scaleFactor/2))}+{int((screen_height*scaleFactor/2)-(800*scaleFactor/2))}') #1.5 for the window scale (150%)
        self.minsize(screen_width/2, screen_height/2)
        try:
            self.iconbitmap(os.path.join(os.path.dirname(__file__), "images/empty.ico"))
        except:
            pass

        with open(os.path.join(os.path.dirname(__file__), 'preferences.json'), 'r') as f:
            theme_data = json.load(f)
        self.App_Theme = theme_data["theme"]
        ctk.set_appearance_mode(f'{self.App_Theme}')
        self.theme_mode = ctk.get_appearance_mode()
        self.title_bar_color(TITLE_BAR_HEX_COLORS[f"{self.theme_mode.lower()}"]) #change the title bar color

        if not os.path.exists(assets_dir + "\Images"):
            os.mkdir(assets_dir + "\Images")
        if not os.path.exists(assets_dir + "\Pages"):
            os.mkdir(assets_dir + "\Pages")
        
        self.Home = Frame(self, usr_assets_dir=assets_dir, page_choise=page_choise)
        
        if spin:
            self.mainloop()

    def title_bar_color(self, color):
        try:
            windll.dwmapi.DwmSetWindowAttribute(
                windll.user32.GetParent(self.winfo_id()), 
                35, 
                byref(c_int(color)), 
                sizeof(c_int)
                )
        except:
            pass

        #^ Remove the title bar
        #! well need to edit the Dialog widgit and edit the Frame layout
        # # Constants from the Windows API
        # GWL_STYLE = -16
        # WS_CAPTION = 0x00C00000
        # WS_SYSMENU = 0x80000

        # hwnd = windll.user32.GetParent(self.winfo_id())
        # current_style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        # new_style = current_style & ~WS_CAPTION & ~WS_SYSMENU
        # windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
        # windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x27)  # Update the window to apply the changes
