from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .TilingWindowManager import TilingWindowManager

import tkinter as tk
import customtkinter as ctk
from typing import Union, Tuple, Callable
import threading, time

from .Core  import userChest as Chest
from .Theme import theme, change_pixel_color
from .utils import hvr_clr_g
from .Minimal_scrollbar import Scrollbar

class Page_BM(ctk.CTkFrame): #the final frame to use is the "self.content_frame"
    def __init__(self, 
                 color:       Tuple[str, str] = hvr_clr_g(theme.Cbg, "ld"), 
                 scrollable:  bool = True, 
                 start_func:  Callable[[None], None] = lambda: None, 
                 pick_func:   Callable[[None], None] = lambda: None, 
                 tile_func:   Callable[[None], None] = lambda: None,
                 update_func: Callable[[None], None] = lambda: None, 
                 leave_func:  Callable[[str], bool] = lambda event: True,
              #* destroy_func:Callable[[None], None] = lambda: None,
                 scrollbar_inside: bool = False,
                 container_pack_side: str = "left",
                 page_pack_side: str = "left",
                 ):
        self.parent = Chest.PageParent
        self.color = color
        self._in_container : ctk.CTkFrame = None
        super().__init__(self.parent, fg_color="transparent")

        self.widget_str = str(self)
        self.scrollable = scrollable
        self.openable = True            #? can the page be opened now or not
        self.opened = False             #? is Page currently opened or not
        self.pickable = False           #? has the page started at least once or not
        
        self.container_pack_side: str = container_pack_side
        self._use_fixed_width: bool = False
        self.scrollbar_inside:bool = scrollbar_inside
        self._managed_by_tile:bool = False
        self.tiling_manager:"TilingWindowManager" = None

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
    def update_width(self): # it updates the whole page (Width & height) + checks the scrollbar status
        #todo: replace this check with something better to allow switching between fixed and non fixed width without any issues (ex. if the page starts as a page then switches to a tile it won't update its width because the pickable is already true)
        if self._managed_by_tile and self._use_fixed_width and self.pickable:  # skip width updates if page width is fixed and the page has already started (initial width is set)
            return
        
        if self.scrollable:
            self.update()
            self.Scrollable_canvas.itemconfigure("frame", width=self.winfo_width()) # update frame width
        if self.pickable and not self._managed_by_tile:     #? if managed by a tile manager. don't update yourself, tile manager will call your updating method for you
            self.Updating() # update widgets and user defined functions 
                
    @_update_queue
    def update_height(self, event):    #! a delay timer needs to be added here, so that if more than one item is being added the function isn't triggered untill all the items are added
        """due to vertical placement changes to the content of the frame"""
        if self.scrollable:
            #? get the height of the contents in the frame
            self.update()
            self.max_height = self.content_frame.winfo_height()
            self.Scrollable_canvas.configure(scrollregion = (0, 0, self.winfo_width(), self.max_height))    # update scroll region

    def get_pf(self):
        return self.content_frame

    def Starting(self): # this function is called only once when the page is opened for the first time
        self.update_width()
        if self.scrollable:
            self.update_height(event=None)
            self.content_frame.bind("<Configure>", lambda event: self.update_height(event))     #^ after this point the updae_height func shouldn't be called manually
        self.updating_call_list.append(lambda page=self: threading.Thread(target=self._bg_thread_creator if page.opened and not page._managed_by_tile else None, daemon=True).start())
        self.pickable = True
    
        if not self._managed_by_tile:
            self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        for func in self.starting_call_list:
            func()
        self.start_func()

    def Picking(self): 
        if not self._managed_by_tile:
            self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        for func in self.picking_call_list:
            func()

        self.pick_func()

    def Tiling(self, state: bool):
        self._managed_by_tile = state
        if state:
            self.tiling_manager.starting_call_list.append(self.Starting)
            self.tiling_manager.picking_call_list.append(self.Picking)
            self.tiling_manager.updating_call_list.append(self.Updating)
        else:
            self.tiling_manager.starting_call_list.remove(self.Starting)
            self.tiling_manager.picking_call_list.remove(self.Picking)
            self.tiling_manager.updating_call_list.remove(self.Updating)
        self.tile_func()

    def Updating(self):
        self.update()
        for func in self.updating_call_list:
            func()

        self.update_func()

    def Leaving(self, event) -> bool:
        for func in self.leaving_call_list:
            func()

        state = self.leave_func(event)
        return state
           
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
        
    def show_page(self, tiled:bool=False):
        self.opened = True
        if self.tiling_manager and self._managed_by_tile != tiled:
            self.Tiling(tiled)
        self.pack(in_=self._in_container if self._managed_by_tile else self.parent, side=self.container_pack_side, expand=True, fill="both")
        if not self._managed_by_tile:
            if self.pickable:
                self.Picking()
            else:               # means that the page hasn't started yet
                self.Starting()

    def hide_page(self, event) -> bool:
        if not self._managed_by_tile:
            state = self.Leaving(event)
        if self._managed_by_tile or state:
            self.opened = False
            self.pack_forget()
            if not self._managed_by_tile:
                self.menu_frame.place_forget()
        return state if not self._managed_by_tile else True

    def destroy_page(self):
        #TODO: 
        # for func in self.destroying_call_list:
        #    func()

        if self.scrollable and not self.scrollbar_inside:
            self.scroll_bar.destroy()
        self.destroy()
        self.menu_frame.destroy()

    def _bg_thread_creator(self):
        for page in {*Chest.MainPages.values(), *Chest.SubPages.values()} - {self}:     #todo: (only in TWM) subtract self.pages with self (if they exist as a main or sub page)
            if page.pickable:                                                           #todo: (Global) add a `and not self._managed_by_tile` check, so that if it is managed by a tile manager don't update it from its own thread, since the tile manager will call its updating method for it.
                threading.Thread(target=page._bg_update, daemon=True).start()

    def _bg_update(self):
        openable = self.openable
        self.openable = False
        self.place(relx=0, rely=1, relwidth=1) if not self._managed_by_tile else self.pack(in_=self._in_container, side=self.container_pack_side, expand=True, fill="both")
        self.update_width()
        self.place_forget() if not self._managed_by_tile else self.pack_forget()
        self.openable = openable
