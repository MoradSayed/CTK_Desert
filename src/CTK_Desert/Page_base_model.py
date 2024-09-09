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
                 update_func: Callable[[None], None] = lambda: None, 
                 leave_func:  Callable[[str], bool] = lambda event: True
                 ):
        self.parent = Chest.PageParent
        super().__init__(self.parent, fg_color="transparent")

        self.widget_str = str(self)
        self.scrollable = scrollable
        self.openable = True
        self.opened = False
        self.pickable = False

        self.starting_call_list = []
        self.picking_call_list = []
        self.updating_call_list = []
        self.leaving_call_list = []
        self.start_func = start_func
        self.pick_func = pick_func
        self.update_func = update_func
        self.leave_func = leave_func

        if self.scrollable:
            self.scrolled = 0
            self.Scrollable_canvas = tk.Canvas(self, background=color[0] if ctk.get_appearance_mode() == "Light" else color[1], 
                                               scrollregion = (0, 0, self.winfo_width(), 10000), yscrollincrement=4, 
                                               bd=0, highlightthickness=0, relief = 'ridge')
            self.Scrollable_canvas.pack(fill="both", expand=True)
            
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

            self.scroll_bar = ctk.CTkScrollbar(Chest.Manager.scroll_bar_frame, orientation="vertical", 
                                               command=self.Scrollable_canvas.yview, button_color=color, button_hover_color=hvr_clr_g(color, "ld"))
            self.Scrollable_canvas.config(yscrollcommand=self.scroll_bar.set)
        else:
            self.content_frame = ctk.CTkFrame(self, fg_color=color, bg_color=theme.Cbg)
            self.content_frame.pack(fill="both", expand=True)

        self.menu_frame = ctk.CTkFrame(Chest.toolsFrame, fg_color="transparent")
        self.updating_call_list.append(lambda page=self: threading.Thread(target=self._bg_thread_creator if page.opened else None, daemon=True).start())

    def update_width(self): # it updates the whole page (Width & height) + checks the scrollbar status
        if self.scrollable:
            self.update()
            self.Scrollable_canvas.itemconfigure("frame", width=self.winfo_width()) # update frame width
        if self.pickable:
            self.Updating() # update widgets and user defined functions 
                
    def update_height(self, event):    #! a delay timer needs to be added here, so that if more than one item is being added the function isn't triggered untill all the items are added
        if self.scrollable:
            #? get the height of the contents in the frame
            self.update()
            self.max_height = self.content_frame.winfo_height()
            self.Scrollable_canvas.configure(scrollregion = (0, 0, self.winfo_width(), self.max_height))    # update scroll region
            self.check_scroll_length()

    def check_scroll_length(self):
        if self.scrollable and self.opened:
            self.update()
            if self.max_height > self.winfo_height():
                self.Scrollable_canvas.bind_all("<MouseWheel>", lambda event: self.scrolling_action(event)) 
                self.scroll_bar.pack(fill="y", expand=True)
            else:
                self.Scrollable_canvas.unbind_all("<MouseWheel>")
                self.scroll_bar.pack_forget()

    def scrolling_action(self, event):
        if str(event.widget).startswith(self.widget_str):
            if self.scrolled == 28:
                self.scrolled = 0
                return 1
            else:
                self.scrolled += 1
                self.Scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                self.update()
                self.after(1, self.scrolling_action, event)

    def get_pf(self):
        return self.content_frame

    def Starting(self): # this function is called only once when the page is opened for the first time
        self.update_width()
        if self.scrollable:
            self.update_height(event=None)
            self.content_frame.bind("<Configure>", lambda event: self.update_height(event))     #^ after this point the updae_height func shouldn't be called manually
        self.pickable = True
    
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        for func in self.starting_call_list:
            func()
        self.start_func()

    def Picking(self): 
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.scrollable: 
            self.check_scroll_length() # called it if the height has changed or not. because, it isn't packed anyway so i need to do the check.

        for func in self.picking_call_list:
            func()

        self.pick_func()

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
           
    def add_menu_button(self, icon_path, command, size = (40, 40)):
        button_image = change_pixel_color(icon_path, colors=theme.icon_norm, return_img=True)
        button_image = ctk.CTkImage(*button_image, size=size)
        ctk.CTkButton(self.menu_frame, text="", fg_color="transparent", hover_color=Chest.Manager.menu_frame._fg_color, image=button_image, 
                      command=command, ).pack()

    def get_scrframe_color(self):
        color = self.Scrollable_frame._fg_color
        if color == "transparent":
            return Chest.Manager._fg_color
        else:
            return color
        
    def show_page(self):
        self.opened = True
        self.pack(expand=True, fill="both")
        if self.pickable:
            self.Picking()
        else:               # means that the page hasn't started yet
            self.Starting()

    def hide_page(self, event) -> bool:
        state = self.Leaving(event)
        if state:
            self.opened = False
            self.pack_forget()
            self.menu_frame.place_forget()
            if self.scrollable:
                self.Scrollable_canvas.unbind_all("<MouseWheel>")
                self.scroll_bar.pack_forget()
        return state

    def destroy_page(self):
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
        self.place(relx=0, rely=1, relwidth=1)
        self.update_width()
        self.place_forget()
        self.openable = openable
        