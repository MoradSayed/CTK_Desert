import customtkinter as ctk
import os, subprocess, pprint

from .Page_base_model import Page_BM
from .Core import userChest as Chest
from .Theme import theme
from .Widgits import C_Widgits, large_tabs, small_tabs
from .utils import color_finder, hvr_clr_g
from .GridLayout import GridLayoutEditor
from .Notifications import Notifications

class TilingWindowManager(Page_BM): #* Note: this whole widget is made with it being in mind that the widget itself will never be scrollable (only its tiled pages can)
    def __init__(self, pages_list: list[Page_BM], grid: tuple[int, int] = (2, 8), gap: int = 5, **kwargs):
        super().__init__(color=hvr_clr_g(theme.Cbg, "ld"), scrollable=False, leave_func=self._on_leave, **kwargs)
        self.frame = self.get_pf()
        self.notify = Notifications()
        for page in pages_list:
            if not isinstance(page, Page_BM):
                raise ValueError("All items in pages_list must be instances of Page_BM")    #* or use UI to tell the user about the error instead of raising it
        self.nominated_pages: list[Page_BM] = pages_list
        self.pages: list[Page_BM] = []
        self.grid_sys = GridLayoutEditor(self.frame, *grid, gap/Chest.scaleFactor)

    #? Load existing tile set #################################################################################

    def load_tiles(self, layout_state):
        self.frame.configure(fg_color=theme.Cbg)
        tiles_dict = self.grid_sys.load_layout(layout_state)
        self._configure_pages(tiles_dict)
        if self.pickable: #? if tile manager page already started, manually display the pages + their starting methods
            self._display_pages()

    #? Create new tile set #################################################################################

    def create_grid(self):
        self.current_stage = 0
        self.next_btn = self.add_menu_button(
            os.path.join(Chest.Manager.original_icons_dir, "icons8-right-arrow-64.png"),
            self._next_cmd_menubutton, size=(30,30))
        self.grid_sys.start_grid()

    def _next_cmd_menubutton(self):
        if self.current_stage == 0:
            self.frame.configure(fg_color=theme.Cbg)
            names = []
            for page in self.nominated_pages:
                names.append(page.widget_str.split("!")[-1])
                # page.add_menu_button = self.add_menu_button   #todo: find a better idea to allow functionality with both cases (tiled and non tiled)
            self.grid_sys.tiles_assignment_UI(names)

        elif self.current_stage == 1:
            tiles_dict = self.grid_sys.confirm_layout()
            self._configure_pages(tiles_dict)
            self._display_pages()
            self.next_btn.pack_forget()
            
            #?send a notfication of the saved item
            layout_data = pprint.pformat(self.grid_sys.save_layout(), indent=4, sort_dicts=False)
            self.notify.create_message("Layout Created", "click to copy layout data to clipboard", "k",
                                       lambda: subprocess.run("clip", input=layout_data, text=True))
        
        self.current_stage += 1

    #? common methods #################################################################################

    def _configure_pages(self, tiles_dict):
        for page in self.nominated_pages:
            tile = tiles_dict.get(page.widget_str.split("!")[-1])
            if tile is None: #? in case there are empty tiles (without assigned pages)
                continue
            page.tiling_manager = self
            page._in_container = tile
            page._use_fixed_width = not tile.tile_expandable
            self.pages.append(page) #? only adds pages that has an assigned tile
            page.lift()

    def _display_pages(self):
        """Single use method to display the pages after configuring them. so that if the tiling manager has already started pages don't miss their Starting call"""
        for page in self.pages:
            page.show_page(tiled=True)
        for page in self.pages:  #? call the starting method after showing all the pages to prevent any width issues due to excessive availability of free space (from pages that didn't load yet)
            page.Starting()
            #// page.lift() #? to prevent any hiding issues (don't know the cause)

    #^ Tiling Manager methods #############################################################################

    def _on_leave(self, event):
        n, keys = 0, 0
        for n, page in enumerate(self.pages, 1):
            keys += bool(page.Leaving(event))
        return n==keys
    
    def update_width(self):
        if self.pickable: #? avoids redundant updates if the page is currently starting (page's initial width gets set in the Starting method)
            for page in self.pages:
                page.update_width()
        super().update_width()

    def show_page(self):
        for page in self.pages:
            page.show_page(tiled=True)
        super().show_page()

    def hide_page(self, event):
        state = super().hide_page(event)
        if state:
            for page in self.pages:
                page.hide_page(event)
        return state
    
    def destroy_page(self):
        for page in self.pages:
            page.hide_page(None)
        super().destroy_page()

    def _bg_update(self):
        openable = self.openable
        self.openable = False
        self.place(relx=0, rely=1, relwidth=1)
        #// self.update_width()
        for page in self.pages:
            page._bg_update()
        self.place_forget()
        self.openable = openable

#^ Only For a Tiling Window Manager Case (or non scrollable Page_BM in general, propaply!!)
#*  update_width: just calls `self.Updating`
#// Update_height: None
#* check_scroll_length: calls each page's check_scroll_length method
#// scrolling_action: None
#* Starting: just add the tiled_pages Starting method to the starting_call_list. Also disable their menu_frame buttons
#* Picking: just add the tiled_pages Picking method to the picking_call_list.
#* Updating: just add the tiled_pages Updating method to the updating_call_list.
#* Leaving: it checks if all the pages returned True for the leave_func
#* show_page: disable any pages Starting or Picking from being called from the pages themselves. Also, monkey patch it to make tile's show_page call pages' show_page.
#* hide_page: just like show_page but for hiding. 
#? destroy_page: exclude pages from being destroyed by the tile manager. 
#// _bg_thread_creator: None
#* _bg_update: update all tiles on the same update thread.


