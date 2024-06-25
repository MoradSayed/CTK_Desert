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

        # Section 1
        self.appearance_sec = self.c_wdgts.section("Appearance")
        # Section Units (options)
            # Combobox 
        self.theme_op   = self.c_wdgts.section_unit(section=self.appearance_sec, title="Theme", widget="combobox", values=["System", "Light", "Dark"], command=Chest.Set_Prefered_Theme, default=Chest.Get_Prefered_Theme().capitalize()) # default=self.window.App_Theme.capitalize()   This was the old one
        #   # Button
        self.Reset_op   = self.c_wdgts.section_unit(section=self.appearance_sec, title="Add a Section", widget="button", command=self.test_func, default= "+")
        #   # Checkbox
        # self.allow_op   = self.c_wdgts.section_unit(section=self.appearance_sec, title="Allow Themes to Change", widget="checkbox", command= lambda: print("NO func implemented _Chk"))

        self.Advanced_Settings = self.c_wdgts.section("Advanced Settings")
        # Section Units (options)
        self.WS_Var = ctk.BooleanVar(value=self.menu_page_frame.mainpages_dict["Workspace"].openable)
        self.Dev_mode   = self.c_wdgts.section_unit(section=self.Advanced_Settings, title="Enable Dev mode", widget="checkbox", command= lambda : self.WS_openable_func(), default=self.WS_Var)
        
        self.addables_frame.pack(fill="x")

    def WS_openable_func(self):
        self.menu_page_frame.mainpages_dict["Workspace"].openable = self.Dev_mode.gval()

    def test_func(self):
        if self.test_num == 0:
            self.test_num += 1
            self.tst1 = self.c_wdgts.section("WELL Well well...")
        self.c_wdgts.add_tab(self.tst1, f"img #{random.randint(100000, 999999)}", "C:\\Users\\Morad\\Downloads\\wallpaperflare.com_wallpaper.jpg", "l")

