import customtkinter as ctk
import os, inspect

from .Core import userChest as Chest
from .Page_base_model import Page_BM
from .Theme import *
from .Widgits import C_Widgits, large_tabs

from .AddPage import AddPage

# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Workspace(Page_BM):
    def __init__(self):
        super().__init__(scrollable=True, start_func=self.on_start)
        self.menu_page_frame = Chest.Manager
        self.frame = self.Scrollable_frame # Parent of all children in this page
        self.mode = ctk.get_appearance_mode()
        self.frame_clr = self.get_scrframe_color()
        self.add_menu_button(r"C:\Users\Morad\Downloads\icons8-reload-64.png", lambda: Chest.reload_page("Workspace"))

        self.icons_path = Chest.Manager.original_icons_dir
        Chest.Store_SubPage("Workspace", AddPage)
        self.cwdgs = C_Widgits(self, self.frame)

        self.workspace_label = ctk.CTkLabel(self.frame, text="Workspace", font=(FONT_B, 40))
        self.workspace_label.pack(fill="x", padx=20, pady=20)

        # Section 1
        self.sectionframe, self.sectionbutton = self.cwdgs.section("Pages", button_text="", button_command=lambda: Chest.Use_SubPage("Workspace", "AddPage"), button_icon=r"C:\Users\Morad\Downloads\icons8-add-96.png", icon_height=30)
        self.sectionbutton.configure(fg_color=self.frame_clr, hover_color=self.frame_clr, width=30, height=30) 
        # Section Unit (options)
        self.pages_tabs = large_tabs(self, self.sectionframe, autofit=True)


    def on_start(self):
        for page in [page for page in self.menu_page_frame.mainpages_dict if page not in ["Workspace", "Settings"]]:
            tab = self.pages_tabs.tab(page, os.path.join(os.path.abspath(os.path.join(self.icons_path, os.pardir)), "preview_window.png"),
                                        button_icon=os.path.join(self.icons_path, "icons8-right-arrow-64.png"),
                                        button_command=lambda page_name = page: self.go(page_name))
            self.pages_tabs.butt0n_icon(tab, button_icon=os.path.join(self.icons_path, "icons8-edit-64.png"), 
                                        button_command=lambda page_name = page: self.edit(page_name))
            self.pages_tabs.butt0n_icon(tab, button_icon=os.path.join(self.icons_path, "icons8-delete-64.png"), override_color=True, 
                                        button_command=lambda page_name = page: self.delete(page_name))            
            
    def go(self, page_name):
        if Chest.MainPages[page_name] is Chest.Displayed_Pages[page_name]:
            Chest.Switch_Page(page_name)
            # print("state 1")
        else:
            Chest.Return_SubPage("Home", "HSubPage")
            Chest.Switch_Page(page_name)
            # print("state 2")

    def edit(self, page_name):
        dir = inspect.getmodule(Chest.MainPages[page_name]).__file__
        os.system('code '+str(dir))
                    
    def delete(self, page_name):
        if f"{page_name}+deletion" not in Chest.Dialog_Manager.dialogs:
            # print("creating a new dialog frame")
            Chest.Dialog_Manager.new(tag=f"{page_name}+deletion", icon="danger", text=f"Are you sure you want to delete {page_name}?", button_text="Delete", 
                                     button_function=lambda: Chest.Manager.delete_page(page_name))
        Chest.Dialog_Manager.show(f"{page_name}+deletion")


