import tkinter as tk
import customtkinter as ctk
from typing import Union, Tuple, Callable

from .Core  import userChest as Chest
from .Theme import *
from .utils import hvr_clr_g


class Page_BM(ctk.CTkFrame): #the final frame to use is the "self.Scrollable_frame"
    def __init__(self, 
                 color:       Tuple[str, str] = (hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), 
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
        self.started = False
        self.pickable = False
        self.last_Known_size = (0, 0)   # the value is set in the Starting method #? holds the dimensions of the page window
        self.content_frame_height = 0   #? holds the height of the content frame

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
            
            self.Scrollable_frame = ctk.CTkFrame(self.Scrollable_canvas, fg_color=color, bg_color=(LIGHT_MODE["background"], DARK_MODE["background"]))
            self.Scrollable_canvas.create_window(
                (0,0), 
                window=self.Scrollable_frame, 
                anchor="nw", 
                width = self.winfo_width(), 
                height = 10000, 
                tags= "frame")
            
            self.content_frame = ctk.CTkFrame(self.Scrollable_frame, fg_color=color, 
                                              background_corner_colors=((LIGHT_MODE["background"], DARK_MODE["background"]), (LIGHT_MODE["background"], DARK_MODE["background"]), (color), (color)))
            self.content_frame.pack(fill="x")

            self.scroll_bar = ctk.CTkScrollbar(Chest.Manager.scroll_bar_frame, orientation="vertical", 
                                               command=self.Scrollable_canvas.yview, button_color=color, button_hover_color=(hvr_clr_g(color[0], "l"), hvr_clr_g(color[1], "d")))
            self.Scrollable_canvas.config(yscrollcommand=self.scroll_bar.set)
        else:
            self.content_frame = ctk.CTkFrame(self, fg_color=color, bg_color=(LIGHT_MODE["background"], DARK_MODE["background"]))
            self.content_frame.pack(fill="both", expand=True)

        self.menu_frame = self.tool_menu()

    def Page_update_manager(self): # it updates the whole page (Width & height) + checks the scrollbar status
        if self.scrollable:
            self.update()
            self.Scrollable_canvas.itemconfigure("frame", width=self.winfo_width()) # update frame width
            if self.pickable:
                self.update()
                self.Updating() # update widgets and user defined functions 
            self.update_height()
                
    def update_height(self, event=None):    #! a delay timer needs to be added here, so that if more than one item is being added the function isn't triggered untill all the items are added
        if event and event.height == self.content_frame_height:
            return 1
        
        #? get the height of the contents in the frame
        self.update()
        self.max_height = self.content_frame.winfo_height()
        self.Scrollable_canvas.configure(scrollregion = (0, 0, self.winfo_width(), self.max_height))    # update scroll region
        
        self.check_scroll_length()
        if event:
            self.content_frame_height = self.max_height

    def check_scroll_length(self):
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
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.content_frame.bind("<Configure>", lambda event: self.update_height(event)) # put up here so that it works with the starting function
        
        for func in self.starting_call_list:
            func()
        self.start_func()
        self.last_Known_size = (self.parent.winfo_width(), self.parent.winfo_height())  # to set the initial known size of the parent window
        self.content_frame_height = self.content_frame.winfo_height()

    def Picking(self): 
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.scrollable: 
            if self.last_Known_size[0] != self.parent.winfo_width():
                self.Page_update_manager()
            else:
                self.check_scroll_length() # called it if the height has changed or not. because, it isn't packed anyway so i need to do the check.
                
            self.last_Known_size = (self.parent.winfo_width(), self.parent.winfo_height())
            self.content_frame_height = self.content_frame.winfo_height()

        for func in self.picking_call_list:
            func()

        self.pick_func()

    def Updating(self):
        for func in self.updating_call_list:
            func()
        
        self.last_Known_size = (self.parent.winfo_width(), self.parent.winfo_height())
        self.content_frame_height = self.content_frame.winfo_height()

        self.update_func()

    def Leaving(self, event):
        for func in self.leaving_call_list:
            func()

        self.last_Known_size = (self.parent.winfo_width(), self.parent.winfo_height())
        self.content_frame_height = self.content_frame.winfo_height()

        state = self.leave_func(event)
        return state 
           
    def tool_menu(self):
        self.tools_f = ctk.CTkFrame(Chest.toolsFrame, fg_color="transparent")
        return self.tools_f

    def add_menu_button(self, icon_path, command, size = (40, 40)):
        button_image = change_pixel_color(icon_path, color=f'{ICONS["_l"]}+{ICONS["_d"]}', return_img=True)
        button_image = ctk.CTkImage(*button_image, size=size)
        ctk.CTkButton(self.tools_f, text="", fg_color="transparent", hover_color=Chest.Manager.menu_frame._fg_color, image=button_image, 
                      command=command, ).pack()

    def get_scrframe_color(self):
        color = self.Scrollable_frame._fg_color
        if color == "transparent":
            return Chest.Manager._fg_color
        else:
            return color
        
    def show_page(self):
        self.pack(expand=True, fill="both")
        if self.pickable == 1:
            self.Picking()
        if self.started == False:
            self.started = True
            self.Page_update_manager()   # used to apply some changes that can't be applied before the frame is displayed
            self.pickable = True
            self.Starting() # this function is called only once when the page is opened for the first time

    def hide_page(self):
        self.pack_forget()
        self.menu_frame.place_forget()
        if self.scrollable:
            self.Scrollable_canvas.unbind_all("<MouseWheel>")
            self.scroll_bar.pack_forget()

    def destroy_page(self):
        self.scroll_bar.destroy()
        self.destroy()
        self.menu_frame.destroy()

