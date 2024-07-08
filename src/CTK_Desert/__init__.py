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
        
        # ctk.set_window_scaling(1.25)  # window geometry dimensions #!investigate (to use instead of the scale factor variable)
        self.title("")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scaleFactor = windll.shcore.GetScaleFactorForDevice(0) / 100
        window_width = int(960*scaleFactor)
        window_height = int(640*scaleFactor)
        self.geometry(f'{window_width}x{window_height}+{int((screen_width*scaleFactor/2)-(window_width*scaleFactor/2))}+{int((screen_height*scaleFactor/2)-(window_height*scaleFactor/2))}') #1.5 for the window scale (150%)
        self.minsize(screen_width/2, screen_height/2)
        try:
            self.iconbitmap(os.path.join(os.path.dirname(__file__), "images/empty.ico"))
        except:
            pass

        if not os.path.exists(assets_dir + "\Images"):
            os.mkdir(assets_dir + "\Images")
        if not os.path.exists(assets_dir + "\Pages"):
            os.mkdir(assets_dir + "\Pages")
        if not os.path.isfile(assets_dir + "\preferences.json"):
            with open(os.path.join(assets_dir, 'preferences.json'), 'w') as f:
                json.dump({"theme": "system"}, f, indent=4) #! needs to be edited after moving the themes to a separate file

        Chest.userAssetsDirectory = assets_dir
        self.App_Theme = Chest.Get_Prefered_Theme()
        ctk.set_appearance_mode(f'{self.App_Theme}')
        if self.App_Theme == "system":
            self.App_Theme = ctk.get_appearance_mode()
        self.title_bar_color(TITLE_BAR_HEX_COLORS[f"{self.App_Theme.lower()}"]) #change the title bar color
        
        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())     #? to focus on the widget that was clicked on
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
