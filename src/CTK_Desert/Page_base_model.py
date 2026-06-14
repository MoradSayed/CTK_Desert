from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .TilingWindowManager import TilingWindowManager

import tkinter as tk
import customtkinter as ctk
from typing import Union, Tuple, Callable
import threading, time
from typing import NamedTuple
from bidict import bidict

from .Core  import userChest as Chest
from .Theme import theme, change_pixel_color
from .utils import hvr_clr_g
from .Minimal_scrollbar import Scrollbar

class TileConfig(NamedTuple):
    row: int
    column: int
    rowspan: int = 1
    columnspan: int = 1
    expandable: bool = True
    width: float = 1
    height: float = 1
from .GridLayout import GridLayoutEditor

class Page_BM(ctk.CTkFrame): #the final frame to use is the "self.content_frame"
    def __init__(self, layout:dict=None):
        self.parent = Chest.PageParent
        super().__init__(self.parent, fg_color="transparent")

        self.widget_str = str(self)
        self._name = self.widget_str.split("!")[-1]
        self.openable = True            #? can the page be opened now or not
        self._displayed = False             #? is Page currently opened or not
        self._started = False

        self.layout = layout
        self._grid_editor = GridLayoutEditor(self, 1, 1, 5)
        if layout:
            self._cells: dict[str, ctk.CTkFrame] = self._grid_editor.load_layout(layout)
        else:
            self._cells: dict[str, ctk.CTkFrame] = {}  #todo: provide the UI to create the layout from gridlayout

        self._current_tile: bidict[ctk.CTkFrame, str] = bidict({cell: t_name for t_name, cell in self._cells.items()})
        self._disconnected_tiles: list[str] = list(self._cells.keys())

        for tile_name in self._disconnected_tiles:
            if tile_name not in Chest.Manager.tiles:
                class_name = tile_name.split("-")[0].lower()
                Chest.Manager.tiles[tile_name] = Chest.Manager.classes_ref["tiles"][class_name]()
                Tile_BM.get_tile(tile_name)._name = tile_name

    def update_width(self):
        for tile_name in self._current_tile.values():
            Tile_BM.get_tile(tile_name).update_width()
        if self._displayed:
            threading.Thread(target=self._bg_thread_creator, daemon=True).start()

    def show_page(self):
        self._displayed = True
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        for tile_name in self._disconnected_tiles:
            Tile_BM.get_tile(tile_name)._process_pack_req(self._current_tile.inverse[tile_name])
        self._disconnected_tiles.clear()
        for tile_name in self._current_tile.values():
            Tile_BM.get_tile(tile_name).lift()
            Tile_BM.get_tile(tile_name)._on_show_callbacks()
        if not self._started:
            self._started = True

    def hide_page(self, event) -> bool:
        results = [Tile_BM.get_tile(tile_name)._on_leave_check(event) for tile_name in self._current_tile.values()]
        state = all(results)
        if state:
            for tile_name in self._current_tile.values():
                Tile_BM.get_tile(tile_name)._process_unpack_req()
            self.place_forget()
            self._displayed = False
        return state

    def destroy_page(self):
        return #todo: recheck how this would go properly (a page can be in multiple windows at the same time)
        for tile in self._tiles:
            tile.destroy_page()

    def _bg_thread_creator(self):
        for page in {*Chest.MainPages.values()} - {self}:
            if page._started:
                threading.Thread(target=page._bg_update, daemon=True).start()

    def _bg_update(self):
        openable = self.openable
        self.openable = False
        self.place(relx=0, rely=1, relwidth=1)
        for tile_name in {*self._current_tile.values()} - {*self._disconnected_tiles}:
            Tile_BM.get_tile(tile_name)._bg_update()
        self.place_forget()
        self.openable = openable

class Tile_BM(ctk.CTkFrame):
    def __init__(self, #page: Page_BM,
                 color:       Tuple[str, str] = hvr_clr_g(theme.Cbg, "ld"),
                 scrollable:  bool = True,
                 start_func:  Callable[[None], None] = lambda: None,
                 pick_func:   Callable[[None], None] = lambda: None,
                 tile_func:   Callable[[Page_BM], None] = lambda page: None,
                 update_func: Callable[[None], None] = lambda: None,
                 leave_func:  Callable[[str], bool] = lambda event: True,
              #* destroy_func:Callable[[None], None] = lambda: None,
                 scrollbar_inside: bool = False,
                 container_pack_side: str = "left",
                 page_pack_side: str = "left",                  #! Propaply not needed anymore (was used with inner scrollbar - with pack)
                 ):
        self.parent = Chest.PageParent
        self.color = color
        self._current_page : Page_BM = None
        self._in_container : ctk.CTkFrame = None
        super().__init__(self.parent, fg_color="transparent")

        self.widget_str = str(self)
        self._name = self.widget_str.split("!")[-1]
        self.scrollable = scrollable
        self.openable = True            #? can the page be opened now or not
        self.opened = False             #? is Page currently opened or not
        self.pickable = False           #? has the page started at least once or not

        self.container_pack_side: str = container_pack_side
        self._is_width_fixed: bool = False
        self.scrollbar_inside:bool = scrollbar_inside
        # self._managed_by_tile:bool = False
        # self.tiling_manager:"TilingWindowManager" = None      #! shouldn't be needed

        self._source_tile : dict[Page_BM, str] = {} #? source_tile._name for each page
        self._linked_tiles: list[str] = []              #? linked_tiles._name

        self.starting_call_list = []
        self.picking_call_list = []
        self.updating_call_list = []
        self.leaving_call_list = []
        self.start_func = start_func
        self.pick_func = pick_func
        self.tile_func = tile_func
        self.update_func = update_func
        self.leave_func = leave_func

        if self.scrollable:
            self.scrolled = 0
            self.Scrollable_canvas = tk.Canvas(self, background=color[0] if ctk.get_appearance_mode() == "Light" else color[1],
                                               scrollregion = (0, 0, self.winfo_width(), 10000), yscrollincrement=1,
                                               bd=0, highlightthickness=0, relief = 'ridge')
            self.Scrollable_canvas.pack(fill="both", expand=True, side=page_pack_side)

            self.Scrollable_frame = ctk.CTkFrame(self.Scrollable_canvas, fg_color=color, bg_color=theme.Cbg)
            self.Scrollable_canvas.create_window(
                (0,0),
                window=self.Scrollable_frame,
                anchor="nw",
                width = self.winfo_width(),
                height = 10000,
                tags= "frame")

            self.content_frame = ctk.CTkFrame(self.Scrollable_frame, fg_color=color,
                                              background_corner_colors=(theme.Cbg, theme.Cbg, (color), (color)))
            self.content_frame.pack(fill="x")

            #^ self.Scrollable_canvas.bind("<FocusIn>", lambda event: print(f"in {self.widget_str.split('!')[-1]}"))
            #^ self.Scrollable_canvas.bind("<FocusOut>", lambda event: print(f"out of {self.widget_str.split('!')[-1]}"))
            if scrollbar_inside:
                self.scroll_bar = Scrollbar(self.Scrollable_canvas, self, color=hvr_clr_g(color, "ld"), side="e",
                                                command=self.Scrollable_canvas.yview)
            else:
                self.scroll_bar = Scrollbar(Chest.Manager.scroll_bar_frame, self, color=color, auto_hide=False, subpage_style=False,
                                                command=self.Scrollable_canvas.yview)
            self.Scrollable_canvas.config(yscrollcommand=self.scroll_bar.set)
        else:
            self.content_frame = ctk.CTkFrame(self, fg_color=color, bg_color=theme.Cbg)
            self.content_frame.pack(fill="both", expand=True)

        self.menu_frame = ctk.CTkFrame(Chest.toolsFrame, fg_color="transparent")

        self._queue = []  # list of (name, task)
        self._busy = False
        self._current = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Chest.Manager.classes_ref["tiles"][cls.__name__.lower()] = cls

    def _update_queue(func):
        def wrapper(self, *args, **kwargs):
            already_queued = any(name == func.__name__ for name, _ in self._queue)
            currently_running = self._current == func.__name__

            if already_queued or currently_running:
                return

            self._queue.append((func.__name__, lambda: func(self, *args, **kwargs)))

            if self._busy:
                return

            self._busy = True
            while self._queue:
                name, task = self._queue.pop(0)
                self._current = name
                task()
            self._busy = False
            self._current = None

        return wrapper

    @_update_queue
    def update_width(self, page_switch=False):
        # print(f"updating width of tile {self.widget_str}. code {self._name} ")
        if self._is_width_fixed and not page_switch:    #? Note: page_switch is always True on first `show_page` call
            return

        if self.scrollable:
            self.update()
            self.Scrollable_canvas.itemconfigure("frame", width=self.winfo_width()) # update frame width
        if self.pickable:
            self.Updating() # update widgets and user defined functions

        #? temp disabled. to be checked later if we are gonna implement it. see below (_chain_update method)
        # if Tile_BM.get_tile(self._current_page._current_tile[self._in_container]) == self and self.pickable:
        #     threading.Thread(target=self._chain_thread_creator, daemon=True).start()

    @_update_queue
    def update_height(self, event):    #todo: a delay timer needs to be added here, so that if more than one item is being added the function isn't triggered untill all the items are added
        """due to vertical placement changes to the content of the frame"""
        #? get the height of the contents in the frame
        self.update()
        self.max_height = self.content_frame.winfo_height()
        self.Scrollable_canvas.configure(scrollregion = (0, 0, self.winfo_width(), self.max_height))    # update scroll region

    def get_pf(self):
        return self.content_frame

    def Starting(self): # this function is called only once when the page is opened for the first time
        # self.update_width()
        if self.scrollable:
            self.update_height(event=None)
            self.content_frame.bind("<Configure>", lambda event: self.update_height(event))     #^ after this point the updae_height func shouldn't be called manually
        self.pickable = True

        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        for func in self.starting_call_list:
            func()
        self.start_func()

    def Picking(self):
        # print("Picking called for", self._name)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        for func in self.picking_call_list:
            func()

        self.pick_func()

    def Updating(self):
        self.update()
        for func in self.updating_call_list:
            func()

        self.update_func()

    def Leaving(self) -> bool:
        for func in self.leaving_call_list:
            func()

    def add_menu_button(self, icon_path, command, size = (40, 40), pady = 3):
        button_image = change_pixel_color(icon_path, colors=theme.icon_norm)
        button_image = ctk.CTkImage(*button_image, size=size)
        button = ctk.CTkButton(self.menu_frame, text="", fg_color="transparent", hover_color=Chest.Manager.menu_frame._fg_color, image=button_image,
                      command=command, )
        button.pack(pady=pady)
        return button

    def get_scrframe_color(self):
        color = self.content_frame._fg_color
        if color == "transparent":
            return Chest.Manager._fg_color
        else:
            return color


    #^ Show Page
    def _process_pack_req(self, container:ctk.CTkFrame):
        # self.opened = True
        page_change = container.master != self._current_page
        if page_change:
            self._on_page_switch(container)
        self._current_page._current_tile[self._in_container] = self._name
        self.pack(in_=self._in_container, side=self.container_pack_side, expand=True, fill="both")
        if page_change:
            self.opened = True
            self.update_width(page_change)

    def _on_page_switch(self, container:ctk.CTkFrame):
        if self._current_page is not None:
            if self._current_page._current_tile[self._in_container] == self._name:
                self._current_page._disconnected_tiles.append(self._name)
            if self._source_tile[self._current_page] is not None:
                Tile_BM.get_tile(self._source_tile[self._current_page])._linked_tiles.remove(self._name)

        self._current_page = container.master
        self._in_container = container
        self._is_width_fixed = container.fixed_width

        if self._current_page not in self._source_tile:
            new_source = Tile_BM.get_tile(self._current_page._current_tile[container])
            new_source = new_source._name if new_source != self else None
            self._source_tile[self._current_page] = new_source
        if self._source_tile[self._current_page] is not None and self._name not in Tile_BM.get_tile(self._source_tile[self._current_page])._linked_tiles:
            Tile_BM.get_tile(self._source_tile[self._current_page])._linked_tiles.append(self._name)

        # self._current_page._current_tile[self._in_container] = self._name
        self.tile_func(self._current_page)

    def _on_show_callbacks(self):
        self.opened = True
        if self.pickable:
            self.Picking()
        else:               # means that the page hasn't started yet
            self.Starting()

    def show_page(self, container:ctk.CTkFrame):
        self._process_pack_req(container)
        self._on_show_callbacks()


    #^ Hide Page
    def _on_leave_check(self, event):
        return self.leave_func(event)

    def _process_unpack_req(self) -> bool: #? perform a _on_leave_check before calling it
        self.Leaving()
        self.opened = False
        self.menu_frame.place_forget()

    def hide_page(self, event) -> bool:
        state = self._on_leave_check(event)
        if state:
            self._process_unpack_req()
            self.pack_forget()
        return state


    def destroy_page(self):
        #TODO:
        # for func in self.destroying_call_list:
        #    func()

        if self.scrollable and not self.scrollbar_inside:
            self.scroll_bar.destroy()
        self.destroy()
        self.menu_frame.destroy()

    def _bg_update(self):
        openable = self.openable
        self.openable = False
        # self.pack(in_=self._in_container, side=self.container_pack_side, expand=True, fill="both")
        self.update_width()
        # self.pack_forget()
        self.openable = openable

    def open_subpage(self, subpage:Union["Tile_BM", str]):
        if isinstance(subpage, str):
            if subpage.lower() not in Chest.Manager.tiles:
                Chest.Manager.tiles[subpage.lower()] = Chest.Manager.classes_ref["tiles"][subpage.lower()]()
            subpage = Tile_BM.get_tile(subpage)
        if isinstance(subpage, Tile_BM) and (subpage._name not in Chest.Manager.tiles):
            Chest.Manager.tiles[subpage._name] = subpage

        if subpage.openable and self.hide_page("subpage.enter"):
            current_width = subpage.winfo_width()
            if (not self._in_container.fixed_width) and current_width != 1 and current_width != self._in_container.winfo_width():
                subpage.place(in_=self._in_container, relx=0, rely=1, relwidth=1, relheight=1)
                subpage.update_width()
            subpage.show_page(self._in_container)

    def return_to_source(self):
        source = Tile_BM.get_tile(self._source_tile[self._current_page])
        if source is not None and self.hide_page("subpage.leave"):
            current_width = source.winfo_width()
            if (not self._in_container.fixed_width) and current_width != 1 and current_width != self._in_container.winfo_width():
                source.place(in_=self._in_container, relx=0, rely=1, relwidth=1, relheight=1)
                source.update_width()
            source.show_page(self._in_container)
            return

    def reload(self, *args, **kwargs):
        class_name = self.__class__.__name__.lower()
        Chest.Manager.classes_ref["tiles"][class_name] = Chest.Manager.ext_pages_importer(self, reload=True)
        Chest.Manager.tiles[self._name] = Chest.Manager.classes_ref["tiles"][class_name](*args, **kwargs)

        new_instance:"Tile_BM" = Tile_BM.get_tile(self._name)
        new_instance._name = self._name
        new_instance._source_tile  = self._source_tile  #? both `_current_page` and `_in_container` will be set by `on_page_switch`

        is_opened = self.opened
        self.destroy_page()
        if is_opened:
            new_instance.show_page(self._in_container)

    @staticmethod
    def get_tile(name: str) -> "Tile_BM":
        return Chest.Manager.tiles[name.lower()]

    #todo(NOT USED): check if we are gonna have background updates for linked tiles (probably not)
    def _chain_thread_creator(self):
        for tile_name in {*self._linked_tiles, *({self._source_tile[self._current_page]} if self._source_tile[self._current_page] is not None else ())}: #- {Chest.Manager.tiles[self._current_page._current_tile[self._in_container]]}:
            tile = Tile_BM.get_tile(tile_name)
            if tile.pickable:
                tile._chain_update()

    def _chain_update(self):
        openable = self.openable
        self.openable = False

        self.place(relx=0, rely=1, relwidth=1)
        # for tile in {*self._tiles} - {*self._disconnected_tiles}:
            # tile._bg_update()
        self.update_width()
        self.place_forget()

        self.openable = openable
