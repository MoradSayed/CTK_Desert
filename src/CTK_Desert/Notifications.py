import customtkinter as ctk
from tkinter import Label
from typing import Literal, Callable
import os, copy, inspect
from .Theme import theme
from .Core import userChest as Chest
from .utils import change_pixel_color, hvr_clr_g
from PIL import ImageTk

class Notifications:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Notifications, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, side:Literal["w", "e"]="e", padding:int = 10, window:ctk.CTk = Chest.Window):
        
        self._configure(side, padding, window)
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.msgs: list[ctkDmessage] = []
                
        self.levels = {
            "x" : ["icons8-danger-48.png" , theme.Cdanger , None], # Critical, alert, form error, emergency, urgent
            "!" : ["icons8-warning-48.png", theme.Cwarning, None], # Serious, error, warning, needs attention      
            "k" : ["icons8-success-48.png", theme.Csuccess, None], # Normal, on, ok, fine, go, satisfactory        
            "0" : ["icons8-pending-48.png", theme.Cpending, None], # Standby, available, enabled                   
            "i" : ["icons8-info-48.png"   , theme.Cinfo   , None], # Off, unavailable, disabled                    
        }

        Chest.Manager.global_updates_list.append(lambda: self.update_pos(0))
        Chest.On_Theme_Change(self._on_theme_change_job)
        self._initialized = True

    def _configure(self, side:Literal["w", "e"]="e", padding:int = 10, window:ctk.CTk = Chest.Window):
        self.side = side
        self.window = window        
        self.padding = padding
        self.w = self.window.winfo_width()/Chest.scaleFactor if self.side == "e" else 0

    def create_message(self, title:str = None, message:str = "", level:Literal["x", "!", "k", "0", "i"]="i", command:Callable=lambda:None):
        if level not in self.levels:
            raise ValueError(f"Level must be one of {list(self.levels.keys())}")
        
        if self.levels[level][2] == None:
            icons = change_pixel_color(os.path.join(Chest.Manager.original_icons_dir, self.levels[level][0]), theme.Ctxt)   # returns two icons (light and dark)
            size = int(25*Chest.scaleFactor)
            self.levels[level][2] = (ImageTk.PhotoImage(icons[0].resize((size,size))), ImageTk.PhotoImage(icons[1].resize((size,size))))
        
        frame = ctkDmessage(self.window, title, message, self.levels[level][1], self.levels[level][2], command)

        self.msgs.append(frame)
        self.place_msg(frame)
        return frame

    def place_msg(self, msg_frame:"ctkDmessage"):
        h = self.msgs[self.msgs.index(msg_frame)-1].winfo_y()/Chest.scaleFactor  if len(self.msgs)>1   else self.window.winfo_height()/Chest.scaleFactor
        msg_frame.place(x=abs(self.w-self.padding), y=h-self.padding, anchor=f"s{self.side}")
        msg_frame.update()

    def update_pos(self, index:int):
        if self.side == "e":
            self.w = self.window.winfo_width()/Chest.scaleFactor
        while index < len(self.msgs):
            h = self.msgs[index-1].winfo_y()/Chest.scaleFactor if index!=0 else self.window.winfo_height()/Chest.scaleFactor
            self.msgs[index].place(x=abs(self.w-self.padding), y=h-self.padding, anchor=f"s{self.side}")
            self.msgs[index].update()
            index += 1

    def del_msg(self, msg_frame:ctk.CTkFrame):
        i = self.msgs.index(msg_frame)
        self.msgs.remove(msg_frame)
        msg_frame.destroy()
        self.update_pos(i)

    def _on_theme_change_job(self, is_dark:bool):
        for msg in self.msgs:
            msg._canvas_index = is_dark
            msg._icon_canvas.itemconfig(msg._created_icon_id, image=msg._iconKeeper[is_dark])
            msg._icon_canvas.configure(bg=msg.msg_color[is_dark])


class ctkDmessage(ctk.CTkFrame):
    def __init__(self, parent:ctk.CTkFrame, title:str = None, message:str = "", color:tuple[str,str]=theme.Csec, icon:tuple[ImageTk.PhotoImage,ImageTk.PhotoImage]=None, command:Callable=lambda:None):
        super().__init__(parent, fg_color=color, bg_color=color, corner_radius=0)
        self._notif_mngr = Notifications()        
        self.command = command
        self._msg_width = parent.winfo_screenwidth()*Chest.scaleFactor * 0.15

        self.msg_color = color
        self._canvas_index = 0 if ctk.get_appearance_mode() == "Light" else 1 
        self.hvr_color = hvr_clr_g(self.msg_color,"ld")

        self.grid_rowconfigure(0, uniform="icon")
        self.grid_rowconfigure(1, uniform="text")
        self.grid_columnconfigure(0, uniform="icon")
        self.grid_columnconfigure(1, uniform="text")
        self.grid_columnconfigure(2, uniform="cls")

        """(hover_color=hvr_clr_g(color,"ld"), text_color=theme.Ctxt, font=(theme.font, 15), text=message, image=icon, command=self._msg_cmd)"""
        self._iconKeeper = icon
        self._icon_canvas = ctk.CTkCanvas(self, bd=0, highlightthickness=0, relief='ridge', width=25*Chest.scaleFactor, height=25*Chest.scaleFactor, bg=color[self._canvas_index])
        self._created_icon_id = self._icon_canvas.create_image(0, 0, anchor="nw", image=icon[self._canvas_index])
        self._icon_canvas.grid(row=0, column=0, sticky="e", padx=(10,5), pady=(10,0))

        self._msg_title = ctk.CTkLabel(self, fg_color="transparent", bg_color=color, text_color=theme.Ctxt, font=(theme.font_B, 17), text=title, 
                                       anchor="w", compound="left", justify="left", 
                                       width=self._msg_width, wraplength = self._msg_width)     #? Use `width` & `wraplength` to ensure fixed width for all messages while keeping the height dynamic based on the content 
                                        #? (width controls min width, while wraplength controls max width by wrapping the text)
        self._msg_title.grid(row=0, column=1, sticky="we", padx=(5,0), pady=(10,0))     # padx=(5,10)

        self._msg_content = ctk.CTkLabel(self, fg_color="transparent", bg_color=color, text_color=theme.Ctxt, font=(theme.font, 15), text=message, 
                                        anchor="w", compound="left", justify="left", 
                                        width=self._msg_width, wraplength = self._msg_width)   #? Use width+wraplength to ensure fixed width for all messages while keeping the height dynamic based on the content 
                                        #? (width controls min width, while wraplength controls max width by wrapping the text)
        self._msg_content.grid(row=1, column=1, sticky="we", padx=(5,0), pady=(0,10))     # padx=(5,10)

        self._power_widget()

        self._cls_msg = ctk.CTkButton(self, fg_color="transparent", hover_color=hvr_clr_g(color,"ld"), width=1, corner_radius = 0, text=" x ", text_color=theme.Ctxt, font=(theme.font, 15), command=lambda :self._notif_mngr.del_msg(self))
        self._cls_msg.grid(row=0, column=2, rowspan=2, sticky="nsew", ipadx=10, ipady=10, padx=(10,0))

    def _power_widget(self):
        for widget in [self, *self.winfo_children()]:
            widget.bind("<Enter>"   , self._in_action)
            widget.bind("<Leave>"   , self._out_action)
            widget.bind("<Button-1>", self._clicked)

    def _in_action(self, event=None):
        self.configure(fg_color=self.hvr_color)
        self._msg_title.configure(fg_color=self.hvr_color)
        self._msg_content.configure(fg_color=self.hvr_color)
        self._icon_canvas.configure(bg=self.hvr_color[self._canvas_index])

    def _out_action(self, event=None):
        self.configure(fg_color=self.msg_color)
        self._msg_title.configure(fg_color=self.msg_color)
        self._msg_content.configure(fg_color=self.msg_color)
        self._icon_canvas.configure(bg=self.msg_color[self._canvas_index])

    def _clicked(self, event=None):
        #TODO: include some animations later on (if necessary)
        self._notif_mngr.del_msg(self)
        self.command()
    
    def edit(self, title:str=None, message:str=None):
        if self.winfo_exists():
            if title != None:
                self._msg_title.configure(text=title)
            if message != None:
                self._msg_content.configure(text=message)
            return True
        else:
            return False
