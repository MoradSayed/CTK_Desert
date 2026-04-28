import customtkinter as ctk

class Binder:
    def __init__(self, window):
        self.window = window
        self._callbacks: dict[str,list] = {}

        self._register("<MouseWheel>")
        self._register("<Button-1>")

    def _register(self, event):
        self._callbacks[event] = []
        self.window.bind_all(event, lambda e: self._dispatch(event, e), add="+")

    def _dispatch(self, event, tk_event):
        callbacks = self._callbacks[event]
        if not callbacks:
            # print(f"[Binder] Warning: no callbacks registered for '{event}'. If intentional, ignore this.")
            return
        if len(callbacks) == 1:
            callbacks[0](tk_event)
            return
        for fn in callbacks:
            fn(tk_event)

    def bind(self, event, callback):
        self._callbacks[event].append(callback)

    def unbind(self, event, callback):
        try:
            self._callbacks[event].remove(callback)
        except ValueError: pass