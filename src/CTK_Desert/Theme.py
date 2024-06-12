LIGHT_MODE = {
    'text'              : "#030303", 
    'background'        : "#ebebeb", 
    'primary'           : "#a3a3a3", 
    'secondary'         : "#d4d4d4", 
    'accent'            : "#61bdab",
    'warning'           : "#ca4a51"
}

DARK_MODE = {
    'text'              : "#ebebeb", 
    'background'        : "#030303", 
    'primary'           : "#3d3d3d", 
    'secondary'         : "#080808", 
    'accent'            : "#25a188",
    'warning'           : "#b83135"
}

ICONS = {
    "_d_s"              : (77, 201, 176)    ,  
    "_d"                : (179, 179, 179)   ,  
    "_l_s"              : (57, 149, 131)    ,  
    "_l"                : (76, 76, 76)  
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