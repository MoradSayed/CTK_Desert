import customtkinter as ctk
from .Core import userChest as Chest
from .Page_base_model import Page_BM
from .Theme import *
from .utils import hvr_clr_g, color_finder
from .Widgits import C_Widgits
from .Theme import theme
import os
from PIL import Image
import numpy as np
from tkinter import filedialog as fd

# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class AddPage(Page_BM):
    def __init__(self):
        super().__init__(start_func=self.on_start, pick_func=self.on_pick, update_func=self.on_update, leave_func=self.on_leave)
        self.menu_page_frame = Chest.Manager
        self.frame = self.get_pf()
        self.mode = ctk.get_appearance_mode()
        self.frame_clr = color_finder(self.frame)
        self.pages_path = Chest.userPagesDirectory
        self.icon_names = ["_d_s", "_d", "_l_s", "_l"]
        self.icon_path = None
        self.add_menu_button(r"C:\Users\Morad\Downloads\icons8-reload-64.png", lambda: Chest.reload_page("Workspace.AddPage"))

        self.ws_label = ctk.CTkLabel(self.frame, text="New", font=(theme.font_B, 40))
        self.ws_label.pack(fill="x", padx=20, pady=20)

        self.c_wgts = C_Widgits(self, self.frame)
        
        self.content_sec = self.c_wgts.section(padx=60)
        self.page_name, self.page_nameVar = self.c_wgts.Entry_unit(self.content_sec, "Page Name", "Pick a name")
        self.icon_path_btn = self.c_wgts.Button_unit(self.content_sec, "Icon Path", "Pick an icon", self.get_icon_path)
        self.scrollableCB, self.scrollableCBVar = self.c_wgts.CheckBox_unit(self.content_sec, "Scrollable", True)

        self.confirmation_sec =    self.c_wgts.section(pady=5)
        self.confirmation     =    self.c_wgts.Button_unit(self.confirmation_sec, "", "Create Page", self.create_page, height=50, font=(theme.font_B, 17))
        self.Back             =    self.c_wgts.Button_unit(self.confirmation.master, "", "Back", lambda: Chest.Return_SubPage("Workspace", "AddPage"), True,
                                                           height=50, font=(theme.font_B, 17), fg_color=theme.Ctxt)

    def on_start(self):
        pass

    def on_pick(self):
        pass

    def on_update(self):
        pass

    def on_leave(self, event):
        return True
    
    def get_icon_path(self):
        filetypes = ( ('images', '*.png'), ('All files', '*.*') )
        f = fd.askopenfile(filetypes=filetypes, title="Pick an icon")
        self.icon_path = f.name if f else None

    def create_page(self):
        file_name = self.page_nameVar.get()         # get field data (page name)
        if not (file_name == "" or self.icon_path == None):

            with open (os.path.join(os.path.dirname(__file__), "Page_EX_Code.py"), 'r') as file:    # open the example code file
                data = file.read()
            #######################################################################
            data = data.replace("CUNAME__C", file_name)  
            
            # module_names = [file[:-3] for file in os.listdir(self.pages_path) if file.endswith('.py') and file != '__init__.py']       # replace the class name with the page name
            # data = data.replace('"PAGE_Num__": 0', f'"PAGE_Num__": {len(module_names)+1}')                                             # replace the class name with the page name

            data = data.replace(r'"SCRL_VAL__"', str(self.scrollableCBVar.get()))
            
            #######################################################################
            with open (os.path.join(self.pages_path, f"{file_name}.py"), 'w') as file:              # create a new file with the page name
                file.write(data)

            self.create_colored_icons(file_name) # get the image path from the dialog box, and the target color from Theme file

            self.menu_page_frame.new_page_constructor(file_name)        # Calling a func in the tab page frame to add the new page to the application
        
    def create_colored_icons(self, file_name):
        # Open the image and convert it to RGBA mode
        img = Image.open(self.icon_path).convert("RGBA")

        # Convert the image to a NumPy array
        img_array = np.array(img)

        for i in self.icon_names:
            # Apply the target color to non-transparent pixels
            img_array[img_array[..., 3] != 0, :3] = getattr(theme, f"icon_{'sel' if i.endswith('s') else 'norm'}")[0 if i.startswith("_l") else 1]  # ICONS[i]

            # Create a new image from the modified array
            modified_img = Image.fromarray(img_array, "RGBA")

            # Save the modified image
            modified_img.save(os.path.join(os.path.dirname(self.pages_path), "Images", f"{file_name.lower()}{i}.png"))
            
    