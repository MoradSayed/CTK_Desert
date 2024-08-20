from .utils import change_pixel_color
import os, pathlib, json
from typing import Tuple

file_dir = pathlib.Path(__file__).parent.resolve()

# LIGHT_MODE = {
#     'text'              : "#030303", 
#     'background'        : "#ebebeb", 
#     'primary'           : "#a3a3a3", 
#     'secondary'         : "#d4d4d4", 
#     'accent'            : "#61bdab",

#     "success"           : "#28a745",
#     "danger"            : "#dc3545",
#     "warning"           : "#fd7e14",
#     "info"              : "#007bff",
#     "pending"           : "#ffc107"
# }

# DARK_MODE = {
#     'text'              : "#ebebeb", 
#     'background'        : "#030303", 
#     'primary'           : "#3d3d3d", 
#     'secondary'         : "#080808", 
#     'accent'            : "#25a188",

#     "success"           : "#1c7430",
#     "danger"            : "#a71d2a",
#     "warning"           : "#d96b06",
#     "info"              : "#0056b3",
#     "pending"           : "#d39e00"
# }

# ICONS = {
#     "_d_s"              : (77, 201, 176)    ,  
#     "_d"                : (179, 179, 179)   ,  
#     "_l_s"              : (57, 149, 131)    ,  
#     "_l"                : (76, 76, 76)      ,

#     "success"           : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-success-48.png")   , f'{LIGHT_MODE["success"]}+{DARK_MODE["success"]}' , return_img=True),
#     "danger"            : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-danger-48.png")    , f'{LIGHT_MODE["danger"]}+{DARK_MODE["danger"]}'   , return_img=True),
#     "warning"           : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-warning-48.png")   , f'{LIGHT_MODE["warning"]}+{DARK_MODE["warning"]}' , return_img=True),
#     "info"              : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-info-48.png")      , f'{LIGHT_MODE["info"]}+{DARK_MODE["info"]}'       , return_img=True),
#     "pending"           : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-pending-48.png")   , f'{LIGHT_MODE["pending"]}+{DARK_MODE["pending"]}' , return_img=True)
# }

# def hex_to_0x(hexcolor):
#     color = '0x00'
#     for i in range(7,0,-2):
#         h = hexcolor[i:i+2]
#         color = color+h
#     return int(color, 16)

# TITLE_BAR_HEX_COLORS = {
#     "light" : hex_to_0x(LIGHT_MODE['background']),
#     "dark"  : hex_to_0x(DARK_MODE['background'])
# }

# FONT    = "Space Mono"
# FONT_B  = "Space Mono Bold"
# FONT_I  = "Space Mono Italic"
# FONT_BI = "Space Mono Bold Italic" 

class Theme:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Theme, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._initialized = True

            self.Ctxt      : Tuple[str, str] 
            self.Cbg       : Tuple[str, str] 
            self.Cpri      : Tuple[str, str] 
            self.Csec      : Tuple[str, str] 
            self.Caccent   : Tuple[str, str] 
            self.Csuccess  : Tuple[str, str] 
            self.Cdanger   : Tuple[str, str] 
            self.Cwarning  : Tuple[str, str] 
            self.Cinfo     : Tuple[str, str] 
            self.Cpending  : Tuple[str, str] 
            self.icon_norm : Tuple[str, str]
            self.icon_sel  : Tuple[str, str]
            
            self.font    : str
            self.font_B  : str
            self.font_I  : str
            self.font_BI : str

    def load(self):
        from .Core import userChest as Chest
        with open(os.path.join(Chest.userAssetsDirectory, 'preferences.json'), 'r') as f:
            pref_data = json.load(f)
        theme_dict = pref_data["theme"]
        
        default_theme = theme_dict["default_theme"]
        themes = theme_dict['themes'][0]
        self.available_themes = [theme for theme in themes]
        theme_data = themes[default_theme]
        for key, value in theme_data.items():
            name = f"icon{key}" if key.startswith("_") else f"C{key}"
            setattr(self, name, tuple(value))

        default_font = theme_dict["default_font"]
        self.available_fonts = [font for font in theme_dict['fonts'][0]]
        font_data = theme_dict['fonts'][0][default_font]
        for key, value in font_data.items():
            setattr(self, key, value)

        self.success_icon   = self._get_icon("success")
        self.danger_icon    = self._get_icon("danger")
        self.warning_icon   = self._get_icon("warning")
        self.info_icon      = self._get_icon("info")
        self.pending_icon   = self._get_icon("pending")

        self.TB_hex_clrs = {
            "light" : self._hex_to_0x(self.Cbg[0]),
            "dark"  : self._hex_to_0x(self.Cbg[1])
        }

    def _get_icon(self, icon_name):
        clr = getattr(self, f"C{icon_name}")
        icon = change_pixel_color(os.path.join(file_dir, f"images\Icons\icons8-{icon_name}-48.png"), clr, return_img=True)
        return icon

    def _hex_to_0x(self, hexcolor):
        color = '0x00'
        for i in range(7,0,-2):
            h = hexcolor[i:i+2]
            color = color+h
        return int(color, 16)
    

theme: Theme = Theme()