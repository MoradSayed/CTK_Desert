import customtkinter as ctk
from CTK_Desert.Page_base_model import Page_BM
from CTK_Desert.Core import userChest as Chest

#* Don't pack Self.frame
class CUNAME__C(Page_BM):
    def __init__(self):
        super().__init__(scrollable="SCRL_VAL__")
        self.frame = self.Scrollable_frame      # Parent of all children in this page


    def tool_menu(self):
        self.tools_f = ctk.CTkFrame(Chest.toolsFrame, fg_color="transparent")

        return self.tools_f

