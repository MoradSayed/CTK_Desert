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
        self.key = 0            # doesn't allow the execution of the "Page_update_manager" function untill the page is opened from the "tab frame page" >> self.key = 1
        self.openable = True
        self.started = False
        self.pickable = False
        self.last_Known_size = (0, 0)

        self.starting_call_list = []
        self.picking_call_list = []
        self.updating_call_list = []
        self.leaving_call_list = []
        self.start_func = start_func
        self.pick_func = pick_func
        self.update_func = update_func
        self.leave_func = leave_func

        if self.scrollable:
            self.Scrollable_canvas = tk.Canvas(self, background=color[0] if ctk.get_appearance_mode() == "Light" else color[1], 
                                               scrollregion = (0, 0, self.winfo_width(), 10000), 
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
        else:
            self.Scrollable_frame = ctk.CTkFrame(self, fg_color=color, bg_color=(LIGHT_MODE["background"], DARK_MODE["background"]))
            self.Scrollable_frame.pack(fill="both", expand=True)

        self.menu_frame = self.tool_menu()

    def Page_update_manager(self, k=0, update_with_extend = True): #it updates the height of the page and the scrollable region
        self.key = k if k else self.key
        if self.key: #* this is to prevent the function from running when the page isn't opened yet from the "tab frame page"
            if self.scrollable:
                
                if update_with_extend:
                    self.update()
                    self.Scrollable_canvas.itemconfigure("frame", width=self.winfo_width()) # update frame width
                    if self.pickable:
                        self.update()
                        self.Updating() # update widgets and user defined functions 

                # get the height of the contents in the frame
                self.update()
                self.widget_children = self.Scrollable_frame.winfo_children()
                if self.widget_children != []:
                    self.max_height = self.Scrollable_frame.winfo_children()[-1].winfo_y() + self.Scrollable_frame.winfo_children()[-1].winfo_height()
                else:
                    self.max_height = 1

                self.Scrollable_canvas.configure(scrollregion = (0, 0, self.winfo_width(), self.max_height))    # update scroll region
                
                # Check if the height of the contents is greater than the height of the frame, to determine if the scrolling function should be on or not
                if self.max_height > self.winfo_height():
                    # using bind_all to make the scrolling function work even on the children of the canvas
                    self.Scrollable_canvas.bind_all("<MouseWheel>", lambda event: self.scrolling_action(event)) 
                else:
                    self.Scrollable_canvas.unbind_all("<MouseWheel>")
            
    def scrolling_action(self, event):
        if str(event.widget).startswith(self.widget_str):
            self.Scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def Starting(self): # this function is called only once when the page is opened for the first time
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        for func in self.starting_call_list:
            func()
        self.start_func()

    def Picking(self): 
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.scrollable: 
            if self.last_Known_size[1] != self.parent.winfo_height():
                if self.last_Known_size[0] != self.parent.winfo_width():
                    print("update")
                    self.Page_update_manager()
                else:
                    print("extend")
                    self.Page_update_manager(update_with_extend = False)
            elif self.last_Known_size[0] != self.parent.winfo_width():
                print("update")
                self.Page_update_manager()
            else:
                if self.max_height > self.winfo_height():
                    self.Scrollable_canvas.bind_all("<MouseWheel>", lambda event: self.scrolling_action(event)) 
                else:
                    self.Scrollable_canvas.unbind_all("<MouseWheel>")
                
            self.last_Known_size = (self.parent.winfo_width(), self.parent.winfo_height())

        for func in self.picking_call_list:
            func()

        self.pick_func()

    def Updating(self):
        for func in self.updating_call_list:
            func()
        
        self.last_Known_size = (self.parent.winfo_width(), self.parent.winfo_height())

        self.update_func()

    def Leaving(self, event):
        for func in self.leaving_call_list:
            func()

        self.last_Known_size = (self.parent.winfo_width(), self.parent.winfo_height())

        state = self.leave_func(event)
        if state and self.scrollable:
            self.Scrollable_canvas.unbind_all("<MouseWheel>")
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
            self.Page_update_manager(k=1)   # used to apply some changes that can't be applied before the frame is displayed
            self.pickable = True
            self.Starting() # this function is called only once when the page is opened for the first time

    def hide_page(self):
        self.pack_forget()
        self.menu_frame.place_forget()    #placed inside the file 

    def destroy_page(self):
        self.destroy()
        self.menu_frame.destroy()    #placed inside the file