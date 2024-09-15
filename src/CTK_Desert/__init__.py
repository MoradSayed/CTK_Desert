import json, os, inspect
import customtkinter as ctk
import socket
import threading, time
from .Core import userChest as Chest
if Chest._OS == "Windows":
    from ctypes import byref, c_int, sizeof, windll 
# elif Chest._OS == "Linux":
#     pass    #! to be implemented
# elif Chest._OS == "Darwin":
#     pass    #! to be implemented
from .Theme import theme

class Desert(ctk.CTk):
    def __init__ (self, assets_dir, page_choise=None, spin=True, reload_on_save=False):
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module is not None:
            if os.path.samefile(os.path.dirname(os.path.abspath(caller_module.__file__)), os.getcwd()):
                pass                        
            else:
                os.chdir(os.path.dirname(os.path.abspath(caller_module.__file__)))
                
        if os.path.isdir(assets_dir):
            Chest.userAssetsDirectory = assets_dir
        else:
            raise FileNotFoundError(f"Directory '{assets_dir}' not found")

        _path = os.path.join(assets_dir, "Images")
        if not os.path.exists(_path):
            os.mkdir(_path)
        _path = os.path.join(assets_dir, "Pages")
        if not os.path.exists(_path):
            os.mkdir(_path)
        _path = os.path.join(assets_dir, "preferences.json")
        if not os.path.isfile(_path):
            with open(os.path.join(os.path.dirname(__file__), 'preferences.json'), 'r') as f:
                pref_data = json.load(f)
            with open(_path, 'w') as f:
                json.dump(pref_data, f, indent=4)
        _path = None

        theme.load()
        super().__init__(fg_color= theme.Cbg)
        
        # if Chest._OS == "Linux":    # windows and macos are able to scale themself properly
        #     ctk.set_widget_scaling(1.35)
        #     ctk.set_window_scaling(1.0)
        self.title("")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scaleFactor = Chest.scaleFactor
        window_width = int(960*scaleFactor)
        window_height = int(640*scaleFactor)
        self.geometry(f'{window_width}x{window_height}+{int((screen_width*scaleFactor/2)-(window_width*scaleFactor/2))}+{int((screen_height*scaleFactor/2)-(window_height*scaleFactor/2))}') #1.5 for the window scale (150%)
        self.minsize(screen_width/2, screen_height/2)
        try:
            self.iconbitmap(os.path.join(os.path.dirname(__file__), "images/empty.ico"))
        except:
            pass

        self.App_Theme = Chest.Get_Prefered_Theme_Mode()
        ctk.set_appearance_mode(f'{self.App_Theme}')
        if self.App_Theme == "system":
            self.App_Theme = ctk.get_appearance_mode()
        self.title_bar_color(theme.TB_hex_clrs[f"{self.App_Theme.lower()}"]) #change the title bar color
        
        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())     #? to focus on the widget that was clicked on
        from .Tab_Page_Frame import Frame
        self.Home = Frame(self, usr_assets_dir=assets_dir, page_choise=page_choise)
        
        if reload_on_save:
            server_thread = threading.Thread(target=self.server_thread, daemon=True)
            server_thread.start()
        if spin:
            self.mainloop()

    def title_bar_color(self, color):
        if Chest._OS == "Windows":
            windll.dwmapi.DwmSetWindowAttribute(
                windll.user32.GetParent(self.winfo_id()), 
                35, 
                byref(c_int(color)), 
                sizeof(c_int)
                )
        # else:   #! for linux and mac (to be implemented)
        #     pass

        """
        #^ Remove the title bar
        #! will need to edit the Dialog widgit and edit the Frame layout
        # # Constants from the Windows API
        # GWL_STYLE = -16
        # WS_CAPTION = 0x00C00000
        # WS_SYSMENU = 0x80000

        # hwnd = windll.user32.GetParent(self.winfo_id())
        # current_style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        # new_style = current_style & ~WS_CAPTION & ~WS_SYSMENU
        # windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
        # windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x27)  # Update the window to apply the changes
        """
        
    def server_thread(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(('localhost', 4831))
            server.listen()
            while True:
                # print("waiting for data")
                client_socket, addr = server.accept()   # this is a blocking function
                # print("got data")
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    Chest.thread_reload_var.set(data)
