import customtkinter as ctk
import numpy as np
from collections import defaultdict

from .Core import userChest as Chest
from .Theme import theme
from .utils import hvr_clr_g
from .Page_base_model import TileConfig

class GridLayoutEditor:
    def __init__(self, parent:ctk.CTkFrame, rows: int, columns: int, gap: int):
        self.parent = parent
        self.req_rows:int = rows
        self.req_columns:int = columns
        self.gap = gap

        self.layout_spawned:bool = False
        self.grid_placeholders: list[list[ctk.CTkFrame]] = []       #? holds the small cells that the user can hover and click to create the page frames.
        self.pConfig_attached = None                                #? holds the reference of the frame attached to the mouse cursor while creating a new page frame.
        self.start, self.end = None, None                           #? holds the start and end cell coordinates of the current selection in (row, column) format.
        self.started_selection = False                              #? becomes true when the user clicks the first cell to start a selection, and becomes false when the user deletes all page frames.

        self.rows_minsize: np.ndarray           #? holds the minimum size of each row as set by the user (0 if not set).
        self.cols_minsize: np.ndarray           #? holds the minimum size of each column as set by the user (0 if not set).
        self.grid_map: np.ndarray               #? a 2D boolean array that holds the state of each cell in the grid (True if occupied by a page frame, False if empty). This is used to prevent overlapping frames and to manage the layout state.

        self._rows = defaultdict(set)   #? holds the frames' references in each row
        self._cols = defaultdict(set)   #? holds the frames' references in each column
        #? ^^^^ to get all the result widgets created regardless of row/column use `set().union(*self._rows.values())`

    def start_grid(self):  #? Temp widget to enter the grid size to be replaced later with a better solution
        if not self.layout_spawned:
            self._process_cells()

            max_rows = 10
            max_cols = 10
            self.rows_slider_frame    = ctk.CTkFrame(self.parent, fg_color=theme.Csec, bg_color=theme.Csec, corner_radius=0)
            self.columns_slider_frame = ctk.CTkFrame(self.parent, fg_color=theme.Csec, bg_color=theme.Csec, corner_radius=0)
            self.rows_label     = ctk.CTkLabel(self.rows_slider_frame, fg_color=theme.Csec, text=f"{self.req_rows}", width=30, height=30)
            self.rows_slider    = ctk.CTkSlider(self.rows_slider_frame, fg_color=theme.Cbg, button_color=theme.Caccent, button_hover_color=hvr_clr_g(theme.Caccent, "ld"), from_=1, to=max_rows, number_of_steps=max_rows-1, command=lambda value: self._slider_cmd(value, "req_rows", self.rows_label), orientation="vertical")
            self.columns_label  = ctk.CTkLabel(self.columns_slider_frame, fg_color=theme.Csec, text=f"{self.req_columns}", width=30, height=30)
            self.columns_slider = ctk.CTkSlider(self.columns_slider_frame, fg_color=theme.Cbg, button_color=theme.Caccent, button_hover_color=hvr_clr_g(theme.Caccent, "ld"), from_=1, to=max_cols, number_of_steps=max_cols-1, command=lambda value: self._slider_cmd(value, "req_columns", self.columns_label))
            self.rows_slider.pack(pady=(10, 0))
            self.rows_label.pack()
            self.columns_label.pack(side="left")
            self.columns_slider.pack(side="left", padx=(0, 10))

        self.rows_slider.set(self.req_rows)
        self.columns_slider.set(self.req_columns)
        self.rows_slider_frame.place(relx=0.0125, rely=0.5, anchor="w")
        self.columns_slider_frame.place(relx=0.5, rely=0.0125, anchor="n")

    def _slider_cmd(self, value:int, attr:int, label:ctk.CTkLabel):
        value = int(value)
        label.configure(text=f"{value}")
        setattr(self, attr, value)

        #? spawn hoverable_frames
        self._process_cells()

        self.rows_slider_frame.lift()
        self.columns_slider_frame.lift()

    def _process_cells(self) -> None:
        old_rows = len(self.grid_placeholders)
        old_cols = len(self.grid_placeholders[0]) if old_rows else 0
        new_rows = self.req_rows
        new_cols = self.req_columns

        #? shrink rows ##########
        if new_rows < old_rows:
            for r in range(new_rows, old_rows):
                self.parent.grid_rowconfigure(r, weight=0, minsize=0, uniform="")
                for cell_btn in self.grid_placeholders[r]:
                    cell_btn.destroy()
            del self.grid_placeholders[new_rows:]

        #? shrink cols ##########
        if new_cols < old_cols:
            for c in range(new_cols, old_cols):
                self.parent.grid_columnconfigure(c, weight=0, minsize=0, uniform="")
            for row in self.grid_placeholders:
                for cell_btn in row[new_cols:]:
                    cell_btn.destroy()
                del row[new_cols:]

        #? grow rows ##########
        if new_rows > old_rows:
            self.parent.grid_rowconfigure(tuple(range(old_rows, new_rows)), weight=1, uniform="rows")
            for r in range(old_rows, new_rows):
                self.grid_placeholders.append([self._cell_frame(r, c) for c in range(new_cols)])

        #? grow cols ##########
        if new_cols > old_cols:
            self.parent.grid_columnconfigure(tuple(range(old_cols, new_cols)), weight=1, uniform="cols")
            for r in range(min(old_rows, new_rows)):
                for c in range(old_cols, new_cols):
                    self.grid_placeholders[r].append(self._cell_frame(r, c))

    def _cell_frame(self, r: int, c: int) -> ctk.CTkFrame:
        cell_btn = ctk.CTkFrame(self.parent, width=1, height=1, fg_color=theme.Cbg, bg_color=theme.Cbg, corner_radius=0)    #? width/height are set to 1. because grid can only shrink to the largest frame size only (why we set all frame sizes to 1)
        cell_btn.bind("<Enter>",    lambda e, p=cell_btn, row=r, col=c: self._enter_callback(p, row, col))
        cell_btn.bind("<Leave>",    lambda e, p=cell_btn, row=r, col=c: self._leave_callback(p, row, col))
        cell_btn.bind("<Button-1>", lambda e, row=r, col=c:       self._btn_1_callback(row, col))
        cell_btn.grid(row=r, column=c, sticky="nsew", padx=self.gap//2, pady=self.gap//2)
        return cell_btn

    def _has_conflict(self, row, col, rowspan, colspan) -> bool:
        return self.grid_map[row:row+rowspan, col:col+colspan].any()

    def _enter_callback(self, frame:ctk.CTkFrame, r: int, c: int):
        if self.pConfig_attached is not None:
            start_row, start_col = min(r, self.start[0]), min(c, self.start[1])
            rowspan, colspan = abs(r - self.start[0]) + 1, abs(c - self.start[1]) + 1

            if not self._has_conflict(start_row, start_col, rowspan, colspan):
                self.pConfig_attached.grid(
                    row=start_row, column=start_col,
                    rowspan=rowspan, columnspan=colspan,
                    sticky="nsew", padx=self.gap//2, pady=self.gap//2
                )

        frame.configure(fg_color=hvr_clr_g(theme.Cbg, "ld"))

    def _leave_callback(self, frame:ctk.CTkFrame, r: int, c: int):
        # print(f"Left cell ({r}, {c})")
        if (r,c) != self.start:
            frame.configure(fg_color=theme.Cbg)

    def _get_info(self, widget):                                            #? helper method
        info = widget.grid_info()
        return (int(info["row"]), int(info["column"]),
                int(info["rowspan"]), int(info["columnspan"])) if info else None

    def _stamp(self, row, col, rowspan, colspan, value: bool):              #? helper method
        self.grid_map[row:row+rowspan, col:col+colspan] = value

    def _btn_1_callback(self, r: int, c: int):
        if not self.started_selection:
            self.started_selection = True
            self.rows_slider_frame.place_forget()
            self.columns_slider_frame.place_forget()
            self.rows_minsize = np.zeros(self.req_rows, dtype=np.int16)
            self.cols_minsize = np.zeros(self.req_columns, dtype=np.int16)
            self.grid_map = np.zeros((self.req_rows, self.req_columns), dtype=bool)
        # print(f"Cell ({r}, {c}) callback executed")
        if self.pConfig_attached is None:
            page_config_frame = ctk.CTkFrame(self.parent, width=1, height=1, fg_color=theme.Cbg)    #? width/height are set to 1. because grid can only shrink to the largest frame size only (why we set all frame sizes to 1)
            page_config_frame.tile_expandable = True     #? True if we want the weigth to be 1 and false for 0 (fixed)
            page_config_frame.grid_state_frame = ctk.CTkFrame(page_config_frame, fg_color="transparent")
            page_config_frame.grid_state_label = ctk.CTkLabel(page_config_frame.grid_state_frame, fg_color="transparent", text="Expandable", font=(theme.font_B, 20))
            page_config_frame.grid_state_entryW = ctk.CTkEntry(page_config_frame.grid_state_frame, fg_color=theme.Cbg, placeholder_text="width", width=50)
            page_config_frame.grid_state_entryW.bind("<Return>", self._entry_return_cb, add="+")
            page_config_frame.grid_state_entryH = ctk.CTkEntry(page_config_frame.grid_state_frame, fg_color=theme.Cbg, placeholder_text="Height", width=50)
            page_config_frame.grid_state_entryH.bind("<Return>", self._entry_return_cb, add="+")
            page_config_frame.grid(row=r, column=c, sticky="nsew", padx=self.gap//2, pady=self.gap//2)
            page_config_frame.lower(self.grid_placeholders[0][0])
            self.pConfig_attached = page_config_frame
            self.start = (r, c)
        else:
            self.end = (r, c)
            new = self._get_info(self.pConfig_attached)
            if new: self._stamp(*new, value=True)

            self.pConfig_attached.grid_configure(
                padx = (self.gap//2 if new[1]!=0 else 0, self.gap//2 if new[1]+new[3]!=self.req_columns else 0),
                pady = (self.gap//2 if new[0]!=0 else 0, self.gap//2 if new[0]+new[2]!=self.req_rows else 0)
            )
            self.pConfig_attached.lift()
            self.pConfig_attached.grid_state_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.pConfig_attached.grid_state_label.pack(side="left", padx=(10, 10))
            self.pConfig_attached.configure(fg_color=theme.Csec)

            self._rows[new[0]].add(self.pConfig_attached); self._cols[new[1]].add(self.pConfig_attached)
            self.pConfig_attached.tile_span = (new[2], new[3])   #? (rowspan, columnspan)

            self.pConfig_attached.bind("<Button-1>", lambda e, tile=self.pConfig_attached: self._toggle_tile(tile))
            self.pConfig_attached.grid_state_label.bind("<Button-1>", lambda e, tile=self.pConfig_attached: self._toggle_tile(tile))
            self.pConfig_attached.bind("<Button-3>", lambda e, tile=self.pConfig_attached: self._destroy_tile(tile))
            self.pConfig_attached.grid_state_label.bind("<Button-3>", lambda e, tile=self.pConfig_attached: self._destroy_tile(tile))

            self.grid_placeholders[self.start[0]][self.start[1]].configure(fg_color=theme.Cbg)

            self.pConfig_attached = None
            self.start, self.end = None, None

    def _toggle_tile(self, tile):   #? on left click
        row, col, rowspan, colspan = self._get_info(tile)
        if tile.tile_expandable:  #? if it was expandable make it fixed
            tile.tile_expandable = False
            tile.grid_state_entryW.pack(before=tile.grid_state_label, side="left")
            tile.grid_state_label.configure(text="x")
            tile.grid_state_entryH.pack(side="right")
            tile.grid_propagate(False)
            tile.pack_propagate(False)
            if rowspan > 1:
                tile.grid_state_entryH.configure(state="disabled", fg_color=theme.Csec)
            else:
                if self.rows_minsize[row]:
                    tile.grid_state_entryH.delete(0, "end")
                    tile.grid_state_entryH.insert(0, int(self.rows_minsize[row]*Chest.scaleFactor))
                    tile.configure(height=self.rows_minsize[row])
                else:
                    tile.grid_state_entryH.delete(0, "end")
                    tile.grid_state_entryH._entry_focus_out()
                    tile.configure(height=1)

            if colspan > 1:
                tile.grid_state_entryW.configure(state="disabled", fg_color=theme.Csec)
            else:
                if self.cols_minsize[col]:
                    tile.grid_state_entryW.delete(0, "end")
                    tile.grid_state_entryW.insert(0, int(self.cols_minsize[col]*Chest.scaleFactor))
                    tile.configure(width=self.cols_minsize[col])
                else:
                    tile.grid_state_entryW.delete(0, "end")
                    tile.grid_state_entryW._entry_focus_out()
                    tile.configure(width=1)


        else:                           #? if it was fixed make it expandable
            tile.tile_expandable = True
            tile.grid_state_label.configure(text="Expandable")
            tile.grid_state_entryW.pack_forget()
            tile.grid_state_entryH.pack_forget()
            tile.grid_propagate(True)
            tile.pack_propagate(True)
            tile.configure(width=1, height=1)

            #? when switching to expandable - reset the row/column if there are no other fixed frames in the same row/column
            if all(t.tile_expandable for t in self._rows[row] if t.tile_span[0] == 1):
                self.rows_minsize[row] = 0
                self.parent.grid_rowconfigure(row, weight=1, minsize=0, uniform="rows")
            if all(t.tile_expandable for t in self._cols[col] if t.tile_span[1] == 1):
                self.cols_minsize[col] = 0
                self.parent.grid_columnconfigure(col, weight=1, minsize=0, uniform="cols")


    def _entry_return_cb(self, event):
        value = event.widget.get()
        event_entry:ctk.CTkLabel = event.widget.master
        placeholder_txt = event_entry.cget("placeholder_text")
        event_frame:ctk.CTkFrame = event_entry.master.master
        row, col, rowspan, colspan = self._get_info(event_frame)
        # print(f"Entry focus out with value: '{value}'")

        if value.isdigit():
            value = int(value)/Chest.scaleFactor
            if placeholder_txt == "width":
                self.cols_minsize[col] = value
                self.parent.grid_columnconfigure(col, weight=0, minsize=value, uniform="")
                for frame in self._cols[col]:    #? modify all the frames in the same column (if applicable)
                    if frame.tile_span[1] == 1:
                        frame.configure(width=value)
                        frame.grid_state_entryW.delete(0, "end")
                        frame.grid_state_entryW.insert(0, int(value*Chest.scaleFactor))
            elif placeholder_txt == "Height":
                self.rows_minsize[row] = value
                self.parent.grid_rowconfigure(row, weight=0, minsize=value, uniform="")
                for frame in self._rows[row]:    #? modify all the frames in the same row (if applicable)
                    if frame.tile_span[0] == 1:
                        frame.configure(height=value)
                        frame.grid_state_entryH.delete(0, "end")
                        frame.grid_state_entryH.insert(0, int(value*Chest.scaleFactor))

        elif value in ("width", "Height", ""):  #? reset to default (weight=1, minsize=0), (cols_minsize =0, rows_minsize=0) if there are no other frames in the same row/column with a fixed size.
            if placeholder_txt == "width":
                list_to_check = self._cols[col]
                span_idx = 1
            else:
                list_to_check = self._rows[row]
                span_idx = 0
            to_adjust = []
            for frame in list_to_check:
                if not frame.tile_expandable and frame.tile_span[span_idx] == 1:
                    to_adjust.append(frame)
            if len(to_adjust) == 1:
                if placeholder_txt == "width":
                    self.cols_minsize[col] = 0
                    self.parent.grid_columnconfigure(col, weight=1, minsize=0, uniform="cols")
                else:
                    self.rows_minsize[row] = 0
                    self.parent.grid_rowconfigure(row, weight=1, minsize=0, uniform="rows")

        else:
            if placeholder_txt == "width":
                event_frame.grid_state_entryW.delete(0, "end")
            elif placeholder_txt == "Height":
                event_frame.grid_state_entryH.delete(0, "end")

    def _destroy_tile(self, tile):
        to_remove = self._get_info(tile)
        if to_remove: self._stamp(*to_remove, value=False)
        row, col = to_remove[0], to_remove[1]
        tile.destroy()
        self._rows[row].remove(tile); self._cols[col].remove(tile)

        if not self._rows[row]:    #? if all the frames in the same row are destroyed reset the row to default (weight=1, minsize=0)
            del self._rows[row]
            self.parent.grid_rowconfigure(row, weight=1, minsize=0, uniform="rows")
            self.rows_minsize[row] = 0
        if not self._cols[col]:   #? if all the frames in the same column are destroyed reset the column to default (weight=1, minsize=0)
            del self._cols[col]
            self.parent.grid_columnconfigure(col, weight=1, minsize=0, uniform="cols")
            self.cols_minsize[col] = 0

        if not self._rows: # to get all the result tiles
            self.started_selection = False
            self.rows_slider_frame.place(relx=0.0125, rely=0.5, anchor="w")
            self.columns_slider_frame.place(relx=0.5, rely=0.0125, anchor="n")

    #^ Stage 2: ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

    def tiles_assignment_UI(self, p_names:list["str"]=None):
        label_text_placeholder = "Which Page?"
        tiles = set().union(*self._rows.values())
        if p_names is None:
            self.assigned_names = list(range(len(tiles)))   #? if no page names are provided, use numbers as placeholders (up to the number of created tiles)
        else:
            self.assigned_names = p_names
        for tile in tiles:
            tile.grid_state_entryW.pack_forget()
            tile.grid_state_entryH.pack_forget()
            tile.grid_state_label.configure(text=label_text_placeholder)

            tile.unbind("<Button-1>"); tile.grid_state_label.unbind("<Button-1>")
            tile.unbind("<Button-3>"); tile.grid_state_label.unbind("<Button-3>")
            btn_1_cmd = lambda e, t=tile: self._switch_assigned_name__btn1(e, t)
            tile.bind("<Button-1>", btn_1_cmd)
            tile.grid_state_label.bind("<Button-1>", btn_1_cmd)

    def _switch_assigned_name__btn1(self, event, tile):   #? on left click
        if self.assigned_names:
            current_text = tile.grid_state_label.cget("text")
            if current_text not in self.assigned_names:
                self.assigned_names.append(current_text)
            tile.grid_state_label.configure(text=self.assigned_names.pop(0))

    def confirm_layout(self):
        tiles = {}
        for tile in set().union(*self._rows.values()):
            tile.unbind("<Button-1>"); tile.grid_state_label.unbind("<Button-1>")
            tile.grid_state_frame.place_forget()
            tiles[tile.grid_state_label.cget("text")]=tile

        return tiles

    def save_layout(self):
        layout_state = {
            "grid": (self.req_rows, self.req_columns, self.gap),
            "tiles": {}
        }
        for tile in set().union(*self._rows.values()):
            page_name = tile.grid_state_label.cget("text")
            if page_name not in self.assigned_names:    #? at this stage any name still inside `self.assigned_names` is a page that wasn't assigned to any tile
                tile_info = self._get_info(tile)
                if not tile.tile_expandable:
                    width = tile.cget('width'); height = tile.cget('height')
                else:
                    width = height = 1
                layout_state["tiles"][page_name] = TileConfig(*tile_info, tile.tile_expandable, width, height)
        return layout_state

    def load_layout(self, layout_state):
        self.req_rows = layout_state["grid"][0]
        self.req_columns = layout_state["grid"][1]
        self.gap = layout_state["grid"][2]
        self.parent.grid_rowconfigure(list(range(self.req_rows)), weight=1, uniform="rows")
        self.parent.grid_columnconfigure(list(range(self.req_columns)), weight=1, uniform="cols")

        tiles = {}
        for tile_name, tile_state in layout_state["tiles"].items():
            tile_state: "TileConfig"
            tile = ctk.CTkFrame(self.parent, width=1, height=1, fg_color=theme.Cbg)    #? width/height are set to 1. because grid can only shrink to the largest frame size only (why we set all frame sizes to 1)
            tile.grid(row=tile_state.row, column=tile_state.column, rowspan=tile_state.rowspan, columnspan=tile_state.columnspan, sticky="nsew",
                        padx = (self.gap//2 if tile_state.column!=0 else 0, self.gap//2 if tile_state.column+tile_state.columnspan!=self.req_columns else 0),
                        pady = (self.gap//2 if tile_state.row!=0 else 0, self.gap//2 if tile_state.row+tile_state.rowspan!=self.req_rows else 0))
            if not tile_state.expandable:
                tile.tile_expandable = False
                tile.fixed_width = False
                tile.fixed_height = False
                if tile_state.width != 1:
                    self.parent.grid_columnconfigure(tile_state.column, weight=0, minsize=tile_state.width, uniform="")
                    tile.configure(width=tile_state.width)
                    tile.fixed_width = True
                if tile_state.height != 1:
                    self.parent.grid_rowconfigure(tile_state.row, weight=0, minsize=tile_state.height, uniform="")
                    tile.configure(height=tile_state.height)
                    tile.fixed_height = True
                tile.grid_propagate(False)
                tile.pack_propagate(False)
            else:
                tile.tile_expandable = True
                tile.fixed_width = False
                tile.fixed_height = False

            tiles[tile_name]=tile

        return tiles


#? how to use grid layout:
"""
# --- FIXED GRID CONFIGURATION ---
# 1. Use weight=0 to prevent the track from growing or shrinking.
# 2. Use minsize to define the strict pixel width/height.
parent.grid_columnconfigure(index=1, weight=0, minsize=50)

# --- FIXED WIDGET PLACEMENT ---
# 1. Use sticky="nsew" so the widget stretches to the minsize of the track.
# 2. Set the physical width/height in the widget constructor.
# 3. Use grid_propagate(False) on the widget if you want to prevent
#    internal children from "pushing" the fixed size larger.
fixed_frame = ctk.CTkFrame(parent, width=50)
fixed_frame.grid(row=0, column=1, sticky="nsew")
fixed_frame.grid_propagate(False)

-----------------------------------------------------------------------------

# --- VARIABLE GRID CONFIGURATION ---
# 1. Use weight=1 (or higher) to tell the track to absorb extra space.
# 2. Usually keep minsize=0 so it can shrink as small as the window allows.
parent.grid_columnconfigure(index=0, weight=1)

# --- VARIABLE WIDGET PLACEMENT ---
# 1. Use sticky="nsew" to ensure the widget follows the expanding grid walls.
# 2. You don't need to set a width in the constructor; the grid will decide it.
variable_frame = ctk.CTkFrame(parent)
variable_frame.grid(row=0, column=0, sticky="nsew")
"""
