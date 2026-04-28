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

        self._velocity = 0.0
        self._scrolling = False
        self._mouse_bound = False

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

            if scrollbar_inside:
                self.scroll_bar_frame = ctk.CTkFrame(self, fg_color=hvr_clr_g(color, "ld"), background_corner_colors=((color), None, None, (color)), width=20)
                self.scroll_bar_frame.pack_propagate(0)
                self.scroll_bar = ctk.CTkScrollbar(self.scroll_bar_frame, orientation="vertical", command=self.Scrollable_canvas.yview, 
                                                   button_color=theme.Csec, button_hover_color=theme.Cpri, 
                                                   fg_color="transparent")
                self.scroll_bar.pack(fill="y", expand=True, pady=5)
            else: 
                self.scroll_bar = ctk.CTkScrollbar(Chest.Manager.scroll_bar_frame, orientation="vertical", 
                                                command=self.Scrollable_canvas.yview, button_color=color, button_hover_color=hvr_clr_g(color, "ld"))
            self.Scrollable_canvas.config(yscrollcommand=self.scroll_bar.set)
        else:
            self.content_frame = ctk.CTkFrame(self, fg_color=color, bg_color=theme.Cbg)
            self.content_frame.pack(fill="both", expand=True)

        self.menu_frame = ctk.CTkFrame(Chest.toolsFrame, fg_color="transparent")
        
    def update_width(self): # it updates the whole page (Width & height) + checks the scrollbar status
        #todo: replace this check with something better to allow switching between fixed and non fixed width without any issues (ex. if the page starts as a page then switches to a tile it won't update its width because the pickable is already true)
        if self._use_fixed_width and self.pickable:  # skip width updates if page width is fixed and the page has already started (initial width is set)
            return
        
        if self.scrollable:
            self.update()
            if self.scrollbar_inside and self.scroll_bar_frame.winfo_ismapped():
                #* print(f"{self.scroll_bar_frame.winfo_ismapped()=} from {self.widget_str.split('!')[-1]}")
                width = self.winfo_width()-self.scroll_bar_frame.winfo_width()
            else:
                width = self.winfo_width()
            self.Scrollable_canvas.itemconfigure("frame", width=width) # update frame width
        if self.pickable and not self._managed_by_tile:     #? if managed by a tile manager. don't update yourself, tile manager will call your updating method for you
            self.Updating() # update widgets and user defined functions 
                
    """
    scrollbar update:
    -accounted for
    1. on content frame change (due to adding or removing widgets inside / vertically shrinking growing widgets) - using content_frame.bind<configure>
    2. main window height resizing (no width change case) 
    ---
    -unaccounted for
    3. main window height resizing with width change (while having static - non shrinking/growing widgets): will not `check_scroll_bar`
    """
    def update_height(self, event):    #! a delay timer needs to be added here, so that if more than one item is being added the function isn't triggered untill all the items are added
        """due to vertical placement changes to the content of the frame"""
        #* print(f"triggered from {self.widget_str.split('!')[-1]}")
        if self.scrollable:
            #? get the height of the contents in the frame
            self.update()
            self.max_height = self.content_frame.winfo_height()
            self.Scrollable_canvas.configure(scrollregion = (0, 0, self.winfo_width(), self.max_height))    # update scroll region
            self.check_scroll_length()

    def check_scroll_length(self):
        """due to changes in the viewport height (main window resizing) + calls from update_height"""
        if self.scrollable and self.opened:
            self.update()
            if self.max_height > self.winfo_height():
                if not self._mouse_bound:
                    self._mouse_bound = True
                    Chest.Binder.bind("<MouseWheel>", self.scrolling_action)
                    if self.scrollbar_inside:
                        self.content_frame.configure(background_corner_colors=(theme.Cbg, (self.color), (self.color), (self.color)))
                        self.scroll_bar_frame.pack(side="right", fill="y", before=self.Scrollable_canvas)
                        self.update_width()
                    else:
                        self.scroll_bar.pack(fill="y", expand=True, pady=5)
            else:
                Chest.Binder.unbind("<MouseWheel>", self.scrolling_action)
                if self.scrollbar_inside:
                    self.content_frame.configure(background_corner_colors=(theme.Cbg, theme.Cbg, (self.color), (self.color)))
                    self.scroll_bar_frame.pack_forget()
                    self.update_width()
                else:
                    self.scroll_bar.pack_forget()
                self._mouse_bound = False

    def scrolling_action(self, event):
        if str(event.widget).startswith(self.widget_str+"."):
            self._velocity += -1 * (event.delta / 120) * 60     #? (-/+)1 * 60
            self._velocity = max(-200, min(200, self._velocity))
            if not self._scrolling:
                self._scrolling = True
                self._animate()

    def _animate(self):
        if abs(self._velocity) < 0.5:
            self._velocity = 0
            self._scrolling = False
            return
        self.Scrollable_canvas.yview_scroll(int(self._velocity), "units")
        self._velocity *= 0.85
        self.after(16, self._animate)

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

        if self.scrollable: 
            self.check_scroll_length() # called it if the height has changed or not. because, it isn't packed anyway so i need to do the check.

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
            if self.scrollable:
                Chest.Binder.unbind("<MouseWheel>", self.scrolling_action)
                if self.scrollbar_inside:
                    self.scroll_bar_frame.pack_forget()
                else:
                    self.scroll_bar.pack_forget()
                self._mouse_bound = False
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
        for page in {*Chest.MainPages.values(), *Chest.SubPages.values()} - {self}:
            if page.pickable:
                threading.Thread(target=page._bg_update, daemon=True).start()

    def _bg_update(self):
        openable = self.openable
        self.openable = False
        self.place(relx=0, rely=1, relwidth=1) if not self._managed_by_tile else self.pack(in_=self._in_container, side=self.container_pack_side, expand=True, fill="both")
        self.update_width()
        self.place_forget() if not self._managed_by_tile else self.pack_forget()
        self.openable = openable
        