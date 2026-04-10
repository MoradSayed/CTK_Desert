import customtkinter as ctk
from tkinter import TclError
from PIL import Image, ImageTk
import numpy as np
from math import ceil
from .Core import userChest as Chest
from .Page_base_model import Page_BM
from .Theme import theme
from .utils import hvr_clr_g, change_pixel_color, color_finder
from typing import Union, Tuple, Callable, Optional, Literal, Any, List
from methodtools import lru_cache
from sklearn.cluster import KMeans

class C_Widgits():
    def __init__(self, page_class, parent):
        self.page = page_class
        self.parent = parent
        
    def section(self, 
                title:      str = None, 
                fg_color:   Union[tuple, str] = "transparent", 
                font:       Union[tuple, ctk.CTkFont] = (theme.font_B, 25), 
                text_color: Union[str, Tuple[str, str]] = theme.Ctxt,
                padx: Union[int, Tuple[int, int]] = 30, 
                pady: Union[int, Tuple[int, int]] = (20, 0), 
                inner_padx: Union[int, Tuple[int, int]] = 40,
                inner_pady: Union[int, Tuple[int, int]] = (20, 0)):
        
        section_frame = ctk.CTkFrame(self.parent, fg_color= fg_color)

        if title != None:
            title_frame = ctk.CTkFrame(section_frame, fg_color= "transparent")  # contains the label and the button (if it exists).
            section_label = ctk.CTkLabel(title_frame, text=f"{title}", font=font, fg_color="transparent", text_color=text_color, anchor="w")
            section_label.pack(side="left", fill="x", padx=0)#20)
            title_frame.pack(fill="x")

        ops_frame = ctk.CTkFrame(section_frame, fg_color= "transparent")
        ops_frame.pack(fill="x", padx=inner_padx, pady=inner_pady)

        section_frame.pack(fill="x", padx=padx, pady=pady)

        return ops_frame  
        
    def section_button(self, 
                       section:         ctk.CTkFrame, 
                       button_icon:     Union[str, Image.Image] = None, 
                       button_command:  Callable = None, 
                       icon_height:     int = 30, 
                       button_text:     str = "", 
                       font:            Union[Tuple[str, int], ctk.CTkFont] = (theme.font, 15), 
                       fg_color:        Union[str, Tuple[str, str]] = theme.Caccent, 
                       hover_color:     Union[str, Tuple[str, str]] = hvr_clr_g(theme.Caccent, "ld") ):

            if button_icon != None:
                try:
                    button_icon = change_pixel_color(button_icon, theme.Ctxt)
                except TypeError:
                    raise TypeError("button_icon should be a path to an image or an Image object.")
                w, h = button_icon[0].size
                r = w/h
                s = (int(icon_height*r), int(icon_height))
                button_icon = ctk.CTkImage(*button_icon, size=s)

            section_button = ctk.CTkButton(section.master.winfo_children()[0], text=f"{button_text}", font=font, 
                                           fg_color=fg_color, hover_color=color_finder(section.master) if fg_color == "transparent" else hover_color, 
                                           image=button_icon, width=s[0], height=s[1], 
                                           command=button_command)
            section_button.pack(side="right", fill="x", padx=0)#20)

            return section_button
    
###############################################################################################################################################################################################

    def _sectionUnit(self, section, title : str = ""):
               
        unit_frame = ctk.CTkFrame(section, fg_color= "transparent")

        unit_label = ctk.CTkLabel(unit_frame, text=f"{title}", font=(theme.font, 20))
        unit_label.pack(side="left", fill="x")

        unit_frame.pack(fill="x", pady=(0, 20))
        
        return unit_frame
    
    def Button_unit(self, section, title : str = "",
                    text: str = "Click",
                    command: Callable = lambda: None,
                    invert: bool = False,
                    lone_widget: bool = False,
                    fg_color: Optional[Union[str, Tuple[str, str]]] = theme.Caccent,
                    font: tuple = (theme.font, 15),
                    width: int = 140,
                    height: int = 28,
                    padx: Tuple[int, int] = (0, 0)
                    ):
        
        if not lone_widget:
            master = self._sectionUnit(section, title)
        else:
            master = section

        if invert:
            hover_color = None
            text_color  = fg_color
            border_color= fg_color
            fg_color = "transparent"
            border_width = 2
        else:
            border_width = None
            border_color = None
            text_color  = theme.Ctxt
            hover_color = hvr_clr_g(fg_color, "ld")
            
        unit_option = ctk.CTkButton(master = master, text = text, font = font, text_color = text_color, width = width, height = height, fg_color = fg_color, hover_color = hover_color, border_width = border_width, border_color = border_color, command = command)
        unit_option.pack(side="right", fill="x", padx=padx)

        if invert:  #? Careful that fg_color is now stored in the text_color var, and fg_color is actually "transparent". 
            textclr_onEntry = theme.Ctxt if text_color != theme.Ctxt else theme.Ctxt[::-1]
            unit_option.bind("<Enter>", command=lambda e: unit_option.configure(fg_color=text_color, text_color=textclr_onEntry))
            unit_option.bind("<Leave>", command=lambda e: unit_option.configure(fg_color="transparent", text_color=text_color))

        return unit_option

    def ComboBox_unit(self, section, title : str = "",
                      values: Optional[List[str]] = None,
                      default: str = None, 
                      command: Union[Callable[[str], Any], None] = lambda var: None, 
                      lone_widget: bool = False,
                      variable: Union[ctk.Variable, None] = None, 
                      fg_color: Optional[Union[str, Tuple[str, str]]] = theme.Csec,
                      border_color: Optional[Union[str, Tuple[str, str]]] = theme.Csec,#hvr_clr_g(theme.Csec, "ld"),
                      font: Optional[tuple] = (theme.font, 15),
                      width: int = 140,
                      height: int = 28):

        if not lone_widget:
            master = self._sectionUnit(section, title)
        else:
            master = section

        variable = ctk.StringVar(value=default) if variable is None else variable
        unit_option = ctk.CTkComboBox(master, fg_color = fg_color, border_color=border_color, button_color=border_color, 
                                      font = font, text_color = theme.Ctxt, width = width, height = height, 
                                      dropdown_fg_color=fg_color, dropdown_font=font, dropdown_text_color = theme.Ctxt,  
                                      state = "readonly", values = values, variable = variable, command = command)
        # unit_option.set(f"{default}") if default is not None else None
        unit_option.pack(side="right", fill="x")

        return unit_option, variable
    
    def CheckBox_unit(self, section, title : str = "",
                      default: bool = False, 
                      command: Union[Callable[[], Any], None] = None,
                      lone_widget: bool = False,
                      variable: Union[ctk.Variable, None] = None,

                      fg_color: Optional[Union[str, Tuple[str, str]]] = theme.Caccent,
                      border_color: Optional[Union[str, Tuple[str, str]]] = None,
                      checkmark_color: Optional[Union[str, Tuple[str, str]]] = None,

                      width: int = 82,  #? (typical_unit_width/2)+(checkbox_width/2) >> 140/2 + 24/2
                      height: int = 24,
                      checkbox_width: int = 24,
                      checkbox_height: int = 24,
                      ):
        
        if not lone_widget:
            master = self._sectionUnit(section, title)
        else:
            master = section

        variable = ctk.BooleanVar(value=default) if variable is None else variable
        unit_option = ctk.CTkCheckBox(master, text="", width=width, height=height, checkbox_width=checkbox_width, checkbox_height=checkbox_height,
                                      fg_color=fg_color, hover_color=hvr_clr_g(fg_color, "ld"), 
                                      border_color=border_color, checkmark_color=checkmark_color,
                                      command=command, variable=variable, onvalue=True, offvalue=False,)
        # if default != None:
        #     unit_option.configure(variable=default) 
        unit_option.pack(side="right", fill="x")

        return unit_option, variable
    
    def Entry_unit(self, section, title : str = "",
                   placeholder_text: Union[str, None] = None,
                   lone_widget: bool = False,
                   textvariable: Union[ctk.StringVar, None] = None,

                   fg_color: Optional[Union[str, Tuple[str, str]]] = "transparent",
                   font: Optional[tuple] = (theme.font, 15),
                   width: int = 140,
                   height: int = 28,
                   ):
        
        if not lone_widget:
            master = self._sectionUnit(section, title)
        else:
            master = section

        text_color = theme.Ctxt
        textvariable = ctk.StringVar(value=placeholder_text) if textvariable is None else textvariable
        unit_option = ctk.CTkEntry(master, font=font, fg_color=fg_color, text_color=text_color, width=width, height=height, textvariable=textvariable)
        unit_option.pack(side="right", fill="x")

        if placeholder_text is not None:
            plchldrClr = theme.Cpri
            unit_option.configure(text_color= plchldrClr)
            unit_option.bind("<FocusIn>", lambda e, wdgt = unit_option, clr = text_color, textVar = textvariable: self._entryFin(e, wdgt, clr, textVar, placeholder_text))
            unit_option.bind("<FocusOut>", lambda e, wdgt = unit_option, clr = plchldrClr, textVar = textvariable: self._entryFout(e, wdgt, clr, textVar, placeholder_text))

        return unit_option, textvariable
    
    def _entryFin(self, event, widget, color, textVar, placeHolder):
        content = textVar.get()
        if content == placeHolder or content == "":
            widget.delete(0, "end")
            widget.configure(text_color = color)

    def _entryFout(self, event, widget, color, textVar, placeHolder):
        content = textVar.get()
        if content == placeHolder or content == "":
            widget.insert(0, placeHolder)
            widget.configure(text_color = color)
    
class small_tabs(ctk.CTkFrame):
    def __init__(self, page_class: Page_BM, parent, img_width=300, img_height=180, padx=0, pady=(0, 0)):
        super().__init__(parent, fg_color="transparent")
        self.page = page_class
        self.parent = parent
        self.image_width = img_width
        self.image_height = img_height
        self.canvas_color = self.page.get_scrframe_color()
        self.tabs = [] 
        self.slots = []
        self.images = [] 
        
        self.reorder_btn_state = 0
        self.unit_h = 0
        self.swapping = 0

        self.tab_index = None
        self.event_y_offset = None

        self.whiteLine_pady = 25

        self.started = False

        self.pack(expand=True, fill="x", padx=padx, pady=pady)
        self.page_function_calls()
        
    def tab(self, text, image, button_icon=None, button_command=None, icon_size=(25, 25)):

        tab_cont = ctk.CTkFrame(self, fg_color="transparent", height=self.image_height+self.whiteLine_pady+2)   # 2 for the white line

        st_frame = ctk.CTkFrame(self, fg_color="transparent", height=self.image_height)
        reorder_btn = ctk.CTkLabel(tab_cont, text="⥮", font=("", 30), fg_color="transparent", width=28)   # ⠿

        if isinstance(image, Image.Image):
            im = image
        elif isinstance(image, str):
            im = Image.open(image)
        else:
            raise TypeError("image should be a path to an image or an Image object.")
        
        ratio = im.size[0]/im.size[1]
        if ratio > (self.image_width/self.image_height):
            s = (int(self.image_height*ratio), self.image_height)
        else:
            s = (self.image_width, int(self.image_width/ratio))
        im_ctk = ImageTk.PhotoImage(im.resize(s))
        self.images.append(im_ctk)

        canvas = ctk.CTkCanvas(st_frame, bg=self.canvas_color[0] if ctk.get_appearance_mode() == "Light" else self.canvas_color[1], 
                               bd=0, highlightthickness=0, relief='ridge', width=self.image_width, height=self.image_height)
        canvas.pack(side="left")
        canvas.create_image(self.image_width/2, self.image_height/2, anchor="center", image=im_ctk)

        tab_title = ctk.CTkLabel(st_frame, fg_color="transparent", text=f"{text}", font=(theme.font, 20), anchor="w", justify="left")
        tab_title.pack(padx=20, side="left", fill="x", expand=True)

        if button_icon: #^ make it so that it can be a directory(str), actual_image(Image.Image), custom_image(tuple), or None
            button_image = change_pixel_color(button_icon, colors=theme.icon_norm)
            button_image = ctk.CTkImage(*button_image, size=icon_size)
            ctk.CTkButton(st_frame, text="", fg_color="transparent", hover_color=self.canvas_color, image=button_image, 
                          command=button_command, width=30, height=30).pack(side="right")

        st_frame.pack(in_=tab_cont, expand=True, fill="x")
        tab_cont.pack(expand=True, fill="x")

        White_line = ctk.CTkFrame(tab_cont, fg_color=theme.Cbg[::-1], height=2)
        White_line.pack(fill="x", side="bottom", pady=self.whiteLine_pady)

        tab_title.configure(wraplength = tab_title.winfo_width()/Chest.scaleFactor)
        tab_title.bind('<Configure>', lambda e: tab_title.configure(wraplength = tab_title.winfo_width()/Chest.scaleFactor))

        self.tabs.append(st_frame)
        self.slots.append(tab_cont)
        if self.started:
            self.update()
            tab_cont.configure(height=tab_cont.winfo_height()/Chest.scaleFactor)
            tab_cont.pack_propagate(0)
        if self.reorder_btn_state:
            reorder_btn.pack(before=st_frame, side = "left", padx=(0, 20), pady=(0, self.whiteLine_pady*2), fill="y")
            reorder_btn.bind("<Enter>"   , lambda e, t=st_frame: t.configure(fg_color=theme.Csec))
            reorder_btn.bind("<Leave>"   , lambda e, t=st_frame: t.configure(fg_color="transparent"))
            reorder_btn.bind("<B1-Motion>", lambda e, t=st_frame, b=reorder_btn: self._on_motion(e, t, b))
            reorder_btn.bind("<ButtonRelease-1>", lambda e, Tc=tab_cont, b=reorder_btn: self._on_release(e, Tc, b))
        return tab_cont

    def reorder(self): # for in app swap
        self.reorder_btn_state = not self.reorder_btn_state
        if self.reorder_btn_state:
            self.unit_h = self.slots[0].winfo_height()/Chest.scaleFactor
            for n, slot in enumerate(self.slots):
                button = slot.winfo_children()[0]
                tab = self.tabs[n]
                button.pack(before=tab, side = "left", padx=(0, 20), pady=(0, self.whiteLine_pady*2), fill="y")
                button.bind("<Enter>"   , lambda e, t=tab: t.configure(fg_color=theme.Csec))
                button.bind("<Leave>"   , lambda e, t=tab: t.configure(fg_color="transparent"))
                button.bind("<B1-Motion>", lambda e, t=tab, b=button: self._on_motion(e, t, b))
                button.bind("<ButtonRelease-1>", lambda e, Tc=slot, b=button: self._on_release(e, Tc, b))
        else:
            for slot in self.slots:
                button = slot.winfo_children()[0]
                button.pack_forget()
                button.unbind("<Enter>")
                button.unbind("<Leave>")
                button.unbind("<B1-Motion>")
                button.unbind("<ButtonRelease-1>")

    def _on_motion(self, event, tab, btn):
        if self.swapping == 0:
            scaled_y_event = event.y/Chest.scaleFactor
            if self.tab_index == None:
                btn.configure(text="")
                self.tab_index = self.tabs.index(tab)
                self.event_y_offset = scaled_y_event
                tab.lift()
            y = (self.tab_index*self.unit_h)+(scaled_y_event-self.event_y_offset)
            tab.place(x=0, y=y, relwidth=1, anchor="nw")
            # print(f"event: {scaled_y_event}, y: {y}")

    def _on_release(self, event, Tab, btn):
        if self.tab_index != None:
            self.swapping = 1
            scaled_y_event = event.y/Chest.scaleFactor
            
            up_target = (scaled_y_event+self.whiteLine_pady+2 -self.event_y_offset)/self.unit_h   # up
            if up_target < 0:
                up_target = up_target - 1
            down_target = (scaled_y_event+self.whiteLine_pady+2 +((self.tabs[0].winfo_height()/Chest.scaleFactor)-self.event_y_offset))/self.unit_h   # down
            if down_target < 0:
                down_target = down_target - 1

            if abs(up_target) < abs(down_target):   # can be improved so that it chooses which ever is further in
                target = int(down_target)
            else:
                target = int(up_target)
            
            # print(f"released: {scaled_y_event}, target step: {target}, offset: {self.event_y_offset}")
            self.swap(Tab, target)
            btn.configure(text="⥮")
            self.tab_index = None
            self.event_y_offset = None
            self.swapping = 0

    def swap(self, Tab, step):  # for code swap
        current_pos = self.slots.index(Tab)
        target_pos = current_pos + step
        tabs_count = len(self.slots)
        
        if target_pos >= 0 and target_pos < tabs_count:
            self.tabs.insert(target_pos, self.tabs.pop(current_pos))
            self.slots.insert(target_pos, self.slots.pop(current_pos))

            if target_pos+1 < tabs_count:
                self.slots[target_pos].pack(before=self.slots[target_pos+1], expand=True, fill="x")
            elif target_pos+1 == tabs_count:
                self.slots[target_pos].pack(after=self.slots[target_pos-1], expand=True, fill="x")
            try: self.tabs[target_pos].pack(in_=self.slots[target_pos], after=self.slots[target_pos].winfo_children()[0], expand=True, fill="x")
            except TclError: pass   #? doing this try-except, because i need to evaluate the after argument even if it is gonna through an error. (because if i didn't the reorder button will have an issue on toggling it)

        else:   #? packing to the old position. (used with the manual dragging case - to not leave the tab hanging in the wrong place if outside of the slots range)
            try: self.tabs[current_pos].pack(in_=self.slots[current_pos], after=self.slots[current_pos].winfo_children()[0], expand=True, fill="x")
            except TclError: pass   #? doing this try-except, because i need to evaluate the after argument even if it is gonna through an error. (because if i didn't the reorder button will have an issue on toggling it)

        self.update()   # update so that if the bind is still holding an old value it lets it out, so that it doesn't cause a swap after the <self.swapping> lock has been unlocked

    def _on_start(self):
        for slot in self.slots:
            slot.configure(height=slot.winfo_height()/Chest.scaleFactor)
            slot.pack_propagate(0)
        self.started = True

    def page_function_calls(self):
        self.page.starting_call_list.append(self._on_start)

class large_tabs(ctk.CTkFrame):
    def __init__(self, page_class, parent, img_width=500, img_height=300, padx=0, pady=(0, 0), autofit=True):
        self._started = False
        super().__init__(parent, fg_color="transparent")
        self.page = page_class
        self.parent = parent
        self.image_width = img_width
        self.image_height = img_height
        self.padx = padx
        self.pady = pady
        self.autofit = autofit
        self.canvas_color = self.page.get_scrframe_color()

        self.tabs: list[ctk.CTkFrame] = []
        self.rows: list[ctk.CTkFrame] = []
        self.images = []
        self.row_capacity = 1
        self.hidden = False
        self.pending_update = False

        self.pack(expand=True, fill="x")

        self.page_function_calls()

    def tab(self, text=None, image=None, button_icon=None, icon_size=20, button_command=None):  
        expander = self.constructor(text, image, button_icon, icon_size, button_command)
        if self._started:
            self.row_frame()
            expander.pack(in_ = self.rows[-1], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady)
        self.tabs.append(expander)

        return expander.winfo_children()[0].winfo_children()

    def constructor(self, text=None, image=None, button_icon=None, icon_size=20, button_command=None):
        if isinstance(image, Image.Image):
            im = image
        elif isinstance(image, str):
            im = Image.open(image)
        else:
            raise TypeError("image should be a path to an image or an Image object.")
        w, h = im.size[0],im.size[1]
        r = w/h
        if r > (self.image_width/self.image_height):
            s = (int(self.image_height*r), self.image_height)
        else:
            s = (self.image_width, int(self.image_width/r))
        im_ctk = ImageTk.PhotoImage(im.resize(s))
        self.images.append(im_ctk)

        expander = ctk.CTkFrame(master=self.parent, fg_color="transparent")
        tab_cont = ctk.CTkFrame(expander, fg_color="transparent")
        
        canvas = ctk.CTkCanvas(tab_cont, bg=self.canvas_color[0] if ctk.get_appearance_mode() == "Light" else self.canvas_color[1], bd=0, highlightthickness=0, relief='ridge', width=self.image_width, height=self.image_height)
        canvas.pack()
        canvas.create_image(self.image_width/2, self.image_height/2, anchor="center", image=self.images[-1])

        content = ctk.CTkFrame(tab_cont, fg_color=theme.Csec, width=canvas.winfo_width())
        text = ctk.CTkLabel(content, text=f"{text}", font=(theme.font, 20), fg_color="transparent", text_color=theme.Ctxt)
        text.pack(side="left", padx=10, pady=5)
        if button_icon != None:
            self.butt0n_icon(["_", content], button_icon, icon_size, button_command)
        content.pack(expand=True, fill="x", pady=(10, 20))
        
        tab_cont.pack()
        return expander

    def butt0n_icon(self, parent, button_icon, icon_size: int = 20, button_command : Callable = None, override_color: bool = False):  # parent is a list of two elements, the first is the canvas and the second is the content frame
        if override_color:  #! change this so that if he pass a tuple then automatically override the color, if it is just an image then change the color
            image = Image.open(button_icon)
            image = [image, image]
        else:
            image = change_pixel_color(button_icon, colors=theme.icon_norm)
        w, h = image[0].size # image[0] or image[1] doesn't matter
        r = w/h
        s = (int(icon_size*r), icon_size)
        image = ctk.CTkImage(image[0], image[1], size=s)
        actbtn = ctk.CTkButton(parent[1], text="", image=image, fg_color="transparent", hover_color=theme.Csec, 
                                width=int(icon_size*r), command= button_command)
        actbtn.pack(side="right", padx=5, pady=5)

    def row_frame(self):
        if self._started:
            if len(self.tabs) != 0:
                last_row_count = ((len(self.tabs) -1) % self.row_capacity) + 1     # a trick to change mod output from [i%N = 1,...,N-1,0] to [(i-1%N)+1 = 1,...,N]
            if len(self.rows) == 0 or self.winfo_width() < (self.image_width+(3*self.padx))*(last_row_count+1): # width of a tab * (number of tabs in the last row + the one that i wanna create):
                row = ctk.CTkFrame(self, fg_color="transparent")
                row.pack(fill="x", expand=True)
                self.rows.append(row)
        else:
            for _ in range(ceil(len(self.tabs) / self.row_capacity)):
                row = ctk.CTkFrame(self, fg_color="transparent")
                row.pack(fill="x", expand=True)
                self.rows.append(row)

    def _update_layout(self):
        if self.hidden:
            self.pending_update = True
            return 0
        if not (self.autofit and len(self.rows) > 0):
            return
    
        new_capacity = int(self.winfo_width() / (self.image_width+(3*self.padx)))
        if new_capacity < self.row_capacity:                    #^ shrinked
            for row in range(len(self.rows)):                   #? for each row (top to bottom)
                for n in range(self.row_capacity-1, -1, -1):    #? for each tab in the row (right to left) 
                    rank = n + (row*self.row_capacity)          #? get tab index in the self.tabs list
                    if len(self.tabs)-1 < rank:                 #? if the index is out of range (happens in the last row) then
                        continue                                    #? skip the rest of this current loop iteration and move to the next one
                    tab = self.tabs[rank]                       #? get the tab object
                    r_old = rank // self.row_capacity           #? get the old row index
                    r_new = rank // new_capacity                #? get the new row index
                    if r_old != r_new:                          #? if the row index has changed then (START MOVING TABS DOWNWARDS)
                        while len(self.rows)-1 < r_new:                                         #? while the new row index is out of range (happens when we need to create a new row) then
                            new_frame = ctk.CTkFrame(self, fg_color="transparent")                #? create a new row 
                            new_frame.pack(fill="x", expand=True)                                   #? pack the new row
                            self.rows.append(new_frame)                                             #? add it to the list of rows
                        before_arg = None                                                       #? preset the before_arg to None. incase the new row is empty (doesn't have other tabs)
                        #// if new_capacity != 1 and len(self.rows[r_new].pack_slaves()) != 0:      #? if the new row isn't empty and the new capacity isn't 1
                        if (rank+1)%new_capacity!=0 and len(self.tabs)-1>rank:                  #? if it is NOT the last element in the row then and Not the last tab in the tabs list
                            before_arg = self.tabs[rank+1]                                          #? set the before_arg to the next tab in the list (if exists)
                        tab.pack(in_=self.rows[r_new], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady, before = before_arg)  #? pack it in the new row with the before_arg
                        # print(f"tab {rank}. from row {r_old} to row {r_new}. pack before {rank+1 if before_arg is not None else before_arg}")    #! for debugging
        elif new_capacity > self.row_capacity:
            for rank, tab in enumerate(self.tabs):
                r_old = rank // self.row_capacity
                r_new = rank // new_capacity
                if r_old != r_new:
                # move up
                    print(f"move up -> r_old : {r_old}, r_new : {r_new}")
                    tab.pack(in_=self.rows[r_new], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady)
                    print("done")

            #? method 2 (clear the empty rows) -> Works
            for r in range(len(self.rows)-1, -1, -1):
                # print(f"range: {r}")
                if len(self.rows[r].pack_slaves()) == 0:
                    self.rows[r].destroy()
                    self.rows.pop(r)
                    # print("del")
                else:
                    break
            #?################################

        self.row_capacity = new_capacity
        # print(f"update per row: {self.row_capacity}")   #! for debugging

    def show(self):
        """Display the hidden widget and its tabs
        """
        if self.hidden:
            self.pack(expand=True, fill="x")
            self.update()
            self.hidden = False
            if self.pending_update:
                print("pending updates")
                self.pending_update = False
                self._update_layout()

    def hide(self):
        """Hide the Widget and its tabs
        """
        if self.hidden == False:
            self.hidden = True
            final_height = self.parent.winfo_height() - self.winfo_height()
            self.pack_forget()
            self.parent.configure(height=final_height)

    def _on_start(self):
        self.row_capacity = int(self.winfo_width() / (self.image_width+(3*self.padx)))
        self.row_frame()
        for n, expander in enumerate(self.tabs):
            expander.pack(in_ = self.rows[n//self.row_capacity], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady)
        self._started = True
        print(f"creation per row= {self.row_capacity}")

    def page_function_calls(self):
        self.page.starting_call_list.append(self._on_start)
        self.page.updating_call_list.append(self._update_layout)

class Banner(ctk.CTkFrame):
    def __init__(self, 
                 page: Page_BM, 
                 parent: ctk.CTkFrame, 
                 image: Union[str, Image.Image], 
                 banner_title: str = "", 
                 banner_content: Optional[str] = None, 
                 button_text: str = "Click", 
                 button_command: Callable = lambda: None, 
                 shifter: int = 0.7,  #? shifter is a value between -1 and 1
                 overlay: int = 0.5, #? overlay is a value between 0 and 1
                 font: Union[Tuple[str, int], ctk.CTkFont] = (theme.font_B, 20), 
                 font2: Union[Tuple[str, int], ctk.CTkFont] = (theme.font, 12), 
                 ): 
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both")

        self.page = page
        self.parent_frame = parent
        self.shifter = shifter
        self.content : bool = False
        font = (font[0], int(font[1]*Chest.scaleFactor))
        font2 = (font2[0], int(font2[1]*Chest.scaleFactor))
        
        if isinstance(image, str):
            self.ori_img = Image.open(image)
        elif isinstance(image, Image.Image):
            self.ori_img = image
        else:
            raise TypeError("image should be a path to an image or an Image object.")
        overlay_color, rgb_value, luminance = self.get_dominant_color(self.ori_img)  # 0.25 secs, need to find a way to make it faster
        if luminance > 128:
            fill = theme.Ctxt[0]
            hvr = "l" 
        else: 
            fill = theme.Ctxt[1]
            hvr = "d" 
        
        width, height = self.ori_img.size
        self.ratio = width/height
        self.image_calc_height = int(Chest.Window.winfo_vrootheight()*0.4)
        self.image_calc_width  = int(self.image_calc_height*self.ratio)

        self.ori_img = self.ori_img.convert("RGBA")
        self.im_tk  = self._resize_image(self.image_calc_width, self.image_calc_height)

        img_array = np.zeros((self.image_calc_height, self.image_calc_width, 4), dtype=np.uint8)
        img_array[:, :, :3] = rgb_value[:]  # Set the RGB channels
        alpha_gradient = np.linspace(255, 0, int(self.image_calc_width*overlay), dtype=np.uint8)
        img_array[:, :alpha_gradient.size, 3] = alpha_gradient
        self.gradient_mask = Image.fromarray(img_array)
        self.mask_tk = ImageTk.PhotoImage(self.gradient_mask)

        self.ori_width, self.ori_height = self.image_calc_width, self.image_calc_height
        self.last_image_state : Literal["zoomed", "original"] = "original"

        self.padding = (font2[1]/1.5)*Chest.scaleFactor
        self.multi = 2.5
        secret_work_x = -2560        # 2560 just acts as a large num (out of view)

        self.canvas = ctk.CTkCanvas(self, bg=overlay_color, bd=0, highlightthickness=0, relief='ridge', height=self.image_calc_height)
        self.canvas.pack(fill="x")
        self.canvas.create_image(secret_work_x, self.image_calc_height/2, anchor="e", tags="banner_image", image=self.im_tk, )
        self.canvas.create_image(secret_work_x, 0, anchor="nw", tags="banner_overlay", image=self.mask_tk)

        self.widgets_heights = []   #? Title, Content, Button
        self.total_height = 0
        
        self.canvas.create_text (secret_work_x, 0, anchor="nw", tags="banner_text" , text=banner_title, font=font, fill=fill)
        self.widgets_heights.append(self.canvas.bbox("banner_text")[3] + self.padding)

        if banner_content is not None:
            self.canvas.create_text (secret_work_x, 0, anchor="nw", tags="banner_content" , text=banner_content, font=font2, fill=fill)
            self.widgets_heights.append(0)
            self.content = True

        action_button = ctk.CTkButton(self, text=f" {button_text} ", font=(font[0], font2[1]), corner_radius=0, command=button_command, text_color=fill, 
                                      fg_color = hvr_clr_g(overlay_color, hvr, 40), hover_color = hvr_clr_g(overlay_color, hvr, 60))
        self.canvas.create_window (secret_work_x, 0, anchor="nw", tags="action_button", window=action_button)
        self.widgets_heights.append(self.canvas.bbox("action_button")[3])

        self.page_function_calls()
        
    def get_dominant_color(self, image: Image.Image, k: int = 4, sample_width: int = 300) -> str:
        width, height = image.size
        image = image.copy().resize((sample_width, int(sample_width/(width/height))))  # Resize the image to speed up processing
        image = image.convert('RGB')
        pixels = np.array(image)
        pixels = pixels.reshape(-1, 3)  # Reshape the image to be a list of pixels

        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(pixels)
        
        # Find the cluster center that is most common
        counts = np.bincount(kmeans.labels_)
        dominant_color = kmeans.cluster_centers_[np.argmax(counts)]

        r, g, b = dominant_color
        luminance = 0.299*r + 0.587*g + 0.114*b

        result = '#%02x%02x%02x' % tuple(dominant_color.astype(int))    # rgb to hex
        return result, tuple(dominant_color.astype(int)), luminance
            
    @lru_cache(maxsize=5)   #! careful may not release the class instance from memory (https://stackoverflow.com/questions/33672412/python-functools-lru-cache-with-instance-methods-release-object)
    def _resize_image(self, width: int, height: int) -> Image.Image:
        resized_img = self.ori_img.copy().resize((width, height))
        result = ImageTk.PhotoImage(resized_img)
        return result

    @lru_cache(maxsize=5)   #! careful may not release the class instance from memory (https://stackoverflow.com/questions/33672412/python-functools-lru-cache-with-instance-methods-release-object)
    def _resize_overlay(self, width: int, height: int) -> Image.Image:
        resized_img = self.gradient_mask.copy().resize((width, height), Image.NEAREST)
        result = ImageTk.PhotoImage(resized_img)
        return result

    def _image_logic(self):
        if self.ori_width < self.canvas_width*(2/3):
            self.image_calc_width  = int(2*self.canvas_width/3)
            self.image_calc_height = int(self.image_calc_width/self.ratio)
            self.im_tk = self._resize_image(self.image_calc_width, self.image_calc_height)
            self.canvas.itemconfigure("banner_image", image=self.im_tk)
            self.last_image_state = "zoomed"
        elif self.last_image_state == "zoomed": # the image width is larger than the 2/3th and the image state is zoomed
            self.image_calc_height = int(self.canvas_height)
            self.image_calc_width  = int(self.image_calc_height*self.ratio)
            self.im_tk = self._resize_image(self.image_calc_width, self.image_calc_height)
            self.canvas.itemconfigure("banner_image", image=self.im_tk)
            self.last_image_state = "original"

        limit = self.canvas_width*(7/9)
        if self.ori_width < limit:
            self.canvas.coords("banner_image", self.canvas_width, self.canvas_height/2)
        else:
            self.canvas.coords("banner_image", self.canvas_width+((self.ori_width-limit)/2), self.canvas_height/2)

        overlay_x1 = max(self.canvas.bbox("banner_image")[0], 0)
        overlay_width = self.canvas_width - overlay_x1
        if self.mask_tk.width() != overlay_width:
            self.mask_tk = self._resize_overlay(overlay_width, self.canvas_height)
            self.canvas.itemconfigure("banner_overlay", image=self.mask_tk)
        self.canvas.moveto("banner_overlay", overlay_x1, "")

    def _on_start(self):
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.starting_x_pos = 68*Chest.scaleFactor

        self._image_logic()

        if self.content:
            self.canvas.itemconfigure("banner_content", width=(self.canvas_width/3)-(self.starting_x_pos))
            self.widgets_heights[1] = self.canvas.bbox("banner_content")[3] + (self.multi*self.padding)
        self.total_height = sum(self.widgets_heights)
        
        starting_y_pos = (self.canvas_height-self.total_height)/2 + (self.shifter*((self.canvas_height-self.total_height)/2))
        self.canvas.moveto("banner_text", self.starting_x_pos, starting_y_pos)
        if self.content:
            self.canvas.moveto("banner_content", self.starting_x_pos, starting_y_pos + self.widgets_heights[0])
            self.canvas.moveto("action_button" , self.starting_x_pos, starting_y_pos + self.widgets_heights[0] + self.widgets_heights[1])
        else:
            self.canvas.moveto("action_button" , self.starting_x_pos, starting_y_pos + self.widgets_heights[0])
    
    def _on_update(self):
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        self._image_logic()

        if self.content:
            y_before = self.canvas.bbox("banner_content")[3]
            self.canvas.itemconfigure("banner_content", width=(self.canvas_width/3)-(self.starting_x_pos))
            y_after  = self.canvas.bbox("banner_content")[3]
            if y_after != y_before:
                #? Make the whole collection move to maintain the shifter position... (this is the easy way. I believe it can be optimized)
                content_bbox = self.canvas.bbox("banner_content")
                self.widgets_heights[1] = (content_bbox[3]-content_bbox[1]) + (self.multi*self.padding)
                self.total_height = sum(self.widgets_heights)
                starting_y_pos = (self.canvas_height-self.total_height)/2 + (self.shifter*((self.canvas_height-self.total_height)/2))
                self.canvas.moveto("banner_text"   , "", starting_y_pos)
                self.canvas.moveto("banner_content", "", starting_y_pos + self.widgets_heights[0])
                self.canvas.moveto("action_button" , "", starting_y_pos + self.widgets_heights[0] + self.widgets_heights[1])

    def page_function_calls(self):
        self.page.starting_call_list.append(self._on_start)
        self.page.updating_call_list.append(self._on_update)

    #! Current probelms:
    #//  1. when scaling down the image (reducing the width of the window) the if condition is not correct yet.
    #//  2. the text wrap isn't ready yet (doesn't allow for the increase of decrease of the num of lines). 
    #//  3. need to work on the color choice for the text and button (probably based on the overlay_color lightness)
    #//  4. Check on the image placement when (its width is so big). Maybe make it so that it is always centered, with the first 1/6 of the canvas width as the limit.
    #//  5. the overlay needs some work

# Note: canvas images and canvas text don't scale with display scale by default, so they need to be updated manually depending on the scale.