import json, os, random
from winreg import *

import customtkinter as ctk

from .Core import userChest as Chest
from .Page_base_model import Page_BM
from .Theme import *
from .Widgits import C_Widgits


# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Settings(Page_BM):
    def __init__(self):
        super().__init__()
        self.window = Chest.Window
        self.menu_page_frame = Chest.Manager
        self.on_theme_change_func = None
        self.frame = self.Scrollable_frame
        self.addables_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.c_wdgts = C_Widgits(page_class = self, parent = self.addables_frame)
        self.test_num = 0

        self.settings_label = ctk.CTkLabel(self.frame, text="Settings", font=(FONT_B, 40))
        self.settings_label.pack(fill="x", padx=20, pady=20)

        self.appearance_sec = self.c_wdgts.section("Appearance")
        self.theme_op, themeVar = self.c_wdgts.ComboBox_unit(self.appearance_sec, "Theme", ["System", "Light", "Dark"], Chest.Get_Prefered_Theme().capitalize(), Chest.Set_Prefered_Theme)  #? combobox sends an argument with the chosen value
        self.Reset_op   = self.c_wdgts.Button_unit(self.appearance_sec, "Add a Section", "+", self.test_func)

        self.Advanced_Settings = self.c_wdgts.section("Advanced Settings")
        self.Dev_mode, self.WSstate   = self.c_wdgts.CheckBox_unit(self.Advanced_Settings, "Enable Dev mode", self.menu_page_frame.mainpages_dict["Workspace"].openable, self.WS_openable_func)
        
        self.addables_frame.pack(fill="x")

    def WS_openable_func(self):
        self.menu_page_frame.mainpages_dict["Workspace"].openable = self.WSstate.get()

    def test_func(self):
        if self.test_num == 0:
            self.test_num += 1
            self.tst1 = self.c_wdgts.section("WELL Well well...")
        self.c_wdgts.add_tab(self.tst1, f"img #{random.randint(100000, 999999)}", "C:\\Users\\Morad\\Downloads\\wallpaperflare.com_wallpaper.jpg", "l")

