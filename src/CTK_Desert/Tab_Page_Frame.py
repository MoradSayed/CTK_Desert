import os, importlib, copy
import importlib.util
import customtkinter as ctk
from PIL import Image
import inspect, send2trash

import win32api

from .Core import userChest as Chest
from .Theme import *
from .Top_level_dialog import Dialog
from .utils import hvr_clr_g

from .Settings import Settings
from .Workspace import Workspace

class Frame(ctk.CTkFrame):
    
    def __init__ (self, parent, usr_assets_dir, page_choise):
        super().__init__(parent, fg_color=(LIGHT_MODE["background"], DARK_MODE["background"]))
        self.current_dir = os.path.dirname(__file__)
        self.original_icons_dir = f"{self.current_dir}\\images\\Icons\\"
        self.user_icons_dir = os.path.join(usr_assets_dir, "Images\\")
        self.window = parent

        self.menu_relwidth = 0.05
        self.menu_relx = 0
        self.padding = 0.02
        self.menu_opened = False

        self.page_choise = page_choise if page_choise != "" else "Workspace"
        self.last_page = None
        self.tabs = [("Workspace", 0), ("Settings", 3), ] # used to add tabs after importing its class, the 1 or 0 is used to determine if the tab is created at the beginning automatically or do i want to create it manually later 
        
        self.U_Pages_dir = os.path.join(usr_assets_dir, "Pages")
        files = os.listdir(self.U_Pages_dir)                   # get all the files in the directory
        sorted_files = sorted(files, key=lambda x: os.path.getctime(os.path.join(self.U_Pages_dir, x)))            # used to sort the files by creation date so that when they are displayed in the menu the by in order
        module_names = [file[:-3] for file in sorted_files if file.endswith('.py') and file != '__init__.py']   # get all the file names without the .py extension
        for module_name in module_names:
            self.ext_pages_importer(module_name)

        self.buttons = {}               # used to save all the tab buttons for later configuration
        self.mainpages_dict = {}
        self.subpages_dict = {}
        # we make it have the same pages as the main pages (as those are the ones that will be displayed), then we make it independent of the main pages so that it show the actual displayed pages
        self.pages_dict = self.mainpages_dict   
        
        self.window.update()
        self.window_width = self.window.winfo_width()
        self.window_height = self.window.winfo_height()

        self.window.bind("<Configure>", self.update_state_checker)
        self.size_event = None
        self.updating = False

        self.dialog_widget = Dialog(self.window)

        self.menu()
        self.page()

        self.pack(expand = True, fill = "both")

        directory = self.original_icons_dir if self.page_choise == "Workspace" or self.page_choise == "Settings" else self.user_icons_dir
        self.buttons[self.page_choise].configure(image=ctk.CTkImage(Image.open(f"{directory}{self.page_choise}_l_s.png"), Image.open(f"{directory}{self.page_choise}_d_s.png"), (45,45) if self.page_choise == "Workspace" else (30,30)))
        self.pages_dict[self.page_choise].show_page()


    def menu(self):
        self.menu_frame = ctk.CTkFrame(self, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), width=70)
        self.menu_frame.pack(side="left", fill="y", pady=(0, 27), padx=(0, 20))
        self.menu_frame.pack_propagate(0)

        self.logo_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        self.logo_frame.pack(fill="x", ipady=5, padx=5)
        self.tabs_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        self.tabs_frame.pack(fill="x", padx=5, pady = 5)    
        self.apps_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        self.apps_frame.pack(fill="both", expand=True, padx=5, pady = 5)
        self.user_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        self.user_frame.pack(fill="x", padx=5)
        self.menu_frames_dict = {"0": self.logo_frame, "1": self.tabs_frame, "2": self.apps_frame, "3": self.user_frame}

        for tab in self.tabs:
            button = self.tab(tab[0], self.menu_frames_dict[str(tab[1])], (45,45) if tab[0] == "Workspace" else (30,30))    #create all the tabs
            self.buttons[tab[0]] = button #saving them for later configuration in the color

        ctk.CTkFrame(self.menu_frame, fg_color=("#b3b3b3","#4c4c4c"), height=2).pack(fill="x", padx=10, after=self.tabs_frame)
        ctk.CTkFrame(self.menu_frame, fg_color=("#b3b3b3","#4c4c4c"), height=2).pack(fill="x", padx=10, after=self.apps_frame)

    def page(self):
        self.page_frame = ctk.CTkFrame(self, fg_color="transparent")
        Chest._D__Setup_Chest(self.window, self)        #^ Initialize the Chest
        for name in self.tabs:
            self.mainpages_dict[name[0]] = eval(name[0] + "()")    #calls all the contents of the tabs (but not displaying them) and passing the arguments, while saving them in a dict for later use
        
        self.page_frame.pack(side="left", fill="both", expand=True, pady=(0, 27), padx=(0, 20))
        
        self.pages_dict = copy.copy(self.mainpages_dict)
        Chest.Displayed_Pages = self.pages_dict
           
    def menu_button_command(self): # currently not used
        if self.menu_opened:
            self.menu_frame.configure(width=70)
            self.update()
            self.menu_opened = False

        else:
            self.menu_frame.configure(width=200)
            self.update()
            self.menu_opened = True

        self.pages_dict[self.page_choise].Page_update_manager()

    def tab(self, tab, parent, btn_size=(30,30)):
        directory = self.original_icons_dir if tab == "Workspace" or tab == "Settings" else self.user_icons_dir
        button = ctk.CTkButton(parent, text="", fg_color="transparent", hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), image=ctk.CTkImage(Image.open(f"{directory}{tab.lower()}_l.png"), Image.open(f"{directory}{tab.lower()}_d.png"), btn_size), command = lambda: self.page_switcher(f'{tab}'))
        button.pack(ipadx = 10, pady=10)
        return button

    def page_switcher(self, buttonID):
        if buttonID != self.page_choise and self.pages_dict[buttonID].openable == True:
            if self.pages_dict[self.page_choise].Leaving("global"):
                self.pages_dict[self.page_choise].hide_page()
                directory = self.original_icons_dir if self.page_choise == "Workspace" or self.page_choise == "Settings" else self.user_icons_dir
                self.buttons[self.page_choise].configure(image=ctk.CTkImage(Image.open(f"{directory}{self.page_choise.lower()}_l.png"), Image.open(f"{directory}{self.page_choise.lower()}_d.png"), (45,45) if self.page_choise == "Workspace" else (30,30)))
                self.last_page = self.page_choise
                # print(self.page_choise, ">>", buttonID)
                self.page_choise = f'{buttonID}'
                directory = self.original_icons_dir if buttonID == "Workspace" or buttonID == "Settings" else self.user_icons_dir
                self.buttons[buttonID].configure(image=ctk.CTkImage(Image.open(f"{directory}{buttonID.lower()}_l_s.png"), Image.open(f"{directory}{buttonID.lower()}_d_s.png"), (45,45) if buttonID == "Workspace" else (30,30)))
                self.pages_dict[buttonID].show_page()

    def update_state_checker(self, event):
        if ((event.width != self.window_width or event.height != self.window_height) and (event.widget == self.window)):
            self.size_event = event
            if not self.updating:    
                # print("detected")
                self.updating = True
                self.pack_forget()
                self.check_click_state()

    def check_click_state(self):
        if win32api.GetKeyState(0x01) < 0:
            self.after(50, self.check_click_state)
        else:
            # print("packing and updating")
            self.pack(expand = True, fill = "both")
            self.update_sizes()
            self.updating = False

    def update_sizes(self): 
        self.window_width = self.size_event.width
        self.window_height = self.size_event.height
        # self.menu_relwidth = 75/self.window_width
        
        self.pages_dict[self.page_choise].Page_update_manager()

    def ext_pages_importer(self, module_name, reload=False):
        in_directory = self.U_Pages_dir
        reldotpath = in_directory.replace("/", ".").replace("\\", ".")
        if reload:
            # in the state of the reload, the module_name isn't actually the name of the module, rather the class itself
            module = importlib.reload(inspect.getmodule(module_name))
            module_name = module_name.__class__.__name__
        else:
            # in the state of the loading, the module_name the name of the module
            module = importlib.import_module(f'{reldotpath}.{module_name}', ".")
            self.tabs.append((f"{module_name}", 1))             # add the class to the tabs list
        try:            
            globals()[module_name] = getattr(module, module_name)   # import the class, and save it in the globals() so it can be used later
        except Exception as e:
            print(f"Failed to import module {module_name}: {e}")

    def new_page_constructor(self, name, switch: bool = True):
        self.ext_pages_importer(name)

        self.pages_dict[name] = eval(name + "()")    #calls all the contents of the tabs (but not displaying them) and passing the arguments, while saving them in a dict for later use

        self.buttons[name] = self.tab(name, self.tabs_frame)    # adding its button to the menu

        self.mainpages_dict[name] = self.pages_dict[name]   # saving it to the main pages

        if switch:
            self.page_switcher(name)

    def reload_page(self, name, args):
        if name in self.mainpages_dict:
            self.ext_pages_importer(self.mainpages_dict[name], reload=True)

            self.mainpages_dict[name] = eval(name + "(*args)")

            if self.page_choise == name:
                self.pages_dict[name].destroy_page()
                self.pages_dict[name] = self.mainpages_dict[name]
                self.pages_dict[name].show_page()
            else:
                self.pages_dict[name] = self.mainpages_dict[name]
                self.page_switcher(name)
        
        elif name in self.subpages_dict:
            splited_name = name.split(".")
            class_name = splited_name[-1]
            # subpage_dir = os.path.relpath(os.path.dirname(inspect.getfile(self.subpages_dict[name].__class__)))
            self.ext_pages_importer(self.subpages_dict[name], reload=True)

            self.subpages_dict[name] = eval(class_name + "(*args)")

            if self.page_choise == splited_name[0]:
                self.pages_dict[splited_name[0]].destroy_page()
                self.pages_dict[splited_name[0]] = self.subpages_dict[name]
                self.pages_dict[splited_name[0]].show_page()
            else:
                self.pages_dict[splited_name[0]] = self.subpages_dict[name]
                self.page_switcher(splited_name[0])

    def delete_page(self, name, delete_subpages: bool = False, shift_del: bool = False):
        
        if name == self.page_choise:
            Chest.Dialog_Manager.new("DsrtSys:Err-Del", "You can't delete a page that's in use", "danger", button_text="")
            Chest.Dialog_Manager.show("DsrtSys:Err-Del")
            return False
        dir = inspect.getmodule(self.mainpages_dict[name]).__file__

        # Deleting Mainpage from the current session
        self.mainpages_dict[name].destroy_page()
        self.buttons[name].configure(image="")
        self.buttons[name].destroy()
        self.buttons.pop(name)
        self.pages_dict.pop(name)
        self.mainpages_dict.pop(name)
        # Deleting Subpages (if the option is checked) from the current session and from the system
        if delete_subpages:
            deletion_names = []
            for key in self.subpages_dict:
                if key.split(".")[0] == name:
                    deletion_names.append(key)
            for key in deletion_names:
                sub_page_dir = inspect.getfile(self.subpages_dict[key].__class__)
                self.subpages_dict[key].destroy_page()
                self.subpages_dict.pop(key)
                if shift_del:
                    os.remove(sub_page_dir)
                else:
                    send2trash.send2trash(sub_page_dir)
        
        # Deleting Mainpage (code file, image files) from the system
        if shift_del:
            os.remove(dir)
        else:
            send2trash.send2trash(dir)
        for n, i in enumerate(ICONS):
            if shift_del:
                os.remove(os.path.join(self.user_icons_dir, f"{name.lower()}{i}.png"))
            else:
                send2trash.send2trash(os.path.join(self.user_icons_dir, f"{name.lower()}{i}.png"))
            if n == 3:
                break

        return True

    def Subpage_Construction(self, Main_page: str, Sub_page, keep: bool = True, args: tuple = ()): 
        """Constructs the Subpage, so that it is ready to be opened at any moment

        Args:
            Main_page (str): used to get the name of the main page class "case sensitive"
            Sub_page (Class): used to initialize the subpage class with the necessary parameters
            keep (bool, optional): keep the subpage if it already exists. Defaults to True.
            args (tuple, optional): arguments to be passed to the subpage class. Defaults to ().
        """
        
        domain = f"{Main_page}.{Sub_page.__name__}"
        if keep and domain in self.subpages_dict:
            pass
        else:
            subpage_inited = Sub_page(*args)
            self.subpages_dict[domain] = subpage_inited

    def Subpage_init(self, Main_page_name: str, Sub_page_name: str): 
        """Opens the SubPage

        Args:
            Main_page (str): used to get the name of the main page class "case sensitive"
            Sub_page (str): used to get the name of the sub page class "case sensitive"
        """

        MN_split = Main_page_name.split(".")[0] if "." in Main_page_name else Main_page_name

        self.pages_dict[MN_split].hide_page()

        self.pages_dict[MN_split] = self.subpages_dict[f"{Main_page_name}.{Sub_page_name}"]
        
        self.pages_dict[MN_split].show_page()

    def Subpage_return(self, Main_page_name: str, Sub_page_name: str): 
        """Closes the SubPage

        Args:
            Main_page (str): used to get the name of the main page class "case sensitive"
            Sub_page (str): used to get the name of the sub page class "case sensitive"
        """

        MN_split = Main_page_name.split(".")[0] if "." in Main_page_name else Main_page_name

        if self.pages_dict[MN_split].Leaving("local"):
            self.pages_dict[MN_split].hide_page()

            if "." in Main_page_name:
                self.pages_dict[MN_split] = self.subpages_dict[Main_page_name]
            else:
                self.pages_dict[MN_split] = self.mainpages_dict[MN_split]

            self.pages_dict[MN_split].show_page()

                
#### end of the class