from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from .Page_base_model import Tile_BM

import customtkinter as ctk
from .Core import userChest as Chest
from .Theme import theme
from .utils import hvr_clr_g

class Scrollbar(ctk.CTkFrame):
    def __init__(self, parent, page:"Tile_BM", color: tuple[str, str], command,
                 subpage_style: bool = True, side:Literal['e', 'w'] = 'e', auto_hide: bool = True):

        from .Notifications import Notifications
        self.notifier = Notifications()

        super().__init__(parent, width=10/Chest.scaleFactor, fg_color=color, bg_color=theme.Cbg)
        if subpage_style:
            self.configure(background_corner_colors=(color, theme.Cbg, color, color))

        self.parent = parent
        self.page = page
        self.color = color
        self.hover_color = hvr_clr_g(color, "ld")
        self._side = side
        self._auto_hide = auto_hide
        self._command = command
        self._mouse_bound = False
        self._subpage_style = subpage_style

        if self._auto_hide:
            if not self._subpage_style:
                self.notifier.create_message("Scrollbar auto_hide is Unavailable", "Can't use auto_hide with the current style\nUse the subpage style to enable auto hide", "x")
                self._auto_hide = False
            else:
                self.page.Scrollable_canvas.bind("<Enter>", self._enter_bind_cb, add="+")
                self.page.Scrollable_canvas.bind("<Leave>", self._leave_bind_cb, add="+")

        self.bind("<Enter>", lambda e: self.configure(fg_color=self.hover_color))
        self.bind("<Leave>", lambda e: self.configure(fg_color=color))
        if subpage_style:
            self.lift()
            if   self._side == "w": self._relx = 0.0
            elif self._side == "e": self._relx = 1.0
            else: raise ValueError("side must be 'e', or 'w'")
        else:
            self._side = ''
            self._relx = 0.5

        self._started = False
        page.starting_call_list.append(lambda: setattr(self, "_started", True))
        page.picking_call_list.append(self._restore_state)
        page.leaving_call_list.append(self._page_leaving)

        self._initial_y = None
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", lambda e: setattr(self, "_initial_y", None))

        self._placed: bool = False
        self._cursor_in_page: bool = False

        self._velocity = 0.0
        self._scrolling = False

    def set(self, start, end):
        if not self._started:
            return
        # print("scrollbar set called with ", start, end, "from", self.page.widget_str.split("!")[-1])

        self._start_value = float(start)
        self._end_value = float(end)
        self.rel_height = self._end_value - self._start_value

        if self.rel_height == 1.0:
            self._placed = False
            self._place_check()
            if self._mouse_bound:
                Chest.Binder.unbind("<MouseWheel>", self.scrolling_action)
                self._mouse_bound = False
            return

        if self._subpage_style:
            if self._start_value == 0.0: self.configure(background_corner_colors=(theme.Cbg if self._side == "w" else self.color, theme.Cbg if self._side == "e" else self.color, self.color, self.color))
            elif self._end_value == 1.0: self.configure(background_corner_colors=(self.color, self.color, theme.Cbg if self._side == "e" else self.color, theme.Cbg if self._side == "w" else self.color))
            else: self.configure(background_corner_colors=(self.color, self.color, self.color, self.color))
        self._placed = True
        self._place_check()
        if not self._mouse_bound:
            self._mouse_bound = True
            Chest.Binder.bind("<MouseWheel>", self.scrolling_action)

    def get(self):
        return self._start_value, self._end_value

    def _on_drag(self, event):
        if self._initial_y is None:
            self._initial_y = event.y
            self._parent_height = self.parent.winfo_height()
        self._start_value += (event.y - self._initial_y) / self._parent_height
        self._start_value = max(0.0, min(1.0 - self.rel_height, self._start_value))
        self._end_value = self._start_value + self.rel_height
        self.set(self._start_value, self._end_value)

        self._command("moveto", self._start_value)

    def _enter_bind_cb(self, event):
        # print(Chest.Binder._callbacks["<MouseWheel>"])
        self._cursor_in_page = True
        self._place_check()

    def _leave_bind_cb(self, event):
        self._cursor_in_page = False
        self._place_check()

    def _place_check(self):
        if self.page.opened and self._placed and (self._cursor_in_page or not self._auto_hide):
            self.place(relx=self._relx, rely=self._start_value, anchor="n"+self._side, relheight=self.rel_height)
        else:
            self.place_forget()

    def _restore_state(self):
        """Used to restore bind state on page pick"""
        if self._mouse_bound:
            Chest.Binder.bind("<MouseWheel>", self.scrolling_action)
        else:
            Chest.Binder.unbind("<MouseWheel>", self.scrolling_action)
        self._place_check()

    def _page_leaving(self):
        """Used to unbind mouse wheel when page is not displayed to prevent unnecessary event processing"""
        if self._mouse_bound:
            Chest.Binder.unbind("<MouseWheel>", self.scrolling_action)
            self.place_forget()

    def scrolling_action(self, event):
        if str(event.widget).startswith(self.page.widget_str+"."):
            self._velocity += -1 * (event.delta / 120) * 60     #? (-/+)1 * 60
            self._velocity = max(-200, min(200, self._velocity))
            if not self._scrolling:
                self._scrolling = True
                self._animate()

    def _animate(self):
        if abs(self._velocity) < 0.5:
            self._velocity = 0
            self._scrolling = False
            return
        self._command('scroll', int(self._velocity), "units")
        self._velocity *= 0.85
        self.after(16, self._animate)
