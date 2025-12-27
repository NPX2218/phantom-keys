"""
Phantom Keys

Author: Neel
License: MIT
"""

from __future__ import annotations

import random
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Any, Callable, Optional

import pyautogui  # type: ignore[import-untyped]


# Configuration & Theming


@dataclass
class Theme:
    """Modern dark theme configuration for the application UI."""

    bg_primary: str = "#0D0D0D"
    bg_secondary: str = "#1A1A1A"
    bg_tertiary: str = "#252525"
    bg_elevated: str = "#2D2D2D"
    text_primary: str = "#FFFFFF"
    text_secondary: str = "#A0A0A0"
    text_muted: str = "#666666"
    accent_primary: str = "#6366F1"
    accent_secondary: str = "#818CF8"
    accent_success: str = "#10B981"
    accent_warning: str = "#F59E0B"
    accent_danger: str = "#EF4444"
    border_color: str = "#333333"
    font_family: str = "Segoe UI"
    font_family_mono: str = "Consolas"


THEME = Theme()


# Typing Engine


class TypingEngine:
    """
    Advanced human-like typing simulation engine.

    Handles realistic human typing simulation including variable timing,
    realistic typos based on keyboard layout, automatic corrections,
    fatigue simulation, and burst typing patterns.
    """

    TYPO_NEIGHBORS: dict[str, str] = {
        "a": "sqwz",
        "b": "vghn",
        "c": "xdfv",
        "d": "serfcx",
        "e": "wsdr",
        "f": "drtgvc",
        "g": "ftyhbv",
        "h": "gyujnb",
        "i": "ujko",
        "j": "huiknm",
        "k": "jiolm",
        "l": "kop",
        "m": "njk",
        "n": "bhjm",
        "o": "iklp",
        "p": "ol",
        "q": "wa",
        "r": "edft",
        "s": "awedxz",
        "t": "rfgy",
        "u": "yhji",
        "v": "cfgb",
        "w": "qase",
        "x": "zsdc",
        "y": "tghu",
        "z": "asx",
    }

    def __init__(self) -> None:
        """Initialize the typing engine with default state."""
        self.is_running: bool = False
        self.is_paused: bool = False
        self._stop_event: threading.Event = threading.Event()
        self._pause_event: threading.Event = threading.Event()
        self._pause_event.set()
        self.progress_callback: Optional[Callable[[float], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        self.stats: dict[str, int] = {
            "chars_typed": 0,
            "typos_made": 0,
            "words_completed": 0,
        }

    def reset_stats(self) -> None:
        """Reset all typing statistics to zero."""
        self.stats = {"chars_typed": 0, "typos_made": 0, "words_completed": 0}

    def stop(self) -> None:
        """Stop typing immediately."""
        self._stop_event.set()
        self._pause_event.set()
        self.is_running = False

    def pause(self) -> None:
        """Pause typing at the current position."""
        self.is_paused = True
        self._pause_event.clear()

    def resume(self) -> None:
        """Resume typing from the paused position."""
        self.is_paused = False
        self._pause_event.set()

    def _get_typo_char(self, char: str) -> str:
        """Get a realistic typo character based on keyboard layout."""
        char_lower = char.lower()
        if char_lower in self.TYPO_NEIGHBORS:
            typo = random.choice(self.TYPO_NEIGHBORS[char_lower])
            return typo.upper() if char.isupper() else typo
        return random.choice("abcdefghijklmnopqrstuvwxyz")

    def _calculate_char_delay(
        self, char: str, base_delay: float, variability: float
    ) -> float:
        """Calculate delay for a character with human-like variability."""
        delay = base_delay

        if char.isupper():
            delay *= 1.1

        if char in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/\\":
            delay *= 1.3

        delay *= 1 + random.uniform(-variability, variability)

        if random.random() < 0.02:
            delay += random.uniform(0.1, 0.3)

        return delay

    def type_text(
        self,
        text: str,
        wpm: int = 60,
        typo_rate: float = 0.05,
        variability: float = 0.3,
        burst_mode: bool = False,
    ) -> None:
        """Type text with human-like characteristics."""
        self._stop_event.clear()
        self.is_running = True
        self.reset_stats()

        chars_per_minute = wpm * 5
        base_delay = 60.0 / chars_per_minute

        paragraphs = text.split("\n")
        total_chars = len(text)
        chars_processed = 0

        if self.status_callback:
            self.status_callback("Typing started...")

        for para_idx, paragraph in enumerate(paragraphs):
            if self._stop_event.is_set():
                break

            words = paragraph.split()

            for word_idx, word in enumerate(words):
                if self._stop_event.is_set():
                    break

                self._pause_event.wait()

                fatigue_factor = 1 + (chars_processed / total_chars) * 0.15
                burst_active = burst_mode and random.random() < 0.15
                burst_multiplier = 0.6 if burst_active else 1.0

                for char in word:
                    if self._stop_event.is_set():
                        break

                    self._pause_event.wait()

                    if random.random() < typo_rate:
                        typo_char = self._get_typo_char(char)
                        pyautogui.write(typo_char, interval=0)
                        self.stats["typos_made"] += 1
                        time.sleep(random.uniform(0.15, 0.35))
                        pyautogui.press("backspace")
                        time.sleep(random.uniform(0.05, 0.12))

                    pyautogui.write(char, interval=0)
                    self.stats["chars_typed"] += 1
                    chars_processed += 1

                    delay = self._calculate_char_delay(
                        char, base_delay, variability)
                    delay *= burst_multiplier * fatigue_factor
                    time.sleep(delay)

                    if self.progress_callback:
                        progress = (chars_processed / total_chars) * 100
                        self.progress_callback(progress)

                if word_idx < len(words) - 1:
                    if not self._stop_event.is_set():
                        pyautogui.press("space")
                        chars_processed += 1
                        self.stats["words_completed"] += 1
                        word_pause = base_delay * \
                            random.uniform(1.5, 2.5) * fatigue_factor
                        time.sleep(word_pause)

            if para_idx < len(paragraphs) - 1:
                if not self._stop_event.is_set():
                    pyautogui.press("enter")
                    chars_processed += 1
                    paragraph_pause = random.uniform(0.8, 1.8)
                    time.sleep(paragraph_pause)

                    if self.status_callback:
                        self.status_callback("Typing... (new paragraph)")

        self.is_running = False
        self.stats["words_completed"] += 1

        if self.status_callback:
            if self._stop_event.is_set():
                self.status_callback("Typing stopped")
            else:
                self.status_callback("Typing complete!")


# Custom Widgets


class ModernButton(tk.Canvas):
    """Custom styled button widget with hover effects and color variants."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[Callable[[], None]] = None,
        variant: str = "primary",
        width: int = 120,
        height: int = 40,
    ) -> None:
        """Initialize a modern styled button."""
        super().__init__(
            parent, width=width, height=height, bg=THEME.bg_secondary, highlightthickness=0
        )

        self.text = text
        self.command = command
        self.variant = variant
        self._width = width
        self._height = height
        self._enabled = True

        self.colors: dict[str, dict[str, str]] = {
            "primary": {
                "bg": THEME.accent_primary,
                "hover": THEME.accent_secondary,
                "text": THEME.text_primary,
            },
            "success": {
                "bg": THEME.accent_success,
                "hover": "#34D399",
                "text": THEME.text_primary,
            },
            "danger": {
                "bg": THEME.accent_danger,
                "hover": "#F87171",
                "text": THEME.text_primary,
            },
            "ghost": {
                "bg": THEME.bg_tertiary,
                "hover": THEME.bg_elevated,
                "text": THEME.text_secondary,
            },
        }

        self.current_color = self.colors[variant]["bg"]
        self.redraw()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def redraw(self) -> None:
        """Redraw the button with current state."""
        self.delete("all")

        radius = 8
        x1, y1, x2, y2 = 2, 2, self._width - 2, self._height - 2

        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]

        fill_color = self.current_color if self._enabled else THEME.bg_tertiary
        text_color = self.colors[self.variant]["text"] if self._enabled else THEME.text_muted

        self.create_polygon(points, fill=fill_color, smooth=True)
        self.create_text(
            self._width // 2,
            self._height // 2,
            text=self.text,
            fill=text_color,
            font=(THEME.font_family, 11, "bold"),
        )

    def _on_enter(self, _: Any) -> None:
        """Handle mouse enter event."""
        if self._enabled:
            self.current_color = self.colors[self.variant]["hover"]
            self.redraw()

    def _on_leave(self, _: Any) -> None:
        """Handle mouse leave event."""
        if self._enabled:
            self.current_color = self.colors[self.variant]["bg"]
            self.redraw()

    def _on_click(self, _: Any) -> None:
        """Handle click event."""
        if self._enabled and self.command:
            self.command()

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button."""
        self._enabled = enabled
        self.current_color = self.colors[self.variant]["bg"]
        self.redraw()


class ModernSlider(tk.Frame):
    """Custom slider widget with label and live value display."""

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        from_: float,
        to: float,
        default: float,
        unit: str = "",
        command: Optional[Callable[[float], None]] = None,
    ) -> None:
        """Initialize a modern styled slider."""
        super().__init__(parent, bg=THEME.bg_secondary)

        self.command = command
        self.unit = unit

        header = tk.Frame(self, bg=THEME.bg_secondary)
        header.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            header,
            text=label,
            font=(THEME.font_family, 10),
            fg=THEME.text_secondary,
            bg=THEME.bg_secondary,
        ).pack(side=tk.LEFT)

        self.value_label = tk.Label(
            header,
            font=(THEME.font_family, 10, "bold"),
            fg=THEME.accent_primary,
            bg=THEME.bg_secondary,
        )
        self.value_label.pack(side=tk.RIGHT)

        self.var = tk.DoubleVar(value=default)

        style = ttk.Style()
        style.configure(
            "Modern.Horizontal.TScale",
            background=THEME.bg_secondary,
            troughcolor=THEME.bg_tertiary,
            sliderrelief="flat",
        )

        self.slider = ttk.Scale(
            self,
            from_=from_,
            to=to,
            variable=self.var,
            orient=tk.HORIZONTAL,
            command=self._on_change,
            style="Modern.Horizontal.TScale",
        )
        self.slider.pack(fill=tk.X)

        self._update_label()

    def _on_change(self, value: str) -> None:
        """Handle slider value change."""
        self._update_label()
        if self.command:
            self.command(float(value))

    def _update_label(self) -> None:
        """Update the value label."""
        value = self.var.get()
        if self.unit == "%":
            self.value_label.config(text=f"{value:.0f}%")
        elif isinstance(value, float) and value != int(value):
            self.value_label.config(text=f"{value:.2f}{self.unit}")
        else:
            self.value_label.config(text=f"{int(value)}{self.unit}")

    def get(self) -> float:
        """Get the current slider value."""
        return self.var.get()


class ProgressRing(tk.Canvas):
    """Circular progress indicator widget."""

    def __init__(
        self, parent: tk.Widget, ring_size: int = 80, thickness: int = 6
    ) -> None:
        """Initialize a circular progress ring."""
        super().__init__(
            parent, width=ring_size, height=ring_size, bg=THEME.bg_secondary, highlightthickness=0
        )

        self.ring_size = ring_size
        self.thickness = thickness
        self.progress: float = 0
        self._draw()

    def _draw(self) -> None:
        """Redraw the progress ring."""
        self.delete("all")

        padding = 4
        x1, y1 = padding, padding
        x2, y2 = self.ring_size - padding, self.ring_size - padding

        self.create_arc(
            x1,
            y1,
            x2,
            y2,
            start=90,
            extent=-360,
            outline=THEME.bg_tertiary,
            width=self.thickness,
            style="arc",
        )

        if self.progress > 0:
            extent = -360 * (self.progress / 100)
            self.create_arc(
                x1,
                y1,
                x2,
                y2,
                start=90,
                extent=extent,
                outline=THEME.accent_primary,
                width=self.thickness,
                style="arc",
            )

        self.create_text(
            self.ring_size // 2,
            self.ring_size // 2,
            text=f"{int(self.progress)}%",
            fill=THEME.text_primary,
            font=(THEME.font_family, 14, "bold"),
        )

    def set_progress(self, value: float) -> None:
        """Set the progress value and redraw."""
        self.progress = min(100, max(0, value))
        self._draw()


# Main Application


class PhantomKeysApp:
    """Main application window for Phantom Keys typing simulator."""

    def __init__(self) -> None:
        """Initialize the application window and all UI components."""
        self.root = tk.Tk()
        self.root.title("Phantom Keys")
        self.root.configure(bg=THEME.bg_primary)
        self.root.resizable(False, False)

        window_width = 700
        window_height = 850
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.engine = TypingEngine()
        self.engine.progress_callback = self._update_progress
        self.engine.status_callback = self._update_status

        self.typing_thread: Optional[threading.Thread] = None
        self.countdown_active = False

        self._build_ui()
        self._setup_styles()

    def _setup_styles(self) -> None:
        """Configure ttk widget styles."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TScale", background=THEME.bg_secondary, troughcolor=THEME.bg_tertiary
        )

        style.configure(
            "Modern.TCheckbutton",
            background=THEME.bg_secondary,
            foreground=THEME.text_secondary,
            font=(THEME.font_family, 10),
        )
        style.map("Modern.TCheckbutton", background=[
                  ("active", THEME.bg_secondary)])

    def _build_ui(self) -> None:
        """Build the complete user interface."""
        # Header
        header = tk.Frame(self.root, bg=THEME.bg_primary)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))

        title_frame = tk.Frame(header, bg=THEME.bg_primary)
        title_frame.pack(anchor=tk.W)

        icon_label = tk.Label(
            title_frame,
            text="⌨",
            font=(THEME.font_family, 28),
            fg=THEME.accent_primary,
            bg=THEME.bg_primary,
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 12))

        text_frame = tk.Frame(title_frame, bg=THEME.bg_primary)
        text_frame.pack(side=tk.LEFT)

        tk.Label(
            text_frame,
            text="Phantom Keys",
            font=(THEME.font_family, 24, "bold"),
            fg=THEME.text_primary,
            bg=THEME.bg_primary,
        ).pack(anchor=tk.W)

        tk.Label(
            text_frame,
            text="Human-Like Typing Simulator",
            font=(THEME.font_family, 11),
            fg=THEME.text_muted,
            bg=THEME.bg_primary,
        ).pack(anchor=tk.W)

        # Main Content Card
        card = tk.Frame(self.root, bg=THEME.bg_secondary)
        card.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))

        # Text Input Section
        input_section = tk.Frame(card, bg=THEME.bg_secondary)
        input_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        section_header = tk.Frame(input_section, bg=THEME.bg_secondary)
        section_header.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            section_header,
            text="Text to Type",
            font=(THEME.font_family, 12, "bold"),
            fg=THEME.text_primary,
            bg=THEME.bg_secondary,
        ).pack(side=tk.LEFT)

        self.char_count_label = tk.Label(
            section_header,
            text="0 characters",
            font=(THEME.font_family, 10),
            fg=THEME.text_muted,
            bg=THEME.bg_secondary,
        )
        self.char_count_label.pack(side=tk.RIGHT)

        text_frame = tk.Frame(
            input_section, bg=THEME.border_color, padx=1, pady=1)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_entry = tk.Text(
            text_frame,
            font=(THEME.font_family_mono, 11),
            bg=THEME.bg_tertiary,
            fg=THEME.text_primary,
            insertbackground=THEME.accent_primary,
            selectbackground=THEME.accent_primary,
            selectforeground=THEME.text_primary,
            relief=tk.FLAT,
            padx=12,
            pady=12,
            wrap=tk.WORD,
            height=8,
        )
        self.text_entry.pack(fill=tk.BOTH, expand=True)
        self.text_entry.bind("<KeyRelease>", self._update_char_count)

        self.text_entry.insert(
            "1.0", "Enter the text you want to type here...")
        self.text_entry.bind("<FocusIn>", self._on_text_focus_in)
        self.text_entry.bind("<FocusOut>", self._on_text_focus_out)
        self.text_entry.config(fg=THEME.text_muted)

        # Settings Section
        settings_section = tk.Frame(card, bg=THEME.bg_secondary)
        settings_section.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Label(
            settings_section,
            text="Settings",
            font=(THEME.font_family, 12, "bold"),
            fg=THEME.text_primary,
            bg=THEME.bg_secondary,
        ).pack(anchor=tk.W, pady=(0, 16))

        settings_grid = tk.Frame(settings_section, bg=THEME.bg_secondary)
        settings_grid.pack(fill=tk.X)

        left_col = tk.Frame(settings_grid, bg=THEME.bg_secondary)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.wpm_slider = ModernSlider(
            left_col, "Typing Speed", 10, 150, 55, unit=" WPM"
        )
        self.wpm_slider.pack(fill=tk.X, pady=(0, 16))

        self.typo_slider = ModernSlider(
            left_col, "Typo Rate", 0, 20, 3, unit="%")
        self.typo_slider.pack(fill=tk.X)

        right_col = tk.Frame(settings_grid, bg=THEME.bg_secondary)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.variability_slider = ModernSlider(
            right_col, "Timing Variability", 0, 50, 35, unit="%"
        )
        self.variability_slider.pack(fill=tk.X, pady=(0, 16))

        self.delay_slider = ModernSlider(
            right_col, "Start Delay", 1, 10, 5, unit="s")
        self.delay_slider.pack(fill=tk.X)

        options_row = tk.Frame(settings_section, bg=THEME.bg_secondary)
        options_row.pack(fill=tk.X, pady=(16, 0))

        self.burst_mode_var = tk.BooleanVar(value=True)
        burst_check = ttk.Checkbutton(
            options_row,
            text="Burst Mode (occasional speed bursts)",
            variable=self.burst_mode_var,
            style="Modern.TCheckbutton",
        )
        burst_check.pack(side=tk.LEFT)

        # Progress & Status Section
        progress_section = tk.Frame(card, bg=THEME.bg_tertiary)
        progress_section.pack(fill=tk.X, padx=20, pady=(0, 20))

        progress_inner = tk.Frame(progress_section, bg=THEME.bg_tertiary)
        progress_inner.pack(fill=tk.X, padx=20, pady=20)

        self.progress_ring = ProgressRing(progress_inner)
        self.progress_ring.pack(side=tk.LEFT)

        status_frame = tk.Frame(progress_inner, bg=THEME.bg_tertiary)
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                          expand=True, padx=(20, 0))

        self.status_label = tk.Label(
            status_frame,
            text="Ready to type",
            font=(THEME.font_family, 12, "bold"),
            fg=THEME.text_primary,
            bg=THEME.bg_tertiary,
        )
        self.status_label.pack(anchor=tk.W)

        self.stats_label = tk.Label(
            status_frame,
            text="Click 'Start' and switch to your target window",
            font=(THEME.font_family, 10),
            fg=THEME.text_muted,
            bg=THEME.bg_tertiary,
            wraplength=350,
            justify=tk.LEFT,
        )
        self.stats_label.pack(anchor=tk.W, pady=(4, 0))

        self.countdown_label = tk.Label(
            status_frame,
            text="",
            font=(THEME.font_family, 14, "bold"),
            fg=THEME.accent_warning,
            bg=THEME.bg_tertiary,
        )
        self.countdown_label.pack(anchor=tk.W, pady=(8, 0))

        # Control Buttons
        controls = tk.Frame(card, bg=THEME.bg_secondary)
        controls.pack(fill=tk.X, padx=20, pady=(10, 20))

        buttons_frame = tk.Frame(controls, bg=THEME.bg_secondary)
        buttons_frame.pack()

        self.start_button = ModernButton(
            buttons_frame,
            text="Start",
            command=self._start_typing,
            variant="success",
            width=130,
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.pause_button = ModernButton(
            buttons_frame,
            text="Pause",
            command=self._toggle_pause,
            variant="primary",
            width=130,
        )
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))
        self.pause_button.set_enabled(False)

        self.stop_button = ModernButton(
            buttons_frame,
            text="Stop",
            command=self._stop_typing,
            variant="danger",
            width=130,
        )
        self.stop_button.pack(side=tk.LEFT)
        self.stop_button.set_enabled(False)

        # Footer
        footer = tk.Frame(self.root, bg=THEME.bg_primary)
        footer.pack(fill=tk.X, padx=30, pady=(0, 20))

        tk.Label(
            footer,
            text="Optimized for Google Docs - history will show natural typing progression",
            font=(THEME.font_family, 10),
            fg=THEME.text_muted,
            bg=THEME.bg_primary,
        ).pack()

    def _on_text_focus_in(self, _: Any) -> None:
        """Clear placeholder text when the text area receives focus."""
        if self.text_entry.get("1.0", tk.END).strip() == "Enter the text you want to type here...":
            self.text_entry.delete("1.0", tk.END)
            self.text_entry.config(fg=THEME.text_primary)

    def _on_text_focus_out(self, _: Any) -> None:
        """Restore placeholder text if the text area is empty."""
        if not self.text_entry.get("1.0", tk.END).strip():
            self.text_entry.insert(
                "1.0", "Enter the text you want to type here...")
            self.text_entry.config(fg=THEME.text_muted)

    def _update_char_count(self, _: Any = None) -> None:
        """Update the character and word count display."""
        text = self.text_entry.get("1.0", tk.END).strip()
        if text != "Enter the text you want to type here...":
            count = len(text)
            words = len(text.split())
            self.char_count_label.config(text=f"{count} chars, {words} words")
        else:
            self.char_count_label.config(text="0 characters")

    def _update_progress(self, value: float) -> None:
        """Update the progress ring display."""
        self.progress_ring.set_progress(value)

    def _update_status(self, message: str) -> None:
        """Update the status message and handle completion state."""
        self.status_label.config(text=message)

        if "complete" in message.lower():
            stats = self.engine.stats
            self.stats_label.config(
                text=f"Typed {stats['chars_typed']} chars, "
                f"{stats['words_completed']} words, "
                f"{stats['typos_made']} typos made"
            )
            self._reset_controls()

    def _countdown(self, seconds: int) -> None:
        """Display countdown before typing starts."""
        if seconds > 0 and self.countdown_active:
            self.countdown_label.config(text=f"Starting in {seconds}...")
            self.status_label.config(text="Switch to target window!")
            self.root.after(1000, lambda: self._countdown(seconds - 1))
        elif self.countdown_active:
            self.countdown_label.config(text="")
            self._execute_typing()

    def _start_typing(self) -> None:
        """Start the typing process."""
        text = self.text_entry.get("1.0", tk.END).strip()

        if not text or text == "Enter the text you want to type here...":
            messagebox.showwarning(
                "No Text", "Please enter some text to type.")
            return

        self.start_button.set_enabled(False)
        self.pause_button.set_enabled(True)
        self.stop_button.set_enabled(True)
        self.progress_ring.set_progress(0)

        self.countdown_active = True
        delay = int(self.delay_slider.get())
        self._countdown(delay)

    def _execute_typing(self) -> None:
        """Execute typing in a separate thread."""
        text = self.text_entry.get("1.0", tk.END).strip()

        self.typing_thread = threading.Thread(
            target=self.engine.type_text,
            args=(
                text,
                int(self.wpm_slider.get()),
                self.typo_slider.get() / 100,
                self.variability_slider.get() / 100,
                self.burst_mode_var.get(),
            ),
            daemon=True,
        )
        self.typing_thread.start()

    def _toggle_pause(self) -> None:
        """Toggle between paused and running states."""
        if self.engine.is_paused:
            self.engine.resume()
            self.pause_button.text = "Pause"
            self.pause_button.redraw()
            self.status_label.config(text="Typing resumed...")
        else:
            self.engine.pause()
            self.pause_button.text = "Resume"
            self.pause_button.redraw()
            self.status_label.config(text="Paused")

    def _stop_typing(self) -> None:
        """Stop typing immediately and reset UI state."""
        self.countdown_active = False
        self.engine.stop()
        self.countdown_label.config(text="")
        self._reset_controls()
        self.status_label.config(text="Stopped")
        self.stats_label.config(text="Typing was cancelled")

    def _reset_controls(self) -> None:
        """Reset all control buttons to initial state."""
        self.start_button.set_enabled(True)
        self.pause_button.set_enabled(False)
        self.stop_button.set_enabled(False)
        self.pause_button.text = "Pause"
        self.pause_button.redraw()

    def run(self) -> None:
        """Run the application."""
        self.root.mainloop()


# Entry Point

if __name__ == "__main__":
    app = PhantomKeysApp()
    app.run()
