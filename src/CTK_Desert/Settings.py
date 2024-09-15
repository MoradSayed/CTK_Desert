import json, os, random

import customtkinter as ctk

from .Core import userChest as Chest
from .Page_base_model import Page_BM
from .Theme import theme
from .Widgits import C_Widgits, small_tabs


# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Settings(Page_BM):
    def __init__(self):
        super().__init__()
        self.window = Chest.Window
        self.menu_page_frame = Chest.Manager
        self.on_theme_change_func = None
        self.frame = self.get_pf()
        self.addables_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.c_wdgts = C_Widgits(page_class = self, parent = self.addables_frame)
        self.test_num = 0

        self.settings_label = ctk.CTkLabel(self.frame, text="Settings", font=(theme.font_B, 40))
        self.settings_label.pack(fill="x", padx=20, pady=(20, 0))

        self.appearance_sec = self.c_wdgts.section("Appearance")
        self.theme_op, themeVar = self.c_wdgts.ComboBox_unit(self.appearance_sec, "Mode", ["System", "Light", "Dark"], Chest.Get_Prefered_Theme_Mode().capitalize(), Chest.Set_Prefered_Theme_Mode)  #? combobox sends an argument with the chosen value
        self.colors_op   = self.c_wdgts.Button_unit(self.appearance_sec, "Colors", "Browse", self.open_pref)

        self.Advanced_Settings = self.c_wdgts.section("Advanced Settings")
        self.Dev_mode, self.WSstate   = self.c_wdgts.CheckBox_unit(self.Advanced_Settings, "Enable Dev mode", self.menu_page_frame.mainpages_dict["Workspace"].openable, self.WS_openable_func)
        
        self.addables_frame.pack(fill="x")

    def WS_openable_func(self):
        self.menu_page_frame.mainpages_dict["Workspace"].openable = self.WSstate.get()

    def open_pref(self):
        os.startfile(os.path.join(Chest.userAssetsDirectory, "preferences.json"), )
