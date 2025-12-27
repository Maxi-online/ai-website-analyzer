# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Maxim Strekolovskiy

"""
Desktop application for analyzing and comparing websites.

Built for Windows using tkinter.
"""

import json
import os
import platform
import sys
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import filedialog
from tkinter import font as tkfont
from tkinter import messagebox, scrolledtext, ttk
from typing import Any, Callable, Dict, List, Optional

import requests
from settings import settings

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
WIN11_THEMES: Dict[str, Dict[str, str]] = {
    "win11_light": {
        "title": "Light theme",
        "window_bg": "#f3f3f3",
        "card_bg": "#ffffff",
        "border": "#d6d6d6",
        "foreground": "#0f0f0f",
        "muted": "#5f6368",
        "muted_alt": "#717171",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "success": "#0f9150",
        "error": "#dc2626",
        "warning": "#d97706",
        "control_bg": "#f7f7f7",
        "control_hover": "#e5e5e5",
        "entry_bg": "#ffffff",
        "editor_bg": "#ffffff",
        "tab_bg": "#eceff1",
        "tab_hover": "#e4e7eb",
        "tab_active": "#ffffff",
        "shadow": "#d0d0d0",
    },
    "win11_dark": {
        "title": "Dark theme",
        "window_bg": "#1f1f1f",
        "card_bg": "#252526",
        "border": "#303033",
        "foreground": "#f3f3f3",
        "muted": "#a0a0a0",
        "muted_alt": "#8a8a8a",
        "accent": "#4f8cff",
        "accent_hover": "#3a7bff",
        "success": "#22c55e",
        "error": "#f87171",
        "warning": "#fbbf24",
        "control_bg": "#2e2f33",
        "control_hover": "#3a3b40",
        "entry_bg": "#2e2f33",
        "editor_bg": "#1e1f23",
        "tab_bg": "#2b2d30",
        "tab_hover": "#32343a",
        "tab_active": "#1f1f1f",
        "shadow": "#181818",
    },
}

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class WinUIEffects:
    """Helpers for enabling Windows 11 Fluent UI effects."""

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWA_MICA_EFFECT = 1029
    SYSTEMBACKDROP_AUTO = 0
    SYSTEMBACKDROP_MICA = 2
    SYSTEMBACKDROP_ACRYLIC = 3

    @staticmethod
    def is_supported() -> bool:
        return sys.platform == "win32" and platform.release() >= "10"

    @staticmethod
    def enable_mica_effect(hwnd, dark: bool = False):
        if not WinUIEffects.is_supported():
            return
        try:
            dwmapi = ctypes.windll.dwmapi
            value = ctypes.c_int(WinUIEffects.SYSTEMBACKDROP_MICA)
            dwmapi.DwmSetWindowAttribute(
                hwnd,
                WinUIEffects.DWMWA_SYSTEMBACKDROP_TYPE,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
            dark_mode = ctypes.c_int(1 if dark else 0)
            dwmapi.DwmSetWindowAttribute(
                hwnd,
                WinUIEffects.DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(dark_mode),
                ctypes.sizeof(dark_mode),
            )
        except Exception:
            pass

    @staticmethod
    def enable_acrylic(hwnd, dark: bool = False):
        if not WinUIEffects.is_supported():
            return
        try:
            dwmapi = ctypes.windll.dwmapi
            accent_policy = ctypes.c_int(0)
            value = ctypes.c_int(WinUIEffects.SYSTEMBACKDROP_ACRYLIC)
            dwmapi.DwmSetWindowAttribute(
                hwnd,
                WinUIEffects.DWMWA_SYSTEMBACKDROP_TYPE,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
            dark_mode = ctypes.c_int(1 if dark else 0)
            dwmapi.DwmSetWindowAttribute(
                hwnd,
                WinUIEffects.DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(dark_mode),
                ctypes.sizeof(dark_mode),
            )
        except Exception:
            pass

    @staticmethod
    def set_immersive_border(hwnd):
        if not WinUIEffects.is_supported():
            return
        try:
            dwmapi = ctypes.windll.dwmapi
            value = ctypes.c_int(1)
            dwmapi.DwmSetWindowAttribute(
                hwnd,
                WinUIEffects.DWMWA_MICA_EFFECT,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
        except Exception:
            pass


class ColorUtils:
    """Helper utilities for working with colors."""

    @staticmethod
    def hex_to_rgb(value: str):
        value = value.lstrip("#")
        lv = len(value)
        return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))

    @staticmethod
    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % rgb

    @staticmethod
    def blend(color_a: str, color_b: str, alpha: float) -> str:
        r1, g1, b1 = ColorUtils.hex_to_rgb(color_a)
        r2, g2, b2 = ColorUtils.hex_to_rgb(color_b)
        r = int(r1 + (r2 - r1) * alpha)
        g = int(g1 + (g2 - g1) * alpha)
        b = int(b1 + (b2 - b1) * alpha)
        return ColorUtils.rgb_to_hex((r, g, b))

    @staticmethod
    def lighten(color: str, amount: float) -> str:
        return ColorUtils.blend(color, "#ffffff", amount)

    @staticmethod
    def darken(color: str, amount: float) -> str:
        return ColorUtils.blend(color, "#000000", amount)


class FluentAnimator:
    """Simple animations for Fluent-like hover/press effects."""

    def __init__(
        self,
        widget: tk.Widget,
        start_color: str,
        end_color: str,
        duration: int = 120,
        steps: int = 6,
    ):
        self.widget = widget
        self.start_color = start_color
        self.end_color = end_color
        self.duration = max(duration, 1)
        self.steps = max(steps, 1)
        self._current_step = 0
        self._job = None

    def start(self):
        self.stop()
        self._current_step = 0
        self._animate_forward()

    def reverse(self):
        self.stop()
        self._current_step = self.steps
        self._animate_backward()

    def stop(self):
        if self._job:
            self.widget.after_cancel(self._job)
            self._job = None

    def _animate_forward(self):
        alpha = min(self._current_step / self.steps, 1.0)
        color = ColorUtils.blend(self.start_color, self.end_color, alpha)
        try:
            self.widget.configure(background=color)
        except tk.TclError:
            pass
        if self._current_step < self.steps:
            self._current_step += 1
            delay = int(self.duration / self.steps)
            self._job = self.widget.after(delay, self._animate_forward)

    def _animate_backward(self):
        alpha = max(self._current_step / self.steps, 0.0)
        color = ColorUtils.blend(self.start_color, self.end_color, alpha)
        try:
            self.widget.configure(background=color)
        except tk.TclError:
            pass
        if self._current_step > 0:
            self._current_step -= 1
            delay = int(self.duration / self.steps)
            self._job = self.widget.after(delay, self._animate_backward)


class WebsiteAnalyzerApp:
    """Main application window for website analysis."""

    def __init__(self, root):
        self.root = root
        self.root.title("Website Analyzer - Website analysis and comparison")
        self.root.geometry("1200x800")
        self.root.minsize(1024, 640)
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        for name in (
            "TkTextFont",
            "TkMenuFont",
            "TkHeadingFont",
            "TkCaptionFont",
            "TkSmallCaptionFont",
            "TkIconFont",
        ):
            try:
                tkfont.nametofont(name).configure(family="Segoe UI", size=10)
            except tk.TclError:
                pass
        self.root.tk.call("tk", "scaling", 1.2)
        if sys.platform == "win32":
            try:
                from ctypes import windll

                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        self.init_theme_support()
        self.create_fluent_manager()
        self.setup_styles()
        self.own_site_data = None
        self.competitor_site_data = None
        self.comparison_data = None
        self.create_widgets()
        self.root.bind_all("<Control-c>", self.global_copy)
        self.root.bind_all("<Control-v>", self.global_paste)
        self.root.bind_all("<Control-x>", self.global_cut)
        self.root.bind_all("<Control-a>", self.global_select_all)
        self.check_services_status()

    def init_theme_support(self):
        self.theme_name = tk.StringVar(value="win11_light")
        self.theme_data = WIN11_THEMES[self.theme_name.get()]
        self.theme_observers: List[Callable] = []

        def on_theme_change(*_):
            self.theme_data = WIN11_THEMES[self.theme_name.get()]
            self.apply_theme()

        self.theme_name.trace_add("write", on_theme_change)
        if WinUIEffects.is_supported():
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if self.theme_name.get() == "win11_dark":
                WinUIEffects.enable_acrylic(hwnd, dark=True)
            else:
                WinUIEffects.enable_mica_effect(hwnd, dark=False)
            WinUIEffects.set_immersive_border(hwnd)

    def setup_styles(self):
        self.apply_theme()

    def apply_theme(self):
        style = ttk.Style()
        theme = self.theme_data
        self.root.configure(bg=theme["window_bg"])
        if WinUIEffects.is_supported():
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if self.theme_name.get() == "win11_dark":
                WinUIEffects.enable_acrylic(hwnd, dark=True)
            else:
                WinUIEffects.enable_mica_effect(hwnd, dark=False)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 18, "bold"),
            foreground=theme["foreground"],
            background=theme["window_bg"],
        )
        style.configure(
            "Heading.TLabel",
            font=("Segoe UI", 13, "bold"),
            foreground=theme["foreground"],
            background=theme["card_bg"],
        )
        style.configure(
            "Body.TLabel",
            font=("Segoe UI", 10),
            foreground=theme["muted"],
            background=theme["card_bg"],
        )
        style.configure(
            "Caption.TLabel",
            font=("Segoe UI", 9),
            foreground=theme["muted_alt"],
            background=theme["card_bg"],
        )
        style.configure(
            "Success.TLabel",
            font=("Segoe UI", 10, "bold"),
            foreground=theme["success"],
            background=theme["card_bg"],
        )
        style.configure(
            "Error.TLabel",
            font=("Segoe UI", 10, "bold"),
            foreground=theme["error"],
            background=theme["card_bg"],
        )
        style.configure(
            "Warning.TLabel",
            font=("Segoe UI", 10, "bold"),
            foreground=theme["warning"],
            background=theme["card_bg"],
        )
        style.configure("Win11.TFrame", background=theme["card_bg"])
        style.configure(
            "Win11.Surface.TFrame",
            background=theme["card_bg"],
            borderwidth=0,
            relief="flat",
        )
        style.configure("Win11.TLabelframe", background=theme["card_bg"], borderwidth=0)
        style.configure(
            "Win11.TLabelframe.Label",
            font=("Segoe UI", 10, "bold"),
            foreground=theme["muted_alt"],
            background=theme["card_bg"],
        )
        style.configure(
            "Win11.TButton",
            font=("Segoe UI", 10),
            padding=(12, 8),
            background=theme["control_bg"],
            foreground=theme["foreground"],
            borderwidth=0,
        )
        style.map(
            "Win11.TButton",
            background=[
                ("active", theme["control_hover"]),
                ("pressed", theme["control_hover"]),
            ],
            foreground=[("disabled", theme["muted"])],
        )
        style.map("Win11.TButton", relief=[("pressed", "flat"), ("!pressed", "flat")])
        style.configure(
            "Win11.Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 9),
            background=theme["accent"],
            foreground="#ffffff",
            borderwidth=0,
        )
        style.map(
            "Win11.Accent.TButton",
            background=[
                ("active", theme["accent_hover"]),
                ("pressed", theme["accent_hover"]),
            ],
            relief=[("pressed", "flat"), ("!pressed", "flat")],
        )
        style.map(
            "Win11.TButton",
            highlightcolor=[("focus", theme["accent"])],
            highlightbackground=[("focus", theme["accent"])],
            highlightthickness=[("focus", 1)],
        )
        style.map(
            "Win11.Accent.TButton",
            highlightcolor=[("focus", "#ffffff")],
            highlightbackground=[("focus", "#ffffff")],
            highlightthickness=[("focus", 1)],
        )
        style.configure(
            "Win11.TMenubutton",
            font=("Segoe UI", 10),
            padding=(12, 6),
            background=theme["control_bg"],
            foreground=theme["foreground"],
            borderwidth=0,
        )
        style.map("Win11.TMenubutton", background=[("active", theme["control_hover"])])
        style.configure("Win11.TNotebook", background=theme["window_bg"], borderwidth=0)
        style.configure(
            "Win11.TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 10),
            foreground=theme["muted"],
            background=theme["tab_bg"],
            borderwidth=0,
        )
        style.map(
            "Win11.TNotebook.Tab",
            background=[
                ("selected", theme["tab_active"]),
                ("active", theme["tab_hover"]),
            ],
            foreground=[
                ("selected", theme["foreground"]),
                ("active", theme["foreground"]),
            ],
        )
        style.configure(
            "Win11.TEntry",
            fieldbackground=theme["entry_bg"],
            foreground=theme["foreground"],
            insertcolor=theme["accent"],
            padding=6,
            borderwidth=0,
        )
        style.configure(
            "Win11.Horizontal.TProgressbar",
            background=theme["accent"],
            troughcolor=theme["card_bg"],
            borderwidth=0,
        )
        style.configure("Win11.TSeparator", background=theme["border"])
        for callback in self.theme_observers:
            try:
                callback()
            except Exception:
                pass
        self.root.update_idletasks()

    def add_theme_observer(self, callback: Callable):
        self.theme_observers.append(callback)
        return callback

    def apply_editor_theme(self, text_widget):
        theme = self.theme_data
        try:
            text_widget.configure(
                background=theme["editor_bg"],
                foreground=theme["foreground"],
                insertbackground=theme["accent"],
                selectbackground=theme["accent"],
                selectforeground=theme["foreground"],
            )
        except tk.TclError:
            pass

    def create_fluent_manager(self):
        self.fluent_manager = {"controls": [], "nav_items": [], "animators": {}}

    def register_control(self, widget: tk.Widget, role: str = "control"):
        self.fluent_manager["controls"].append((widget, role))
        self.apply_control_fluent_style(widget, role)

    def register_nav_item(self, widget: tk.Widget):
        self.fluent_manager["nav_items"].append(widget)
        self.apply_nav_reveal(widget)

    def apply_control_fluent_style(self, widget: tk.Widget, role: str):
        theme = self.theme_data
        accent = theme["accent"]
        base_bg = theme["control_bg"] if role == "control" else theme["accent"]
        hover_bg = ColorUtils.lighten(base_bg, 0.08 if role == "control" else 0.12)
        animator = FluentAnimator(widget, base_bg, hover_bg, duration=160, steps=8)
        self.fluent_manager["animators"][widget] = animator

        def on_enter(_):
            animator.start()

        def on_leave(_):
            animator.reverse()

        def on_press(_):
            try:
                widget.configure(relief="sunken")
            except tk.TclError:
                pass

        def on_release(_):
            try:
                widget.configure(relief="flat")
            except tk.TclError:
                pass

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<ButtonPress-1>", on_press)
        widget.bind("<ButtonRelease-1>", on_release)
        self.add_theme_observer(lambda: self._update_control_colors(widget, role))

    def _update_control_colors(self, widget: tk.Widget, role: str):
        theme = self.theme_data
        base_bg = theme["control_bg"] if role == "control" else theme["accent"]
        hover_bg = ColorUtils.lighten(base_bg, 0.08 if role == "control" else 0.12)
        animator = self.fluent_manager["animators"].get(widget)
        if animator:
            animator.start_color = base_bg
            animator.end_color = hover_bg
        try:
            widget.configure(background=base_bg)
        except tk.TclError:
            pass

    def apply_nav_reveal(self, widget: tk.Widget):
        theme = self.theme_data
        base_bg = theme["tab_bg"]
        hover_bg = ColorUtils.lighten(base_bg, 0.1)
        animator = FluentAnimator(widget, base_bg, hover_bg, duration=140, steps=7)
        self.fluent_manager["animators"][widget] = animator
        widget.bind("<Enter>", lambda _: animator.start())
        widget.bind("<Leave>", lambda _: animator.reverse())
        self.add_theme_observer(lambda: self._update_nav_colors(widget))

    def _update_nav_colors(self, widget: tk.Widget):
        theme = self.theme_data
        base_bg = theme["tab_bg"]
        hover_bg = ColorUtils.lighten(base_bg, 0.1)
        animator = self.fluent_manager["animators"].get(widget)
        if animator:
            animator.start_color = base_bg
            animator.end_color = hover_bg
        try:
            widget.configure(background=base_bg)
        except tk.TclError:
            pass

    def setup_clipboard_shortcuts(self, widget):
        """Configure a context menu for Entry widgets."""
        # Context menu for Entry widgets
        popup = tk.Menu(self.root, tearoff=0)
        popup.add_command(
            label="Cut", accelerator="Ctrl+X", command=lambda: self.entry_cut(widget)
        )
        popup.add_command(
            label="Copy", accelerator="Ctrl+C", command=lambda: self.entry_copy(widget)
        )
        popup.add_command(
            label="Paste",
            accelerator="Ctrl+V",
            command=lambda: self.entry_paste(widget),
        )
        popup.add_separator()
        popup.add_command(
            label="Select All",
            accelerator="Ctrl+A",
            command=lambda: self.entry_select_all(widget),
        )

        def show_popup(event):
            try:
                popup.tk_popup(event.x_root, event.y_root)
            finally:
                popup.grab_release()

        widget.bind("<Button-3>", show_popup)  # Right click

    def entry_cut(self, widget):
        """Cut selection for an Entry widget."""
        try:
            if widget.selection_present():
                text = widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except BaseException:
            pass

    def entry_copy(self, widget):
        """Copy selection for an Entry widget."""
        try:
            if widget.selection_present():
                text = widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
        except BaseException:
            pass

    def entry_paste(self, widget):
        """Paste clipboard into an Entry widget."""
        try:
            text = self.root.clipboard_get()
            if widget.selection_present():
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            widget.insert(tk.INSERT, text)
        except BaseException:
            pass

    def entry_select_all(self, widget):
        """Select all text in an Entry widget."""
        try:
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)
        except BaseException:
            pass

    def copy_to_clipboard(self, widget):
        """Copy selected text."""
        try:
            if widget.selection_present():
                text = widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
        except BaseException:
            pass
        return "break"

    def cut_to_clipboard(self, widget):
        try:
            if widget.selection_present():
                text = widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except BaseException:
            pass
        return "break"

    def paste_from_clipboard(self, widget):
        try:
            text = self.root.clipboard_get()
            if widget.selection_present():
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            widget.insert(tk.INSERT, text)
        except BaseException:
            pass
        return "break"

    def global_copy(self, event):
        try:
            widget = self.root.focus_get()
            if widget and isinstance(widget, (ttk.Entry, tk.Entry, tk.Text)):
                if isinstance(widget, (ttk.Entry, tk.Entry)):
                    if widget.selection_present():
                        text = widget.selection_get()
                        self.root.clipboard_clear()
                        self.root.clipboard_append(text)
                elif isinstance(widget, tk.Text):
                    try:
                        text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                        self.root.clipboard_clear()
                        self.root.clipboard_append(text)
                    except tk.TclError:
                        pass
        except BaseException:
            pass
        return "break"

    def global_paste(self, event):
        try:
            widget = self.root.focus_get()
            if widget and isinstance(widget, (ttk.Entry, tk.Entry, tk.Text)):
                text = self.root.clipboard_get()
                if isinstance(widget, (ttk.Entry, tk.Entry)):
                    if widget.selection_present():
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    widget.insert(tk.INSERT, text)
                elif isinstance(widget, tk.Text):
                    try:
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    except tk.TclError:
                        pass
                    widget.insert(tk.INSERT, text)
        except BaseException:
            pass
        return "break"

    def global_cut(self, event):
        try:
            widget = self.root.focus_get()
            if widget and isinstance(widget, (ttk.Entry, tk.Entry, tk.Text)):
                if isinstance(widget, (ttk.Entry, tk.Entry)):
                    if widget.selection_present():
                        text = widget.selection_get()
                        self.root.clipboard_clear()
                        self.root.clipboard_append(text)
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                elif isinstance(widget, tk.Text):
                    try:
                        text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                        self.root.clipboard_clear()
                        self.root.clipboard_append(text)
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    except tk.TclError:
                        pass
        except BaseException:
            pass
        return "break"

    def global_select_all(self, event):
        try:
            widget = self.root.focus_get()
            if widget and isinstance(widget, (ttk.Entry, tk.Entry, tk.Text)):
                if isinstance(widget, (ttk.Entry, tk.Entry)):
                    widget.select_range(0, tk.END)
                    widget.icursor(tk.END)
                elif isinstance(widget, tk.Text):
                    widget.tag_add(tk.SEL, "1.0", tk.END)
                    widget.mark_set(tk.INSERT, "1.0")
                    widget.see(tk.INSERT)
        except BaseException:
            pass
        return "break"

    def setup_text_widget_shortcuts(self, widget):
        widget.bind("<Button-3>", lambda e: self.show_context_menu(e, widget))

    def show_context_menu(self, event, widget):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(
            label="Copy (Ctrl+C)", command=lambda: widget.event_generate("<<Copy>>")
        )
        menu.add_command(
            label="Select all (Ctrl+A)", command=lambda: self.select_all_text(widget)
        )
        try:
            menu.post(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def select_all_text(self, widget):
        widget.tag_add(tk.SEL, "1.0", "end-1c")
        widget.mark_set(tk.INSERT, "1.0")
        widget.see(tk.INSERT)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="12", style="Win11.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        header_frame = ttk.Frame(main_frame, style="Win11.Surface.TFrame")
        header_frame.grid(
            row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 16)
        )
        header_frame.columnconfigure(0, weight=1)
        title_label = ttk.Label(
            header_frame, text="Website Analyzer", style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        subtitle = ttk.Label(
            header_frame,
            text="Modern website analysis using microservices and GPT-5",
            style="Caption.TLabel",
        )
        subtitle.grid(row=1, column=0, sticky=tk.W, pady=(4, 0))
        theme_menu = ttk.Menubutton(
            header_frame, text="Theme", style="Win11.TMenubutton"
        )
        theme_menu.menu = tk.Menu(theme_menu, tearoff=0)
        theme_menu["menu"] = theme_menu.menu
        for key, data in WIN11_THEMES.items():
            theme_menu.menu.add_radiobutton(
                label=data["title"], variable=self.theme_name, value=key
            )
        theme_menu.grid(row=0, column=1, rowspan=2, padx=(12, 0))
        status_frame = ttk.Labelframe(
            main_frame,
            text="Microservices status",
            padding="16",
            style="Win11.TLabelframe",
        )
        status_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12)
        )
        status_frame.columnconfigure(1, weight=1)
        self.service_status_labels = {}
        services = [
            ("SEO Analysis", settings.SEO_SERVICE_PORT),
            ("Text Analysis", settings.TEXT_SERVICE_PORT),
            ("Convenience Analysis", settings.CONVENIENCE_SERVICE_PORT),
            ("Senior Analysis", settings.SENIOR_SERVICE_PORT),
        ]
        for i, (service_name, port) in enumerate(services):
            ttk.Label(
                status_frame, text=f"{service_name}:", style="Heading.TLabel"
            ).grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            status_label = ttk.Label(
                status_frame, text="Checking...", style="Caption.TLabel"
            )
            status_label.grid(row=i, column=1, sticky=tk.W)
            address_label = ttk.Label(
                status_frame, text=f"http://localhost:{port}", style="Caption.TLabel"
            )
            address_label.grid(row=i, column=2, sticky=tk.W)
            self.service_status_labels[service_name] = status_label
        url_frame = ttk.Labelframe(
            main_frame,
            text="URL input for analysis",
            padding="16",
            style="Win11.TLabelframe",
        )
        url_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        url_frame.columnconfigure(1, weight=1)
        url_frame.columnconfigure(3, weight=1)
        ttk.Label(url_frame, text="Your website:", style="Body.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.own_site_entry = ttk.Entry(url_frame, width=50, style="Win11.TEntry")
        self.own_site_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 24))
        self.own_site_entry.insert(0, "https://themore.ru")
        self.setup_clipboard_shortcuts(self.own_site_entry)
        ttk.Label(url_frame, text="Competitor website:", style="Body.TLabel").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 10)
        )
        self.competitor_site_entry = ttk.Entry(
            url_frame, width=50, style="Win11.TEntry"
        )
        self.competitor_site_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))
        self.competitor_site_entry.insert(0, "https://www.dominos.ru")
        self.setup_clipboard_shortcuts(self.competitor_site_entry)
        buttons_frame = ttk.Frame(main_frame, style="Win11.Surface.TFrame")
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(0, 12))
        ttk.Label(buttons_frame, text="Your website:", style="Body.TLabel").pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(
            buttons_frame,
            text="SEO",
            command=lambda: self.analyze_site("seo", self.own_site_entry.get()),
            style="Win11.TButton",
        ).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(
            buttons_frame,
            text="Text",
            command=lambda: self.analyze_site("text", self.own_site_entry.get()),
            style="Win11.TButton",
        ).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(
            buttons_frame,
            text="UX",
            command=lambda: self.analyze_site("convenience", self.own_site_entry.get()),
            style="Win11.TButton",
        ).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(buttons_frame, text="Competitor:", style="Body.TLabel").pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(
            buttons_frame,
            text="SEO",
            command=lambda: self.analyze_site("seo", self.competitor_site_entry.get()),
            style="Win11.TButton",
        ).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(
            buttons_frame,
            text="Text",
            command=lambda: self.analyze_site("text", self.competitor_site_entry.get()),
            style="Win11.TButton",
        ).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(
            buttons_frame,
            text="UX",
            command=lambda: self.analyze_site(
                "convenience", self.competitor_site_entry.get()
            ),
            style="Win11.TButton",
        ).pack(side=tk.LEFT, padx=(0, 12))
        for child in buttons_frame.winfo_children():
            if isinstance(child, ttk.Button):
                role = (
                    "accent" if child["text"] == "Full site comparison" else "control"
                )
                self.register_control(
                    child, role="accent" if role == "accent" else "control"
                )
        ttk.Separator(buttons_frame, orient="vertical", style="Win11.TSeparator").pack(
            side=tk.LEFT, fill=tk.Y, padx=12
        )
        compare_button = ttk.Button(
            buttons_frame,
            text="Full site comparison",
            command=self.full_comparison,
            style="Win11.Accent.TButton",
        )
        compare_button.pack(side=tk.LEFT, padx=(0, 6))
        self.register_control(compare_button, role="accent")
        export_button = ttk.Button(
            buttons_frame,
            text="Export results",
            command=self.export_results,
            style="Win11.TButton",
        )
        export_button.pack(side=tk.LEFT, padx=(0, 6))
        self.register_control(export_button)
        clear_button = ttk.Button(
            buttons_frame,
            text="Clear",
            command=self.clear_results,
            style="Win11.TButton",
        )
        clear_button.pack(side=tk.LEFT)
        self.register_control(clear_button)
        results_frame = ttk.Frame(main_frame, style="Win11.TFrame")
        results_frame.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12)
        )
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.notebook = ttk.Notebook(results_frame, style="Win11.TNotebook")
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.own_site_frame = ttk.Frame(self.notebook, style="Win11.TFrame")
        self.notebook.add(self.own_site_frame, text="Your website")
        self.register_nav_item(self.own_site_frame)
        self.competitor_site_frame = ttk.Frame(self.notebook, style="Win11.TFrame")
        self.notebook.add(self.competitor_site_frame, text="Competitor website")
        self.register_nav_item(self.competitor_site_frame)
        self.comparison_frame = ttk.Frame(self.notebook, style="Win11.TFrame")
        self.notebook.add(self.comparison_frame, text="Comparison")
        self.register_nav_item(self.comparison_frame)
        self.create_results_text_areas()
        progress_frame = ttk.Frame(main_frame, style="Win11.Surface.TFrame")
        progress_frame.grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12)
        )
        progress_frame.columnconfigure(0, weight=1)
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(
            progress_frame, textvariable=self.progress_var, style="Caption.TLabel"
        )
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(
            progress_frame, mode="indeterminate", style="Win11.Horizontal.TProgressbar"
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(6, 0))

    def create_services_status_frame(self, parent, row):
        status_frame = ttk.LabelFrame(parent, text="Microservices status", padding="10")
        status_frame.grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        status_frame.columnconfigure(1, weight=1)
        self.service_status_labels = {}
        services = [
            ("SEO Analysis", settings.SEO_SERVICE_PORT),
            ("Text Analysis", settings.TEXT_SERVICE_PORT),
            ("Convenience Analysis", settings.CONVENIENCE_SERVICE_PORT),
            ("Senior Analysis", settings.SENIOR_SERVICE_PORT),
        ]
        for i, (service_name, port) in enumerate(services):
            ttk.Label(status_frame, text=f"{service_name}:").grid(
                row=i, column=0, sticky=tk.W, padx=(0, 10)
            )
            status_label = ttk.Label(
                status_frame, text="Checking...", style="Warning.TLabel"
            )
            status_label.grid(row=i, column=1, sticky=tk.W)
            self.service_status_labels[service_name] = status_label

    def create_url_input_frame(self, parent, row):
        url_frame = ttk.LabelFrame(parent, text="URL input for analysis", padding="10")
        url_frame.grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        url_frame.columnconfigure(1, weight=1)
        url_frame.columnconfigure(3, weight=1)
        ttk.Label(url_frame, text="Your website:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.own_site_entry = ttk.Entry(url_frame, width=50)
        self.own_site_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        self.own_site_entry.insert(0, "https://themore.ru")
        self.setup_clipboard_shortcuts(self.own_site_entry)
        ttk.Label(url_frame, text="Competitor website:").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 10)
        )
        self.competitor_site_entry = ttk.Entry(url_frame, width=50)
        self.competitor_site_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))
        self.competitor_site_entry.insert(0, "https://www.dominos.ru")
        self.setup_clipboard_shortcuts(self.competitor_site_entry)

    def create_analysis_buttons_frame(self, parent, row):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        own_label = ttk.Label(buttons_frame, text="Your website:")
        own_label.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            buttons_frame,
            text="SEO",
            command=lambda: self.analyze_site("seo", self.own_site_entry.get()),
        ).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(
            buttons_frame,
            text="Text",
            command=lambda: self.analyze_site("text", self.own_site_entry.get()),
        ).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(
            buttons_frame,
            text="UX",
            command=lambda: self.analyze_site("convenience", self.own_site_entry.get()),
        ).pack(side=tk.LEFT, padx=(0, 10))
        comp_label = ttk.Label(buttons_frame, text="Competitor:")
        comp_label.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            buttons_frame,
            text="SEO",
            command=lambda: self.analyze_site("seo", self.competitor_site_entry.get()),
        ).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(
            buttons_frame,
            text="Text",
            command=lambda: self.analyze_site("text", self.competitor_site_entry.get()),
        ).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(
            buttons_frame,
            text="UX",
            command=lambda: self.analyze_site(
                "convenience", self.competitor_site_entry.get()
            ),
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Separator(buttons_frame, orient="vertical").pack(
            side=tk.LEFT, fill=tk.Y, padx=10
        )
        ttk.Button(
            buttons_frame,
            text="Full site comparison",
            command=self.full_comparison,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            buttons_frame, text="Export results", command=self.export_results
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Clear", command=self.clear_results).pack(
            side=tk.LEFT
        )

    def create_results_frame(self, parent, row):
        results_frame = ttk.LabelFrame(parent, text="Analysis results", padding="10")
        results_frame.grid(
            row=row,
            column=0,
            columnspan=3,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(0, 10),
        )
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(row, weight=1)
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.own_site_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.own_site_frame, text="Your website")
        self.competitor_site_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.competitor_site_frame, text="Competitor website")
        self.comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_frame, text="Comparison")
        self.create_results_text_areas()

    def create_results_text_areas(self):
        self.own_site_text = scrolledtext.ScrolledText(
            self.own_site_frame, wrap=tk.WORD, height=20, width=100, relief="flat", bd=1
        )
        self.own_site_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.setup_text_widget_shortcuts(self.own_site_text)
        self.add_theme_observer(lambda: self.apply_editor_theme(self.own_site_text))
        self.apply_editor_theme(self.own_site_text)
        self.competitor_site_text = scrolledtext.ScrolledText(
            self.competitor_site_frame,
            wrap=tk.WORD,
            height=20,
            width=100,
            relief="flat",
            bd=1,
        )
        self.competitor_site_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.setup_text_widget_shortcuts(self.competitor_site_text)
        self.add_theme_observer(
            lambda: self.apply_editor_theme(self.competitor_site_text)
        )
        self.apply_editor_theme(self.competitor_site_text)
        self.comparison_text = scrolledtext.ScrolledText(
            self.comparison_frame,
            wrap=tk.WORD,
            height=20,
            width=100,
            relief="flat",
            bd=1,
        )
        self.comparison_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.setup_text_widget_shortcuts(self.comparison_text)
        self.add_theme_observer(lambda: self.apply_editor_theme(self.comparison_text))
        self.apply_editor_theme(self.comparison_text)

    def create_progress_frame(self, parent, row):
        """Create a progress/status frame."""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        progress_frame.columnconfigure(0, weight=1)
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

    def check_services_status(self):
        """Check microservices availability status."""

        def check_services():
            services = [
                ("SEO Analysis", settings.SEO_SERVICE_PORT),
                ("Text Analysis", settings.TEXT_SERVICE_PORT),
                ("Convenience Analysis", settings.CONVENIENCE_SERVICE_PORT),
                ("Senior Analysis", settings.SENIOR_SERVICE_PORT),
            ]
            for service_name, port in services:
                try:
                    response = requests.get(f"http://localhost:{port}/", timeout=2)
                    if response.status_code == 200:
                        self.service_status_labels[service_name].config(
                            text="[OK] Available", style="Success.TLabel"
                        )
                    else:
                        self.service_status_labels[service_name].config(
                            text="[X] Error", style="Error.TLabel"
                        )
                except BaseException:
                    self.service_status_labels[service_name].config(
                        text="[X] Unavailable", style="Error.TLabel"
                    )

        # Run checks in a background thread
        threading.Thread(target=check_services, daemon=True).start()

    def analyze_site(self, analysis_type: str, url: str):
        """Analyze a single website."""
        if not url or not url.startswith(("http://", "https://")):
            messagebox.showerror("Error", "Please enter a valid URL.")
            return

        def perform_analysis():
            self.progress_bar.start()
            self.progress_var.set(f"Running {analysis_type} analysis...")
            try:
                if analysis_type == "seo":
                    result = self.call_seo_service(url)
                elif analysis_type == "text":
                    result = self.call_text_service(url)
                elif analysis_type == "convenience":
                    result = self.call_convenience_service(url)
                else:
                    result = {"error": "Unknown analysis type"}
                # Update the UI in the main thread
                self.root.after(
                    0, lambda: self.display_analysis_result(result, analysis_type, url)
                )
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Analysis error: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
                self.root.after(0, lambda: self.progress_var.set("Analysis completed"))

        threading.Thread(target=perform_analysis, daemon=True).start()

    def full_comparison(self):
        """Run a full comparison between two websites."""
        own_url = self.own_site_entry.get()
        competitor_url = self.competitor_site_entry.get()
        if not own_url or not competitor_url:
            messagebox.showerror("Error", "Please enter both URLs.")
            return
        if not (
            own_url.startswith(("http://", "https://"))
            and competitor_url.startswith(("http://", "https://"))
        ):
            messagebox.showerror("Error", "Please enter valid URLs.")
            return

        def perform_comparison():
            self.progress_bar.start()
            self.progress_var.set("Running full site comparison...")
            try:
                # Compare via the Senior service (it orchestrates the other services)
                self.progress_var.set("Starting comparison via Senior Agent...")
                comparison_result = self.call_senior_service(own_url, competitor_url)
                # Update the UI
                self.root.after(
                    0,
                    lambda: self.display_comparison_results_v2(
                        own_url, competitor_url, comparison_result
                    ),
                )
            except Exception as e:
                error_msg = f"Comparison error: {str(e)}"
                print(f"DEBUG: {error_msg}")
                import traceback

                traceback.print_exc()
                # Pass error_msg as a default arg to avoid late binding issues
                self.root.after(0, lambda msg=error_msg: self.show_error(msg))
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
                self.root.after(
                    0, lambda: self.progress_var.set("Comparison completed")
                )

        threading.Thread(target=perform_comparison, daemon=True).start()

    def call_seo_service(self, url: str) -> str:
        """Call the SEO service."""
        response = requests.post(
            f"http://localhost:{settings.SEO_SERVICE_PORT}/seo_analysis",
            json={"url": url},
            timeout=60,
        )
        response.raise_for_status()
        return response.text

    def call_text_service(self, url: str) -> str:
        """Call the Text service."""
        response = requests.post(
            f"http://localhost:{settings.TEXT_SERVICE_PORT}/text_analysis",
            json={"url": url},
            timeout=60,
        )
        response.raise_for_status()
        return response.text

    def call_convenience_service(self, url: str) -> str:
        """Call the Convenience/UX service."""
        response = requests.post(
            f"http://localhost:{settings.CONVENIENCE_SERVICE_PORT}/convenience_analysis",
            json={"url": url},
            timeout=60,
        )
        response.raise_for_status()
        return response.text

    def call_senior_service(self, site1_url: str, site2_url: str) -> str:
        """Call the Senior comparison service."""
        data = {"site1_url": site1_url, "site2_url": site2_url}
        response = requests.post(
            f"http://localhost:{settings.SENIOR_SERVICE_PORT}/compare_sites",
            json=data,
            timeout=600,  # 10 minutes: Senior calls all services + GPT-5 analysis
        )
        response.raise_for_status()
        return response.text

    def display_analysis_result(self, result: str, analysis_type: str, url: str):
        """Display an analysis result in the appropriate tab."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = f"[{timestamp}] {analysis_type.upper()} analysis for {url}:\n"
        text += result
        text += "\n\n"
        # Decide which tab should receive the output
        own_url = self.own_site_entry.get().strip()
        competitor_url = self.competitor_site_entry.get().strip()
        url_clean = url.strip()
        # Debug
        print(f"DEBUG: Analysis URL: '{url_clean}'")
        print(f"DEBUG: Your website: '{own_url}'")
        print(f"DEBUG: Competitor: '{competitor_url}'")
        if url_clean == own_url:
            print("DEBUG: Result goes to the 'Your website' tab")
            self.own_site_text.insert(tk.END, text)
            self.own_site_text.see(tk.END)
        elif url_clean == competitor_url:
            print("DEBUG: Result goes to the 'Competitor website' tab")
            self.competitor_site_text.insert(tk.END, text)
            self.competitor_site_text.see(tk.END)
        else:
            # If the URL does not match either input, default to competitor tab
            print("DEBUG: URL does not match inputs; defaulting to competitor tab")
            self.competitor_site_text.insert(tk.END, text)
            self.competitor_site_text.see(tk.END)

    def display_comparison_results_v2(
        self, own_url: str, competitor_url: str, comparison_result: str
    ):
        """Display comparison results (current version)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Comparison results: plain-text analysis from Senior
        comparison_text_content = f"[{timestamp}] COMPARATIVE ANALYSIS:\n\n"
        comparison_text_content += f"Your website: {own_url}\n"
        comparison_text_content += f"Competitor website: {competitor_url}\n\n"
        comparison_text_content += "─" * 80 + "\n\n"
        comparison_text_content += comparison_result
        comparison_text_content += "\n\n"
        self.comparison_text.delete("1.0", tk.END)
        self.comparison_text.insert(tk.END, comparison_text_content)
        self.comparison_text.see(tk.END)
        # Switch to the comparison tab
        self.notebook.select(self.comparison_frame)

    def display_comparison_results(
        self,
        own_seo,
        own_text,
        own_convenience,
        competitor_seo,
        competitor_text,
        competitor_convenience,
        comparison_result,
    ):
        """Display comparison results (legacy version; not used)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Your website results
        own_text_content = f"[{timestamp}] YOUR WEBSITE RESULTS:\n\n"
        own_text_content += self.format_analysis_results(
            own_seo, own_text, own_convenience
        )
        self.own_site_text.insert(tk.END, own_text_content)
        self.own_site_text.see(tk.END)
        # Competitor website results
        competitor_text_content = f"[{timestamp}] COMPETITOR WEBSITE RESULTS:\n\n"
        competitor_text_content += self.format_analysis_results(
            competitor_seo, competitor_text, competitor_convenience
        )
        self.competitor_site_text.insert(tk.END, competitor_text_content)
        self.competitor_site_text.see(tk.END)
        # Comparison results
        comparison_text_content = f"[{timestamp}] COMPARISON RESULTS:\n\n"
        comparison_text_content += self.format_comparison_result(comparison_result)
        comparison_text_content += "\n\n"
        self.comparison_text.insert(tk.END, comparison_text_content)
        self.comparison_text.see(tk.END)
        # Switch to the comparison tab
        self.notebook.select(self.comparison_frame)

    def format_site_analysis(self, site_data: Dict[str, Any]) -> str:
        """Format a single-site analysis payload into readable text."""
        result = ""
        if isinstance(site_data, dict):
            result = self.format_dict_recursive(site_data, indent=0)
        else:
            result = str(site_data)
        return result

    def format_analysis_results(self, seo, text, convenience):
        """Format analysis results into a readable text block."""
        result = ""
        # SEO analysis
        result += "━" * 80 + "\n"
        result += "SEO ANALYSIS\n"
        result += "━" * 80 + "\n\n"
        if isinstance(seo, dict):
            result += self.format_dict_recursive(seo, indent=0)
        else:
            result += str(seo)
        result += "\n\n"
        # Text analysis
        result += "━" * 80 + "\n"
        result += "TEXT ANALYSIS\n"
        result += "━" * 80 + "\n\n"
        if isinstance(text, dict):
            result += self.format_dict_recursive(text, indent=0)
        else:
            result += str(text)
        result += "\n\n"
        # Usability analysis
        result += "━" * 80 + "\n"
        result += "USABILITY ANALYSIS\n"
        result += "━" * 80 + "\n\n"
        if isinstance(convenience, dict):
            result += self.format_dict_recursive(convenience, indent=0)
        else:
            result += str(convenience)
        result += "\n\n"
        return result

    def format_comparison_result(self, comparison: Dict[str, Any]) -> str:
        theme = self.theme_data
        divider = "─" * 80
        sb = []

        def add_block(title: str, lines: List[str]):
            sb.append(divider)
            sb.append(f"{title}\n")
            sb.extend(lines)
            sb.append("\n")

        if not comparison or not isinstance(comparison, dict):
            sb.append("WARNING: Empty comparison result\n")
            sb.append(json.dumps(comparison, indent=2, ensure_ascii=False))
            return "\n".join(sb)
        sb.append(f"Your website: {comparison.get('site1_url', 'N/A')}\n")
        sb.append(f"Competitor website: {comparison.get('site2_url', 'N/A')}\n\n")
        if "comparison_summary" in comparison and comparison["comparison_summary"]:
            add_block("Summary", [comparison["comparison_summary"]])
        if "overall_scores" in comparison and isinstance(
            comparison["overall_scores"], dict
        ):
            lines = [
                f"• {key}: {value}"
                for key, value in comparison["overall_scores"].items()
            ]
            add_block("Overall scores", lines)
        gpt5 = comparison.get("gpt5_analysis")
        if isinstance(gpt5, dict):
            summary_lines = []
            summary = gpt5.get("summary")
            if isinstance(summary, dict):
                observations = summary.get("observations") or []
                summary_lines.append("Observations:")
                for obs in observations:
                    summary_lines.append(f"  • {obs}")
                if summary.get("insights"):
                    summary_lines.append("\nKey insights:")
                    for insight in summary["insights"]:
                        summary_lines.append(f"  • {insight}")
            add_block("GPT-5 analysis", summary_lines or ["No data"])
            recommendations = gpt5.get("recommendations") or []
            if recommendations:
                lines = [
                    f"{idx}. {rec}" for idx, rec in enumerate(recommendations, start=1)
                ]
                add_block("Recommendations", lines)
            action_plan = gpt5.get("action_plan") or []
            if action_plan:
                plan_lines = []
                for phase in action_plan:
                    if isinstance(phase, dict):
                        plan_lines.append(f"▸ {phase.get('phase', 'Phase')}\n")
                        tasks = phase.get("tasks") or []
                        for task in tasks:
                            plan_lines.append(f"  • {task}")
                        plan_lines.append("")
                add_block("Action plan", plan_lines)
        return "\n".join(sb)

    def format_dict_recursive(self, data, indent=0, exclude_keys=None):
        """Recursively format a dict into a readable text tree."""
        if exclude_keys is None:
            exclude_keys = []
        result = ""
        indent_str = "  " * indent
        if isinstance(data, dict):
            for key, value in data.items():
                if key in exclude_keys:
                    continue
                # Convert technical keys to human-readable labels
                key_ru = self.translate_key(key)
                if isinstance(value, dict):
                    result += f"{indent_str}▸ {key_ru}:\n"
                    result += self.format_dict_recursive(value, indent + 1)
                elif isinstance(value, list):
                    result += f"{indent_str}▸ {key_ru}:\n"
                    for i, item in enumerate(value, 1):
                        if isinstance(item, (dict, list)):
                            result += f"{indent_str}  {i}. {self.format_dict_recursive(item, indent + 2)}"
                        else:
                            result += f"{indent_str}  {i}. {item}\n"
                else:
                    result += f"{indent_str}• {key_ru}: {value}\n"
        elif isinstance(data, list):
            for i, item in enumerate(data, 1):
                result += f"{indent_str}{i}. {item}\n"
        else:
            result += f"{indent_str}{data}\n"
        return result

    def translate_key(self, key):
        """Convert technical keys to human-readable English labels."""
        translations = {
            "url": "URL",
            "seo_score": "SEO score",
            "text_quality": "Text quality",
            "convenience_score": "Usability score",
            "performance": "Performance",
            "loading_time": "Load time",
            "recommendations": "Recommendations",
            "issues": "Issues",
            "strengths": "Strengths",
            "weaknesses": "Weaknesses",
            "comparison_summary": "Summary",
            "overall_scores": "Overall scores",
            "error": "Error",
            "status": "Status",
            "raw_data": "Raw data",
            "gpt5_analysis": "GPT-5 analysis",
            "mobile_performance": "Mobile performance",
            "desktop": "Desktop",
            "mobile": "Mobile",
        }
        return translations.get(key, key.replace("_", " ").title())

    def export_results(self):
        """Export results to a file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if filename:
            try:
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "own_site_url": self.own_site_entry.get(),
                    "competitor_site_url": self.competitor_site_entry.get(),
                    "own_site_results": self.own_site_text.get("1.0", tk.END),
                    "competitor_site_results": self.competitor_site_text.get(
                        "1.0", tk.END
                    ),
                    "comparison_results": self.comparison_text.get("1.0", tk.END),
                }
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export error: {str(e)}")

    def clear_results(self):
        """Clear all results from the UI."""
        if messagebox.askyesno(
            "Confirm", "Are you sure you want to clear all results?"
        ):
            self.own_site_text.delete("1.0", tk.END)
            self.competitor_site_text.delete("1.0", tk.END)
            self.comparison_text.delete("1.0", tk.END)
            self.progress_var.set("Results cleared")

    def show_error(self, message: str):
        """Show an error message."""
        messagebox.showerror("Error", message)
        self.progress_var.set("Execution error")


def main():
    """Application entrypoint."""
    root = tk.Tk()
    app = WebsiteAnalyzerApp(root)

    # Handle application close
    def on_closing():
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    # Start UI loop
    root.mainloop()


if __name__ == "__main__":
    main()
