from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Page_base_model import Tile_BM

import os, importlib, copy, glob
import importlib.util
import customtkinter as ctk
from tkinter import Event
from PIL import Image
import inspect
from typing import Dict, Union

from .Core import userChest as Chest
if Chest._OS == "Windows":
    import win32api, send2trash
    _LC_state = lambda: win32api.GetKeyState(0x01) < 0
elif Chest._OS == "Linux":
    from Xlib import X, display
    _linux_disp = display.Display()             # Initialize the X server connection
    _linux_root = _linux_disp.screen().root     # Get the root window
    def _LC_state():
        # Query the current state of the pointer (mouse)
        pointer_data = _linux_root.query_pointer()
        # Check if the left mouse button is pressed (Button1Mask)
        left_button_mask = X.Button1Mask
        is_pressed = pointer_data.mask & left_button_mask
        return bool(is_pressed)
# elif Chest._OS == "Darwin":
#     pass    #! to be implemented

from .Theme import theme
from .Top_level_dialog import Dialog
from .utils import hvr_clr_g
from .Page_base_model import Page_BM

class Frame(ctk.CTkFrame):

    def __init__ (self, parent, usr_assets_dir, page_choise):
        super().__init__(parent, fg_color=theme.Cbg)
        self.current_dir = os.path.dirname(__file__)
        self.original_icons_dir = os.path.join(self.current_dir, "images", "Icons")
        self.user_icons_dir = os.path.join(usr_assets_dir, "Images")
        self.window = parent
        self.update_cover = ctk.CTkFrame(parent, fg_color="transparent")

        self.menu_relwidth = 0.05
        self.menu_relx = 0
        self.padding = 0.02
        self.menu_opened = False

        self.page_choise = page_choise if page_choise else "Workspace"
        self.last_page = None
        self.tabs = [("Workspace", 0), ("Settings", 3), ] # used to add tabs after importing its class, the 1 or 0 is used to determine if the tab is created at the beginning automatically or do i want to create it manually later

        self.U_Pages_dir = os.path.join(usr_assets_dir, "Pages")
        files = os.listdir(self.U_Pages_dir)                   # get all the files in the directory
        sorted_files = sorted(files, key=lambda x: os.path.getctime(os.path.join(self.U_Pages_dir, x)))            # used to sort the files by creation date so that when they are displayed in the menu the by in order
        module_names = [file[:-3] for file in sorted_files if file.endswith('.py') and file != '__init__.py']   # get all the file names without the .py extension

        self.buttons:Dict[str, ctk.CTkButton] = {}               # used to save all the tab buttons for later configuration
        self.classes_ref:Dict[str, list[Union[type[Page_BM], type[Tile_BM]]]] = {"pages": {}, "tiles": {}}
        self.mainpages_dict:Dict[str, Page_BM] = {}
        self.tiles:Dict[str, Tile_BM] = {}

        self.window.update()
        self.window_width = self.window.winfo_width()
        self.window_height = self.window.winfo_height()
        self.global_updates_list = []   #? used to update any widget that isn't associated with a specific page (ex: Notifications)

        self.window.bind("<Configure>", self.update_state_checker)
        self.size_event = None
        self.updating = False

        #! Atterntion here!!!!!!!!!!!
        if Chest._OS == "Windows":
            self.dialog_widget = Dialog(self.window)
        else:
            self.dialog_widget = None

        self.scroll_bar_frame = ctk.CTkFrame(self, fg_color="transparent", width=20)
        self.scroll_bar_frame.pack(side="right", fill="y", pady=(0, 27))
        self.scroll_bar_frame.pack_propagate(0)
        self.menu()
        self.page(module_names)
        self.menu_btn_allocator()

        self.pack(expand = True, fill = "both")

        directory = self.original_icons_dir if self.page_choise == "Workspace" or self.page_choise == "Settings" else self.user_icons_dir
        self.buttons[self.page_choise].configure(image=ctk.CTkImage(Image.open(os.path.join(directory, f"{self.page_choise.lower()}_l_s.png")), Image.open(os.path.join(directory, f"{self.page_choise.lower()}_d_s.png")), (45,45) if self.page_choise == "Workspace" else (30,30)))
        self.mainpages_dict[self.page_choise].show_page()


    def menu(self):
        self.menu_frame = ctk.CTkFrame(self, fg_color=hvr_clr_g(theme.Cbg, "ld"), width=70)
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

        ctk.CTkFrame(self.menu_frame, fg_color=("#b3b3b3","#4c4c4c"), height=2).pack(fill="x", padx=10, after=self.tabs_frame)
        ctk.CTkFrame(self.menu_frame, fg_color=("#b3b3b3","#4c4c4c"), height=2).pack(fill="x", padx=10, after=self.apps_frame)

    def menu_btn_allocator(self):
        for tab in self.tabs:
            button = self.tab(tab[0], self.menu_frames_dict[str(tab[1])], (45,45) if tab[0] == "Workspace" else (30,30))    #create all the tabs
            self.buttons[tab[0]] = button #saving them for later configuration in the color

    def page(self, module_names):
        self.page_frame = ctk.CTkFrame(self, fg_color="transparent")
        Chest._D__Setup_Chest(self.window, self)        #^ Initialize the Chest
        for module_name in module_names:
            self.ext_pages_importer(module_name)
        from .Settings import Settings
        from .Workspace import Workspace
        for name in self.tabs:
            self.mainpages_dict[name[0]] = eval(name[0] + "()")    #calls all the contents of the tabs (but not displaying them) and passing the arguments, while saving them in a dict for later use

        self.page_frame.pack(side="left", fill="both", expand=True, pady=(0, 27))

    def menu_button_command(self): #! currently not used
        if self.menu_opened:
            self.menu_frame.configure(width=70)
            self.update()
            self.menu_opened = False

        else:
            self.menu_frame.configure(width=200)
            self.update()
            self.menu_opened = True

        self.mainpages_dict[self.page_choise].update_width()

    def tab(self, tab, parent, btn_size=(30,30)):
        directory = self.original_icons_dir if tab == "Workspace" or tab == "Settings" else self.user_icons_dir
        button = ctk.CTkButton(parent, text="", fg_color="transparent", hover_color=hvr_clr_g(theme.Cbg, "ld"), image=ctk.CTkImage(Image.open(os.path.join(directory, f"{tab.lower()}_l.png")), Image.open(os.path.join(directory, f"{tab.lower()}_d.png")), btn_size), command = lambda: self.page_switcher(f'{tab}'))
        button.pack(ipadx = 10, pady=10)
        return button

    def page_switcher(self, buttonID):
        if buttonID != self.page_choise and self.mainpages_dict[buttonID].openable and self.mainpages_dict[self.page_choise].hide_page("global"):
            directory = self.original_icons_dir if self.page_choise == "Workspace" or self.page_choise == "Settings" else self.user_icons_dir
            self.buttons[self.page_choise].configure(image=ctk.CTkImage(Image.open(os.path.join(directory, f"{self.page_choise.lower()}_l.png")), Image.open(os.path.join(directory, f"{self.page_choise.lower()}_d.png")), (45,45) if self.page_choise == "Workspace" else (30,30)))
            self.last_page = self.page_choise
            # print(self.page_choise, ">>", buttonID)
            self.page_choise = f'{buttonID}'
            directory = self.original_icons_dir if buttonID == "Workspace" or buttonID == "Settings" else self.user_icons_dir
            self.buttons[buttonID].configure(image=ctk.CTkImage(Image.open(os.path.join(directory, f"{buttonID.lower()}_l_s.png")), Image.open(os.path.join(directory, f"{buttonID.lower()}_d_s.png")), (45,45) if buttonID == "Workspace" else (30,30)))
            self.mainpages_dict[buttonID].show_page()

    def update_state_checker(self, event: Event):
        if ((event.width != self.window_width or event.height != self.window_height) and (event.widget == self.window)):
            self.size_event = event
            if not self.updating:
                # print("detected")
                self.updating = True
                self.update_cover.lift()
                self.update_cover.place(x=0, y=0, relwidth=1, relheight=1)
                self.pack_forget()
                self.check_click_state()

    def check_click_state(self):
        if _LC_state():     # it will check if the left mouse button is pressed (Custom function for each OS)
            self.after(50, self.check_click_state)
        else:
            # print("packing and updating")
            self.pack(expand = True, fill = "both")
            self.update_sizes()
            self.update()
            self.update_cover.place_forget()
            self.update()
            self.updating = False

    def update_sizes(self):
        if self.size_event.width != self.window_width:
            self.mainpages_dict[self.page_choise].update_width()

        for func in self.global_updates_list:
            func()

        self.window_width = self.size_event.width
        self.window_height = self.size_event.height

    def ext_pages_importer(self, module_name, reload: bool =False):
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

        return eval(module_name)

    def new_page_constructor(self, name: str, switch: bool):
        self.ext_pages_importer(name)

        self.mainpages_dict[name] = eval(name + "()")    #calls all the contents of the tabs (but not displaying them) and passing the arguments, while saving them in a dict for later use

        self.buttons[name] = self.tab(name, self.tabs_frame)    # adding its button to the menu

        if switch:
            self.page_switcher(name)

    def reload_page(self, instance: Union["Page_BM", "Tile_BM"], args):   #todo: deprecate this method after adding its equivalent in the Page_BM
        name = instance.__class__.__name__
        self.ext_pages_importer(instance, reload=True)
        new_instance: Union["Page_BM", "Tile_BM"] = eval(name + "(*args)")
        new_instance._name = instance._name
        instance.destroy_page()
        if name in self.mainpages_dict:
            self.mainpages_dict[name] = new_instance
            new_instance.show_page()
        #todo: do we implement a switch to the new page?
        return new_instance

        #! Old code. to be deleted after testing the new code
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

    def delete_page(self, object: Union[Page_BM, "Tile_BM"], delete_subpages: bool, shift_del: bool=False):   #todo: move this method to the Page_BM and Tile_BM
        if shift_del==True and Chest._OS != "Windows":
            Chest.Dialog_Manager.new("DsrtSys:Err-Del", "Shift+Delete is only available on Windows", "danger", button_text="")
            Chest.Dialog_Manager.show("DsrtSys:Err-Del")
            return False

        #todo: make it possible to delete a page you are currently on
        if object == self.page_choise:
            Chest.Dialog_Manager.new("DsrtSys:Err-Del", "You can't delete a page that's in use", "danger", button_text="")
            Chest.Dialog_Manager.show("DsrtSys:Err-Del")
            return False
        dir = inspect.getmodule(object).__file__
        name = object.__class__.__name__

        # Deleting Mainpage from the current session
        object.destroy_page()
        if isinstance(object, Page_BM):
            self.buttons[name].configure(image="")
            self.buttons[name].destroy()
            self.buttons.pop(name)
            self.mainpages_dict.pop(name)
        # Deleting Subpages (if the option is checked) from the current session and from the system
        if delete_subpages:
            deletion_names: list["Tile_BM"] = []
            for tile in object._linked_tiles:
                if len(tile._source_tile):
                    deletion_names.append(tile)
            for tile in deletion_names:
                sub_page_dir = inspect.getfile(tile.__class__)
                tile.destroy_page()
                if shift_del:
                    os.remove(sub_page_dir)
                else:
                    send2trash.send2trash(sub_page_dir)

        # Deleting Mainpage (code file, image files) from the system
        if shift_del:
            os.remove(dir)
        else:
            send2trash.send2trash(dir)
        for n, file in enumerate(glob.glob(f"{self.user_icons_dir}/{name.lower()}*")):
            if shift_del:
                os.remove(file)
            else:
                send2trash.send2trash(file)
            if n == 3:
                break

        return True
