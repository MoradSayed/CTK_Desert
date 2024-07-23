import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
from .Page_base_model import Page_BM
from .Theme import *
from .utils import hvr_clr_g, change_pixel_color, color_finder
import textwrap
from typing import Union, Tuple, Callable, Optional, Any, List

class C_Widgits():
    def __init__(self, page_class, parent):
        self.page = page_class
        self.parent = parent
        
    def section(self, 
                title:      str = None, 
                fg_color:   Union[tuple, str] = "transparent", 
                font:       Union[tuple, ctk.CTkFont] = (FONT_B, 25), 
                text_color: Union[str, Tuple[str, str]] = (LIGHT_MODE["text"], DARK_MODE["text"]),
                padx: Union[int, Tuple[int, int]] = 0, 
                pady: Union[int, Tuple[int, int]] = 10):
        
        section_frame = ctk.CTkFrame(self.parent, fg_color= fg_color)

        if title != None:
            title_frame = ctk.CTkFrame(section_frame, fg_color= "transparent")  # contains the label and the button (if it exists).
            section_label = ctk.CTkLabel(title_frame, text=f"{title}", font=font, fg_color="transparent", text_color=text_color, anchor="w")
            section_label.pack(side="left", fill="x", padx=20)
            title_frame.pack(fill="x")

        ops_frame = ctk.CTkFrame(section_frame, fg_color= "transparent")
        ops_frame.pack(fill="x", padx=20, pady=10)

        section_frame.pack(fill="x", padx=padx, pady=pady)

        return ops_frame  
        
    def section_button(self, 
                       section:         ctk.CTkFrame, 
                       button_icon:     Union[str, Image.Image] = None, 
                       button_command:  Callable = None, 
                       icon_height:     int = 30, 
                       button_text:     str = "", 
                       font:            Union[Tuple[str, int], ctk.CTkFont] = (FONT, 15), 
                       fg_color:        Union[str, Tuple[str, str]] = (LIGHT_MODE["accent"], DARK_MODE["accent"]), 
                       hover_color:     Union[str, Tuple[str, str]] = (hvr_clr_g(LIGHT_MODE["accent"], "l", 20), hvr_clr_g(DARK_MODE["accent"], "d", 20)) ):

            if button_icon != None:
                if isinstance(button_icon, str):
                    button_icon = Image.open(button_icon)
                elif isinstance(button_icon, Image.Image):
                    pass
                else:
                    raise TypeError("button_icon should be a path to an image or an Image object.")
                w, h = button_icon.size[0],button_icon.size[1]
                r = w/h
                s = (int(icon_height*r), int(icon_height))
                button_icon = ctk.CTkImage(button_icon, size=s)

            section_button = ctk.CTkButton(section.master.winfo_children()[0], text=f"{button_text}", font=font, 
                                           fg_color=fg_color, hover_color=color_finder(section.master) if fg_color == "transparent" else hover_color, 
                                           image=button_icon, width=s[0], height=s[1], 
                                           command=button_command)
            section_button.pack(side="right", fill="x", padx=20)

            return section_button
    
###############################################################################################################################################################################################

    def _sectionUnit(self, section, title : str = ""):
               
        unit_frame = ctk.CTkFrame(section, fg_color= "transparent")

        unit_label = ctk.CTkLabel(unit_frame, text=f"{title}", font=(FONT, 20))
        unit_label.pack(side="left", fill="x", padx=20, pady=10)

        unit_frame.pack(fill="x")
        
        return unit_frame
    
    def Button_unit(self, section, title : str = "",
                    text: str = "Click",
                    command: Callable = lambda: None,
                    invert: bool = False,
                    lone_widget: bool = False,
                    fg_color: Optional[Union[str, Tuple[str, str]]] = (LIGHT_MODE["accent"], DARK_MODE["accent"]),
                    font: tuple = (FONT, 15),
                    width: int = 140,
                    height: int = 28,
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
            text_color  = (LIGHT_MODE["text"], DARK_MODE["text"])
            hover_color = (hvr_clr_g(fg_color[0], "l"), hvr_clr_g(fg_color[1], "d"))
            
        unit_option = ctk.CTkButton(master = master, text = text, font = font, text_color = text_color, width = width, height = height, fg_color = fg_color, hover_color = hover_color, border_width = border_width, border_color = border_color, command = command)
        unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if invert:  #? Careful that fg_color is now stored in the text_color var, and fg_color is actually "transparent". 
            textclr_onEntry = (LIGHT_MODE["text"], DARK_MODE["text"]) if text_color != (LIGHT_MODE["text"], DARK_MODE["text"]) else (DARK_MODE["text"], LIGHT_MODE["text"])
            unit_option.bind("<Enter>", command=lambda e: unit_option.configure(fg_color=text_color, text_color=textclr_onEntry))
            unit_option.bind("<Leave>", command=lambda e: unit_option.configure(fg_color="transparent", text_color=text_color))

        return unit_option

    def ComboBox_unit(self, section, title : str = "",
                      values: Optional[List[str]] = None,
                      default: str = None, 
                      command: Union[Callable[[str], Any], None] = lambda var: None, 
                      lone_widget: bool = False,
                      variable: Union[ctk.Variable, None] = None, 
                      fg_color: Optional[Union[str, Tuple[str, str]]] = (LIGHT_MODE["primary"], DARK_MODE["primary"]),
                      border_color: Optional[Union[str, Tuple[str, str]]] = (hvr_clr_g(LIGHT_MODE["primary"], "l", 30), hvr_clr_g(DARK_MODE["primary"], "d", 30)),
                      font: Optional[tuple] = (FONT, 15),
                      width: int = 140,
                      height: int = 28):

        if not lone_widget:
            master = self._sectionUnit(section, title)
        else:
            master = section

        variable = ctk.StringVar(value=default) if variable is None else variable
        unit_option = ctk.CTkComboBox(master, fg_color = fg_color, border_color=border_color, button_color=border_color, 
                                      font = font, text_color = (LIGHT_MODE["text"], DARK_MODE["text"]), width = width, height = height, 
                                      dropdown_fg_color=fg_color, dropdown_font=font, dropdown_text_color = (LIGHT_MODE["text"], DARK_MODE["text"]),  
                                      state = "readonly", values = values, variable = variable, command = command)
        # unit_option.set(f"{default}") if default is not None else None
        unit_option.pack(side="right", fill="x", padx=20, pady=10)

        return unit_option, variable
    
    def CheckBox_unit(self, section, title : str = "",
                      default: bool = False, 
                      command: Union[Callable[[], Any], None] = None,
                      lone_widget: bool = False,
                      variable: Union[ctk.Variable, None] = None,

                      fg_color: Optional[Union[str, Tuple[str, str]]] = (LIGHT_MODE["accent"], DARK_MODE["accent"]),
                      border_color: Optional[Union[str, Tuple[str, str]]] = None,
                      checkmark_color: Optional[Union[str, Tuple[str, str]]] = None,

                      width: int = 100,
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
                                      fg_color=fg_color, hover_color=(hvr_clr_g(fg_color[0], "l"), hvr_clr_g(fg_color[1], "d")), 
                                      border_color=border_color, checkmark_color=checkmark_color,
                                      command=command, variable=variable, onvalue=True, offvalue=False,)
        # if default != None:
        #     unit_option.configure(variable=default) 
        unit_option.pack(side="right", fill="x", pady=10)

        return unit_option, variable
    
    def Entry_unit(self, section, title : str = "",
                   placeholder_text: Union[str, None] = None,
                   lone_widget: bool = False,
                   textvariable: Union[ctk.StringVar, None] = None,

                   fg_color: Optional[Union[str, Tuple[str, str]]] = "transparent",
                   font: Optional[tuple] = (FONT, 15),
                   width: int = 140,
                   height: int = 28,
                   ):
        
        if not lone_widget:
            master = self._sectionUnit(section, title)
        else:
            master = section

        text_color = (LIGHT_MODE["text"], DARK_MODE["text"])
        textvariable = ctk.StringVar(value=placeholder_text) if textvariable is None else textvariable
        unit_option = ctk.CTkEntry(master, font=font, fg_color=fg_color, text_color=text_color, width=width, height=height, textvariable=textvariable)
        unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if placeholder_text is not None:
            plchldrClr = (LIGHT_MODE["primary"], DARK_MODE["primary"])
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
    
class small_tabs(ctk.CTkFrame):     #^ Currently working on this
    def __init__(self, page_class: Page_BM, parent, img_width=300, img_height=180, padx=20, pady=(0, 10)):
        super().__init__(parent, fg_color="transparent")
        self.page = page_class
        self.parent = parent
        self.image_width = img_width
        self.image_height = img_height
        self.canvas_color = self.page.get_scrframe_color()
        self.tabs = [] 
        self.images = [] 
        
        self.reorder_btn_state = 0
        self.unit_h = 0
        self.swapping = 0

        self.pack(expand=True, fill="x", padx=padx, pady=pady)
        # self.page_function_calls()
        
    def tab(self, text, image, button_icon=None, button_command=None, icon_size=(25, 25)):  #! current problem is with text wrapping
        if self.reorder_btn_state:
            self.reorder()  # closes the reorder action if it is active

        tab_cont = ctk.CTkFrame(self, fg_color="transparent")

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

        canvas = ctk.CTkCanvas(tab_cont, bg=self.canvas_color[0] if ctk.get_appearance_mode() == "Light" else self.canvas_color[1], 
                               bd=0, highlightthickness=0, relief='ridge', width=self.image_width, height=self.image_height)
        canvas.pack(side="left", pady=30)
        canvas.create_image(self.image_width/2, self.image_height/2, anchor="center", image=im_ctk)

        tab_title = ctk.CTkLabel(tab_cont, fg_color="transparent", text=f"{text}", font=(FONT, 20), anchor="w", justify="left")
        tab_title.pack(padx=20, side="left")

        if button_icon:
            button_image = change_pixel_color(button_icon, color=f'{ICONS["_l"]}+{ICONS["_d"]}', return_img=True)
            button_image = ctk.CTkImage(*button_image, size=icon_size)
            ctk.CTkButton(tab_cont, text="", fg_color="transparent", hover_color=self.canvas_color, image=button_image, 
                          command=button_command, width=30, height=30).pack(side="right")

        tab_cont.pack(expand=True, fill="both")
        # tab_title.update()
        # tab_title.configure(wraplength = 3*tab_title.winfo_width()/4)

        White_line = ctk.CTkFrame(tab_cont, fg_color=(DARK_MODE["background"], LIGHT_MODE["background"]), height=2)
        White_line.place(relx=0, rely=1, relwidth=1, anchor="sw")

        self.tabs.append(tab_cont)
        return tab_cont

    def reorder(self): # for in app swap
        self.reorder_btn_state = not self.reorder_btn_state
        if self.reorder_btn_state:
            # print("starting reorder")
            self.unit_h = self.tabs[0].winfo_height()
            for tab in self.tabs:
                tab.bind("<Enter>"   , lambda e, t=tab: t.configure(fg_color=(LIGHT_MODE["primary"], DARK_MODE["primary"])))
                tab.bind("<Leave>"   , lambda e, t=tab: t.configure(fg_color="transparent"))
                tab.bind("<B1-Motion>", lambda e, t=tab: self._on_motion(e, t))    # perfect
        else:
            # print("closing reorder")
            for tab in self.tabs:
                tab.unbind("<Enter>")
                tab.unbind("<Leave>")
                tab.unbind("<B1-Motion>")

    def _on_motion(self, event, tab):
        target_step = event.y/self.unit_h
        if target_step < 0:
            target_step -= 1
        target_step = int(target_step)
        # print(f"event: {event.y}, step: {target_step}")
        if self.swapping == 0 and (target_step >= 1 or target_step <= -1):
            self.swapping = 1
            self.swap(tab, target_step)
            self.swapping = 0

    def swap(self, tab, step):  # for code swap
        current_pos = self.tabs.index(tab)
        target_pos = current_pos + step
        tabs_count = len(self.tabs)
        
        if target_pos >= 0 and target_pos < tabs_count:
            self.tabs.insert(target_pos, self.tabs.pop(current_pos))

            if target_pos+1 < tabs_count:
                self.tabs[target_pos].pack(before=self.tabs[target_pos+1], expand=True, fill="both")
            elif target_pos+1 == tabs_count:
                self.tabs[target_pos].pack(after=self.tabs[target_pos-1], expand=True, fill="both")
            
            self.update()   # update so that if the bind is still holding an old value it lets it out, so that it doesn't cause a swap after the <self.swapping> lock has been unlocked

    def _on_update(self):
        for tab in self.tabs:
            label = tab.winfo_children()[1]
            label.configure(wraplength = 3*label.winfo_width()/4)

    def page_function_calls(self):
        self.page.updating_call_list.append(self._on_update)

class large_tabs(ctk.CTkFrame):
    def __init__(self, page_class, parent, img_width=500, img_height=300, padx=10, pady=10, autofit=True):
        super().__init__(parent, fg_color="transparent")
        self.page = page_class
        self.parent = parent
        self.image_width = img_width
        self.image_height = img_height
        self.padx = padx
        self.pady = pady
        self.autofit = autofit
        self.canvas_color = self.page.get_scrframe_color()

        self.rows = []
        self.tabs = {}
        self.images = []
        self.tabs_per_row = 0
        self.constructed_expander = None
        self.hidden = False
        self.pending_update = False

        self.pack(expand=True, fill="x")

        self.page_function_calls()

    def tab(self, text=None, image=None, button_icon=None, icon_size=20, button_command=None):  
        expander = self.constructor(text, image, button_icon, icon_size, button_command) if self.constructed_expander == None else self.constructed_expander

        row_getter = self.row_frame()
        if row_getter != 0:
            self.rows.append(row_getter)

        expander.pack(in_ = self.rows[-1], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady)
        
        if self.constructed_expander == None:
            if len(self.rows)-1 not in self.tabs:
                self.tabs[len(self.rows)-1] = []
            self.tabs[len(self.rows)-1].append(expander)
            
        self.update()
        self.constructed_expander = None
        if len(self.rows) == 1:
            self.tabs_per_row = len(self.tabs[0])

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

        content = ctk.CTkFrame(tab_cont, fg_color=(LIGHT_MODE["primary"], DARK_MODE["primary"]), width=canvas.winfo_width())
        text = ctk.CTkLabel(content, text=f"{text}", font=(FONT, 20), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]))
        text.pack(side="left", padx=10, pady=5)
        if button_icon != None:
            self.butt0n_icon(["_", content], button_icon, icon_size, button_command)
        content.pack(expand=True, fill="x", pady=10)
        
        tab_cont.pack()
        return expander

    def butt0n_icon(self, parent, button_icon, icon_size: int = 20, button_command : Callable = None, override_color: bool = False):  # parent is a list of two elements, the first is the canvas and the second is the content frame
        if override_color:  #! change this so that if he pass a tuple then automatically override the color, if it is just an image then change the color
            image = Image.open(button_icon)
            image = [image, image]
        else:
            image = change_pixel_color(button_icon, color=f'{ICONS["_l"]}+{ICONS["_d"]}', return_img=True)
        w, h = image[0].size[0],image[0].size[1] # image[0] or image[1] doesn't matter
        r = w/h
        s = (int(icon_size*r), icon_size)
        image = ctk.CTkImage(image[0], image[1], size=s)
        actbtn = ctk.CTkButton(parent[1], text="", image=image, fg_color="transparent", hover_color=(LIGHT_MODE["primary"], DARK_MODE["primary"]), 
                                width=int(icon_size*r), command= button_command)
        actbtn.pack(side="right", padx=5, pady=5)

    def row_frame(self):
        if len(self.rows) == 0 or self.rows[-1].winfo_width() < (self.image_width+(3*self.padx))*(len(self.tabs[len(self.rows)-1])+1): # width of a tab * (number of tabs in the last row + the one that i wanna create):
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", expand=True)
        else:
            row = 0

        return row

    def ltabs_update(self):
        if self.hidden:
            self.pending_update = True
            return 0
        if self.autofit and len(self.rows) > 0:
            self.available_tab_spaces = int(self.rows[0].winfo_width() / (self.image_width+(3*self.padx)))
            print(self.available_tab_spaces, self.tabs_per_row)
            if self.available_tab_spaces != self.tabs_per_row:
                #^ Filling empty spaces
                if len(self.rows) > 1 and self.available_tab_spaces > self.tabs_per_row:    # if there's more space to add more tabs and there's more than one row
                    for row in range(len(self.rows)-1):     # go through all the rows except the last one
                        print(f"row: {row}", f"len(self.rows): {len(self.rows)}", f"len(self.tabs): {len(self.tabs)}")
                        if row >= len(self.rows)-1:          # if the row is the last row, break (we use this as a safety measure, as the size of the rows list might change during the loop)
                            break
                        self.req_tabs = self.available_tab_spaces - len(self.tabs[row])  # calculate the number of tabs that should be added to the row
                        
                        #* if the required tabs are less than the number of tabs in the next row
                        if self.req_tabs < len(self.tabs[row+1]):
                            # print("F1: just taking some of the next row")
                            self.Shift_up(row)
                        
                        #* if the required tabs are equal to the number of tabs in the next row
                        #* or if the required tabs are more than the number of tabs in the next row and the next row is the last row
                        elif (self.req_tabs == len(self.tabs[row+1])) or ((self.req_tabs > len(self.tabs[row+1])) and (row+1 == list(self.tabs)[-1])):
                            # print("F2: taking all of the next row then deleting it and shifting the dict keys")
                            self.Shift_up_with_delete(row)

                        #* if the required tabs are more than the number of tabs in the next row and the next row is not the last row
                        elif (self.req_tabs > len(self.tabs[row+1])) and (row+1 != list(self.tabs)[-1]) :    
                            # print("F3: taking from the next row and the following ones untill the req_tabs is satisfied, while deleting the empty rows and shifting the dict keys")
                            while self.req_tabs > 0:
                                if self.req_tabs >= len(self.tabs[row+1]):
                                    self.req_tabs -= len(self.tabs[row+1])   # leave this line here, because the next line will change the number of tabs in the next row
                                    self.Shift_up_with_delete(row)
                                else:
                                    self.Shift_up(row)
                                    self.req_tabs = 0                        # leave this line here, because the shift_up function requires the original value of req_tabs

                #^ Removing extra tabs
                elif len(self.rows) >= 1 and self.available_tab_spaces < self.tabs_per_row:    # if there's more space to add more tabs and there's more than one row
                    num_of_tabs = ((len(self.rows)-1)*self.tabs_per_row)+len(self.tabs[len(self.rows)-1])  # number of tabs in the rows
                    for row in range(int(num_of_tabs/self.available_tab_spaces)):     # go through all the rows except the last one
                        # print(f"Before:\nrows: {self.rows}\ntabs: {self.tabs}\n")
                        # print(f"row: {row}", f"len(self.rows): {len(self.rows)}", f"len(self.tabs): {len(self.tabs)}")
                        self.req_tabs = len(self.tabs[row]) - self.available_tab_spaces   # calculate the number of tabs that should be added to the row
                        if self.req_tabs == 0:
                            break
                        # print(f"req_tabs: {self.req_tabs}, empty spaces: {self.available_tab_spaces - len(self.tabs[row+1])}")
                        
                        if len(self.rows) == 1: #if we are starting from the last row
                            # print("R1: only one row is available, Creating a new empty row")
                            new_frame = ctk.CTkFrame(self, fg_color="transparent")
                            new_frame.pack(fill="x", expand=True)
                            self.rows.append(new_frame)
                            self.tabs[len(self.rows)-1] = []
                            self.Shift_down(row)

                        #* if the required tabs are less than the number of empty spaces in the next row
                        elif self.req_tabs <= self.available_tab_spaces - len(self.tabs[row+1]):              #^ Finished
                            # print("R2: Giving tabs to the next row")
                            self.Shift_down(row)
                        
                        #* if the required tabs are more than the number of tabs in the next row and the next row is the last row
                        elif (self.req_tabs > self.available_tab_spaces - len(self.tabs[row+1])):
                            # print("R3: Giving all to the next row and creating a new empty row if this is the last row")
                            self.Shift_down(row)
                            if (row+1 == list(self.tabs)[-1]): # if the next row is the last row
                                new_frame = ctk.CTkFrame(self, fg_color="transparent")
                                new_frame.pack(fill="x", expand=True)
                                self.rows.append(new_frame)
                                self.tabs[len(self.rows)-1] = []
                        # print(f"After:\nrows: {self.rows}\ntabs: {self.tabs}\n")

            self.tabs_per_row = len(self.tabs[0])
            
    def Shift_up(self, row): 
        if self.req_tabs == 1:
            self.tabs[row+1][0].pack(in_=self.rows[row], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady)
            self.tabs[row].append(self.tabs[row+1][0])
            del self.tabs[row+1][0]
        else:
            for tab in self.tabs[row+1][:self.req_tabs]:
                tab.pack(in_=self.rows[row], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady)
                self.tabs[row].append(tab)
            del self.tabs[row+1][:self.req_tabs]

    def Shift_down(self, row):
        if self.req_tabs == 1:
            before_arg = self.tabs[row+1][0] if len(self.tabs[row+1]) > 0 else None
            self.tabs[row][-1].pack(in_=self.rows[row+1], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady, before = before_arg)
            self.tabs[row+1].insert(0, self.tabs[row][-1])
            del self.tabs[row][-1]
        else:
            for tab in self.tabs[row][:-self.req_tabs-1:-1]:
                before_arg = self.tabs[row+1][0] if len(self.tabs[row+1]) > 0 else None
                tab.pack(in_=self.rows[row+1], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady, before = before_arg)
                self.tabs[row+1].insert(0, tab)
            del self.tabs[row][:-self.req_tabs-1:-1]

    def Shift_up_with_delete(self, row): # takes row
        for tab in self.tabs[row+1]:
            self.tabs[row].append(tab)
            tab.pack(in_=self.rows[row], expand=self.autofit, fill="both", side="left", padx=self.padx, pady=self.pady)
        for key in range(row+1, len(self.tabs)-1):  # from the next row to the second last row
            self.tabs[key] = self.tabs[key+1]   # shift the dict keys
        del self.tabs[len(self.tabs)-1]
        self.rows[row+1].destroy()
        del self.rows[row+1] 

    def show(self):
        """Display the hidden widget and its tabs
        """
        if self.hidden:
            self.pack(expand=True, fill="x")
            self.update()
            if self.pending_update:
                print("pending updates")
                self.hidden = False
                self.pending_update = False
                self.ltabs_update()
            else:
                self.hidden = False

    def hide(self):
        """Hide the Widget and its tabs
        """
        if self.hidden == False:
            self.hidden = True
            final_height = self.parent.winfo_height() - self.winfo_height()
            self.pack_forget()
            self.parent.configure(height=final_height)

    def page_function_calls(self):
        self.page.updating_call_list.append(self.ltabs_update)

class Banner(ctk.CTkFrame): #! change the image resizing stuff (_, 642) | 0.4*window_height
    def __init__(self, page, parent, overlay_color, image_path=None, banner_title="", banner_content=None, button_text="Click", font=(FONT_B, 25), font2=(FONT, 15), button_command=None, button_colors=(LIGHT_MODE["accent"], DARK_MODE["accent"]), shifter=0, overlay=0.5): 
        #shifter and overlay are values between 0 and 1
        super().__init__(parent, fg_color="transparent")
        if overlay_color == "transparent":
            raise ValueError("Banner color can't be transparent, provide a color value.")
        
        self.page = page
        self.parent_frame = parent
        self.canvas_color = overlay_color

        self.pack(fill="both")
        self.im = Image.open(r"C:\Users\Morad\Desktop\Page_layout_library\Assets\Images\val.png") if image_path is None else Image.open(image_path)
        self.im = self.im.convert("RGBA")
        img_data = np.array(self.im)
        width, _ = self.im.size
        alpha_gradient = np.linspace(30, 255, int(width*overlay), dtype=np.uint8)  # Create a gradient from 255 to 0
        img_data[:, :int(width*overlay), 3] = alpha_gradient  # Assign the gradient to the alpha channel
        self.new_img = Image.fromarray(img_data)
        self.im_tk  = ImageTk.PhotoImage(self.new_img)

        self.banner_ttitle = banner_title
        self.banner_content = banner_content
        self.button_text = button_text
        self.font = font
        self.font2 = font2
        self.shifter = shifter
        
        self.padding = self.font[1]
        self.multi = 1.5

        self.canvas = ctk.CTkCanvas(self, bg=self.canvas_color, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()

        self.action_button = ctk.CTkButton(self, text=self.button_text, command=button_command, fg_color=button_colors, hover_color=(hvr_clr_g(button_colors[0], "l"), hvr_clr_g(button_colors[1], "d")), font=(font[0], font[1]*0.75), corner_radius=0)

        self.page_function_calls()
        
    def init(self):
        self.update_widget()

    def update_widget(self):
        self.frame_width = self.parent_frame.winfo_width()
        if self.frame_width == 1:
            raise ValueError("Parent width is 1, if you're using this widget in a page, make sure it's called when the page is opened.")
        if self.frame_width != self.im_tk.width():
            self.r = self.im.size[0]/self.im.size[1] # aspect ratio = width/height
            self.s = (self.frame_width, int(self.frame_width/self.r))
            self.im_tk  = ImageTk.PhotoImage(self.new_img.resize(self.s))

            try:
                self.canvas.delete("banner_image")
                self.canvas.delete("banner_text")
                self.canvas.delete("banner_content")
            except:
                pass
            self.canvas.config(width=self.s[0], height=self.s[1])
            b_image = self.canvas.create_image(0, 0, anchor="nw", tags="banner_image", image=self.im_tk, )

            #TODO//: wrap all these widgets to a location manager
            #TODO//: use text wrap for dynamic resizing of the banner content
            #TODO: change font size dynamically
            b_titletext = self.canvas.create_text ((self.s[0]*(1/4)*(1/4)), 0, anchor="nw", tags="banner_text" , text=self.banner_ttitle, font=self.font, fill="white")
            bbox_title = self.canvas.bbox(b_titletext)

            if self.banner_content is not None:
                self.numOfChars = 40
                self.banner_content = textwrap.fill(self.banner_content, width=(self.numOfChars/697)*(self.s[0]//2)) # 40 characters per line, 697 is the width available for the text 
                b_content = self.canvas.create_text ((self.s[0]*(1/4)*(1/4)), bbox_title[3]+self.padding, anchor="nw", tags="banner_content" , text=self.banner_content, font=self.font2, fill="white")
                bbox_content = self.canvas.bbox(b_content)
                self.multi = 2
            else:
                bbox_content = bbox_title

            b_btn = self.canvas.create_window ((self.s[0]*(1/4)*(1/4)), bbox_content[3]+(self.multi*self.padding), anchor="nw", tags="acbtn", window=self.action_button)
            bbox_btn = self.canvas.bbox(b_btn)

            length = bbox_btn[3]
            start_y_pos = (self.s[1]-length)/2 + (self.shifter*((self.s[1]-length)/2))
            self.canvas.moveto(b_titletext, (self.s[0]*(1/4)*(1/4)), start_y_pos)
            if self.banner_content is not None:
                self.canvas.moveto(b_content  , (self.s[0]*(1/4)*(1/4)), start_y_pos + bbox_title[3]+self.padding)
            self.canvas.moveto(b_btn      , (self.s[0]*(1/4)*(1/4)), start_y_pos + bbox_content[3]+(self.multi*self.padding))

    def page_function_calls(self):
        self.page.starting_call_list.append(self.init)
        self.page.updating_call_list.append(self.update_widget)

