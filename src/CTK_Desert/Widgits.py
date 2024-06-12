import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
from .Theme import *
from .utils import hvr_clr_g, change_pixel_color
import textwrap
from typing import Callable

class C_Widgits():
    def __init__(self, page_class, parent):
        self.page = page_class
        self.parent = parent
        self.c = 1 # multiplier for y padding
        
    def section(self, Title=None, padx=0, pady=10, button_text=None, button_command=None, button_icon=None, icon_height=50):
        section_frame = ctk.CTkFrame(self.parent, fg_color= "transparent")

        if Title != "" and Title != None:
            title_frame = ctk.CTkFrame(section_frame, fg_color= "transparent")
            section_label = ctk.CTkLabel(title_frame, text=f"{Title}", font=(FONT_B, 25), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="w")
            section_label.pack(side="left", fill="x", padx=20)
            title_frame.pack(fill="x")

        if button_text != None:
            if button_icon != None:
                button_icon = Image.open(button_icon)
                w, h = button_icon.size[0],button_icon.size[1]
                r = w/h
                s = (int(icon_height*r), int(icon_height))
                button_icon = ctk.CTkImage(button_icon, size=s)
            section_button = ctk.CTkButton(title_frame, text=f"{button_text}", font=(FONT, 15), command=button_command, fg_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), hover_color=(hvr_clr_g(LIGHT_MODE["accent"], "l", 20), hvr_clr_g(DARK_MODE["accent"], "d", 20)), image=button_icon)
            section_button.pack(side="right", fill="x", padx=20)
        

        ops_frame = ctk.CTkFrame(section_frame, fg_color= "transparent")
        ops_frame.pack(fill="x", padx=20, pady=10)

        section_frame.pack(fill="x", padx=padx, pady=pady)

        if button_text==None:
            return ops_frame  
        else:
            return ops_frame, section_button
    
###############################################################################################################################################################################################

    def section_unit(self, section, title : str = "", widget : str =None, command: callable =None, values : list =None, default : str =None):
        """
        Adds a unit to a section with specified parameters.

        Parameters:
        - section (ctk.Frame): The parent widget to which the unit will be added.
        - title (str, optional): The title of the unit.
        - widget (str, optional): The type of widget to be used in the unit. 
            - Supported values: "combobox", "button", "checkbox", "entry", "switch".
        - command (callable, optional): The command to be executed when the widget is interacted with.
        - values (list, optional): A list of values to populate a combobox widget.
        - default: The default value for the widget.
            - treated as the text for a button widget.

        Returns:
        - ctk.Frame: The frame containing the unit.

        You can get the value of the widget using the gval method of the returned frame.
        """
                
        unit_parent = section
        unit_frame = ctk.CTkFrame(unit_parent, fg_color= "transparent")

        unit_label = ctk.CTkLabel(unit_frame, text=f"{title}", font=(FONT, 20))
        unit_label.pack(side="left", fill="x", padx=20, pady=10)

        if widget == "combobox" or widget == "ComboBox":
            unit_option = ctk.CTkComboBox(unit_frame, font=(FONT, 15), values = values, dropdown_font=(FONT, 15), state="readonly", command=command)
            unit_option.set(f"{default}")
            unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if widget == "button" or widget == "Button":
            unit_option = ctk.CTkButton(unit_frame, text=f"{'' if default == None else default}", font=(FONT, 15), command=command, fg_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), hover_color=(hvr_clr_g(LIGHT_MODE["accent"], "l", 20), hvr_clr_g(DARK_MODE["accent"], "d", 20)))
            unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if widget == "checkbox" or widget == "CheckBox":
            unit_option = ctk.CTkCheckBox(unit_frame, text="", command=command, fg_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), hover_color=(hvr_clr_g(LIGHT_MODE["accent"], "l", 20), hvr_clr_g(DARK_MODE["accent"], "d", 20)), onvalue=True, offvalue=False,)
            if default != None:
                unit_option.configure(variable=default) 
            unit_option.pack(side="right", fill="x", pady=10)

        if widget == "entry" or widget == "Entry":
            unit_option = ctk.CTkEntry(unit_frame, font=(FONT, 15), fg_color="transparent", placeholder_text=f"{default}", placeholder_text_color=(LIGHT_MODE["text"], DARK_MODE["text"]))
            # unit_option.insert(0, f"{default}")
            unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if widget == "switch" or widget == "Switch":
            unit_option = ctk.CTkSwitch(unit_frame, command=command, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l", 85), hvr_clr_g(DARK_MODE["background"], "d", 85)), progress_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), onvalue=True, offvalue=False, text="", bg_color="transparent", border_color="transparent")
            if default != None:
                unit_option.configure(variable=default) 
            unit_option.pack(side="right", fill="x", pady=10)

        unit_frame.pack(fill="x")

        def gval():
            if widget != None:
                return unit_option.get()
            return None
        unit_frame.gval = gval

        self.page.Page_update_manager(update_with_extend = False)
        
        return unit_frame
    
###############################################################################################################################################################################################

    def add_tab(self, section, text=None, image=None, size=None, simage_size=250, limage_size=250): # (frame >> frame_template, image input is of a normal image)
        if image != None:        
            im = Image.open(image)
            w, h = im.size[0],im.size[1]
            r = w/h
                    
        if size == "l":
            # s = (limage_size, int(limage_size/r))
            # im_ctk = ImageTk.PhotoImage(im.resize(s))
            # self.large(section, text, im_ctk)
            pass
        elif size == "s":
            s = (simage_size, int(simage_size/r))
            im_ctk = ctk.CTkImage(im, size=s)
            self.small(section, text, im_ctk)
        
        self.page.Page_update_manager(update_with_extend = False)

    # Type num 1 (Ready to use)
    def Label_func(self, parent_f):          
        l_widget = ctk.CTkLabel(parent_f, text="No Recent projects", font=(FONT, 20), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="center")
        l_widget.pack(fill="x", padx=20, pady=10*self.c, expand=True)

    # Type num 3 (Ready to use)
    def small(self, parent_f, text, image):  
        tab_cont = ctk.CTkFrame(parent_f, fg_color="transparent", height=300, width=self.parent.winfo_width())

        tab_img = ctk.CTkButton(tab_cont, fg_color="transparent", text="", image=image, hover_color=self.page.get_scrframe_color())
        tab_img.pack(padx=20, pady=10*self.c, side="left")

        tab_cont.update()
        tit_f   = ctk.CTkFrame(tab_cont, fg_color="transparent",)
        newtext = textwrap.shorten(text, 50)
        tab_tit = ctk.CTkLabel(tit_f, fg_color="transparent", text=f"{newtext}", font=(FONT, 20), anchor="w")
        tab_tit.pack(fill = "both", expand = True)
        tit_f.pack(pady=10*self.c, fill = "x", expand = True, side="left")

        add_btn = ctk.CTkButton(tab_cont, width=30, height=30, text="+", font=(FONT_B, 30),  
                                fg_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), 
                                hover_color=(hvr_clr_g(LIGHT_MODE["accent"], "l", 20), hvr_clr_g(DARK_MODE["accent"], "d", 20)), 
                                command= lambda : None)                 # command= lambda num = self.image_count.queue[0]: self.add_image_btn_command(num) #
        add_btn.place(relx=0.975, rely=0.5, anchor="e")

        tab_cont.pack(expand=True, fill="both", pady=10)

        White_line = ctk.CTkFrame(parent_f, fg_color=(DARK_MODE["background"], LIGHT_MODE["background"]), height=2)
        White_line.pack(fill="x", expand=True, padx = 20)

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
            
        self.page.Page_update_manager(update_with_extend = False)
        self.constructed_expander = None
        if len(self.rows) == 1:
            self.tabs_per_row = len(self.tabs[0])

        return expander.winfo_children()[0].winfo_children()

    def constructor(self, text=None, image=None, button_icon=None, icon_size=20, button_command=None):
        im = Image.open(image)
        w, h = im.size[0],im.size[1]
        r = w/h
        if r > (self.image_width/self.image_height):
            s = (int(self.image_height*r), self.image_height)
        else:
            s = (self.image_width, int(self.image_width/r))
        im_ctk = ImageTk.PhotoImage(im.resize(s))
        self.images.append(im_ctk)

        expander = ctk.CTkFrame(master=self.parent, fg_color=self.canvas_color, bg_color=self.canvas_color)
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
        if override_color:
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
        if len(self.rows) == 0 or self.rows[-1].winfo_width() < (self.image_width+self.padx)*(len(self.tabs[len(self.rows)-1])+1): # width of a tab * (number of tabs in the last row + the one that i wanna create):
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

    def show(self): # simplify it (p_u_m)
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
            self.page.Page_update_manager(update_with_extend = False)

    def hide(self):
        """Hide the Widget and its tabs
        """
        if self.hidden == False:
            self.hidden = True
            final_height = self.parent.winfo_height() - self.winfo_height()
            self.pack_forget()
            self.parent.configure(height=final_height)
            self.page.Page_update_manager(update_with_extend = False)

    def page_function_calls(self):
        self.page.updating_call_list.append(self.ltabs_update)

class Banner(ctk.CTkFrame):
    def __init__(self, page, parent, overlay_color, image_path=None, banner_title="", banner_content=None, button_text="Click", font=(FONT_B, 25), font2=(FONT, 15), button_command=None, button_colors=(LIGHT_MODE["accent"], DARK_MODE["accent"]), shifter=0, overlay=0.5): 
        #shifter and overlay are values between 0 and 1
        super().__init__(parent, fg_color="transparent")
        if overlay_color == "transparent":
            raise ValueError("Banner color can't be transparent, provide a color value.")
        
        self.page = page
        self.parent_frame = parent
        self.canvas_color = overlay_color
        self.created = False

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

            if self.created == False:
                self.page.Page_update_manager(update_with_extend = False)
                self.created = True
            #? all pages updates are called from the tab_frame_page when updates occur

    def page_function_calls(self):
        self.page.starting_call_list.append(self.init)
        self.page.updating_call_list.append(self.update_widget)

