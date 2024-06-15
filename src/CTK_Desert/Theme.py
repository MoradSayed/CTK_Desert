from .utils import change_pixel_color
import os
import pathlib
file_dir = pathlib.Path(__file__).parent.resolve()

LIGHT_MODE = {
    'text'              : "#030303", 
    'background'        : "#ebebeb", 
    'primary'           : "#a3a3a3", 
    'secondary'         : "#d4d4d4", 
    'accent'            : "#61bdab",

    "success"           : "#28a745",
    "danger"            : "#dc3545",
    "warning"           : "#fd7e14",
    "info"              : "#007bff",
    "pending"           : "#ffc107"
}

DARK_MODE = {
    'text'              : "#ebebeb", 
    'background'        : "#030303", 
    'primary'           : "#3d3d3d", 
    'secondary'         : "#080808", 
    'accent'            : "#25a188",

    "success"           : "#1c7430",
    "danger"            : "#a71d2a",
    "warning"           : "#d96b06",
    "info"              : "#0056b3",
    "pending"           : "#d39e00"
}

ICONS = {
    "_d_s"              : (77, 201, 176)    ,  
    "_d"                : (179, 179, 179)   ,  
    "_l_s"              : (57, 149, 131)    ,  
    "_l"                : (76, 76, 76)      ,

    "success"           : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-success-48.png")   , f'{LIGHT_MODE["success"]}+{DARK_MODE["success"]}' , return_img=True),
    "danger"            : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-danger-48.png")    , f'{LIGHT_MODE["danger"]}+{DARK_MODE["danger"]}'   , return_img=True),
    "warning"           : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-warning-48.png")   , f'{LIGHT_MODE["warning"]}+{DARK_MODE["warning"]}' , return_img=True),
    "info"              : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-info-48.png")      , f'{LIGHT_MODE["info"]}+{DARK_MODE["info"]}'       , return_img=True),
    "pending"           : lambda: change_pixel_color(os.path.join(file_dir, "images\Icons\icons8-pending-48.png")   , f'{LIGHT_MODE["pending"]}+{DARK_MODE["pending"]}' , return_img=True)
}

def hex_to_0x(hexcolor):
    color = '0x00'
    for i in range(7,0,-2):
        h = hexcolor[i:i+2]
        color = color+h
    return int(color, 16)

TITLE_BAR_HEX_COLORS = {
    "light" : hex_to_0x(LIGHT_MODE['background']),
    "dark"  : hex_to_0x(DARK_MODE['background'])
}

FONT    = "Space Mono"
FONT_B  = "Space Mono Bold"
FONT_I  = "Space Mono Italic"
FONT_BI = "Space Mono Bold Italic" 