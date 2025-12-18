import threading
import time
import random
import tkinter as tk
from tkinter import ttk
from pynput import keyboard as pynput_keyboard
import win32api
import win32con
import json
import os
import sys
import winsound


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        root.title("✧ Plastdrakes Autoclicker ✧")
        root.configure(bg="#050a1f")
        root.resizable(False, False)

        # Configure modern sci-fi theme
        self.setup_theme()

        # Settings file path - use executable directory if frozen, otherwise script directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(app_dir, 'autoclicker_settings.json')

        # Load saved settings or use defaults
        saved_settings = self.load_settings()
        
        self.cps_var = tk.DoubleVar(value=saved_settings.get('cps', 10.0))
        self.button_var = tk.StringVar(value=saved_settings.get('button', 'Left Click'))
        self.hotkey_var = tk.StringVar(value=saved_settings.get('hotkey_display', 'x'))
        self.hotkey_combo = saved_settings.get('hotkey_combo', {"ctrl": False, "shift": False, "alt": False, "key": "x"})
        self.status_var = tk.StringVar(value="STANDBY")

        # Main container with rounded effect
        main = tk.Frame(root, bg="#050a1f", padx=35, pady=30)
        main.grid(row=0, column=0, sticky="nsew")
        main.bind('<Button-1>', lambda e: root.focus_set())

        # Title with glow effect
        title = tk.Label(main, text="✧ PLASTDRAKES AUTOCLICKER ✧", 
                        font=("Segoe UI", 16, "bold"),
                        bg="#050a1f", fg="#00ffff", cursor="hand2")
        title.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        title.bind('<Button-1>', lambda e: root.focus_set())

        # Settings container with single rounded background
        settings_container = tk.Frame(main, bg="#0d1635", highlightthickness=0, bd=0)
        settings_container.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        settings_container.grid_columnconfigure(0, weight=1)
        
        # Inner padding for settings
        settings_inner = tk.Frame(settings_container, bg="#0d1635", padx=30, pady=20, highlightthickness=0, bd=0)
        settings_inner.pack()
        settings_inner.grid_columnconfigure(1, weight=1)

        # Clicks per second
        cps_label = tk.Label(settings_inner, text="Clicks Per Second", 
                            font=("Segoe UI", 10),
                            bg="#0d1635", fg="#66d9ff", cursor="hand2")
        cps_label.grid(row=0, column=0, sticky="w", pady=10)
        cps_label.bind('<Button-1>', lambda e: root.focus_set())
        
        # Rounded entry container for CPS
        cps_container = tk.Frame(settings_inner, bg="#1a2a4a", highlightbackground="#00ddff", highlightthickness=2, highlightcolor="#00ddff")
        cps_container.grid(row=0, column=1, sticky="ew", pady=10, padx=(15, 0))
        cps_entry = tk.Entry(cps_container, textvariable=self.cps_var, 
                            width=15, font=("Segoe UI", 11),
                            bg="#1a2a4a", fg="#00ffff", insertbackground="#00ffff",
                            relief="flat", borderwidth=0, highlightthickness=0)
        cps_entry.pack(padx=8, pady=6, fill="both")
        cps_entry.bind('<FocusOut>', lambda e: self.save_settings())

        # Mouse button
        mb_label = tk.Label(settings_inner, text="Mouse Button", 
                           font=("Segoe UI", 10),
                           bg="#0d1635", fg="#66d9ff", cursor="hand2")
        mb_label.grid(row=1, column=0, sticky="w", pady=10)
        mb_label.bind('<Button-1>', lambda e: root.focus_set())
        
        # Mouse/Keyboard button dropdown with matching width
        button_container = tk.Frame(settings_inner, bg="#0d1635")
        button_container.grid(row=1, column=1, sticky="ew", pady=10, padx=(15, 0))
        button_menu = ttk.OptionMenu(button_container, self.button_var, "Left Click", 
                                     "Left Click", "Right Click", "Middle Click",
                                     "Space", "E", "F", "R", "Enter",
                                     command=lambda _: self.save_settings())
        button_menu.pack(fill="both")

        # Hotkey with click-to-capture
        hk_label = tk.Label(settings_inner, text="Hotkey Toggle", 
                           font=("Segoe UI", 10),
                           bg="#0d1635", fg="#66d9ff", cursor="hand2")
        hk_label.grid(row=2, column=0, sticky="w", pady=10)
        hk_label.bind('<Button-1>', lambda e: root.focus_set())
        
        # Rounded entry container for hotkey
        hotkey_container = tk.Frame(settings_inner, bg="#1a2a4a", highlightbackground="#00ddff", highlightthickness=2, highlightcolor="#00ddff")
        hotkey_container.grid(row=2, column=1, sticky="ew", pady=10, padx=(15, 0))
        
        self.hotkey_entry = tk.Entry(hotkey_container, textvariable=self.hotkey_var, 
                               width=15, font=("Segoe UI", 11),
                               bg="#1a2a4a", fg="#00ffff", insertbackground="#00ffff",
                               relief="flat", borderwidth=0, highlightthickness=0,
                               readonlybackground="#1a2a4a")
        self.hotkey_entry.pack(padx=8, pady=6, fill="both")
        self.hotkey_entry.bind('<Button-1>', lambda e: self.start_capture())
        self.hotkey_entry.bind('<KeyPress>', self.capture_hotkey)
        self.hotkey_entry.config(state="readonly")

        # Status display with glow
        status_container = tk.Frame(main, bg="#050a1f")
        status_container.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.status_label = tk.Label(status_container, textvariable=self.status_var, 
                                     font=("Segoe UI", 13, "bold"),
                                     bg="#050a1f", fg="#4dd0e1")
        self.status_label.pack()

        self._running = threading.Event()
        self._thread = None
        self._listener = None
        self._entry_focused = False

        # Track entry widgets
        self._entry_widgets = [cps_entry]
        for entry in self._entry_widgets:
            entry.bind('<FocusIn>', lambda e: self._on_entry_focus(True))
            entry.bind('<FocusOut>', lambda e: self._on_entry_focus(False))

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.start_keyboard_listener()

    def setup_theme(self):
        """Configure modern glowing sci-fi theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure OptionMenu with rounded modern look
        style.configure('TMenubutton', 
                       background='#1a2a4a', 
                       foreground='#00ffff',
                       borderwidth=0, 
                       relief='flat', 
                       font=('Segoe UI', 11),
                       padding=8)
        style.map('TMenubutton', 
                 background=[('active', '#2a4a6a')],
                 foreground=[('active', '#00ffff')])

    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            settings = {
                'cps': self.cps_var.get(),
                'button': self.button_var.get(),
                'hotkey_display': self.hotkey_var.get(),
                'hotkey_combo': self.hotkey_combo
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass

    def _on_entry_focus(self, focused):
        """Track when entry widgets have focus"""
        self._entry_focused = focused
    
    def start_capture(self):
        """Prepare to capture new hotkey"""
        self.hotkey_var.set("Press any key...")
        self.hotkey_entry.config(state="normal")
        self.hotkey_entry.focus_set()
    
    def capture_hotkey(self, event):
        """Capture hotkey combination including modifiers"""
        # Skip if the key is just a modifier by itself
        if event.keysym in ['Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R']:
            return "break"
        
        modifiers = []
        
        # Check for Control
        if event.state & 0x4:
            modifiers.append("Ctrl")
            self.hotkey_combo["ctrl"] = True
        else:
            self.hotkey_combo["ctrl"] = False
            
        # Check for Shift
        if event.state & 0x1:
            modifiers.append("Shift")
            self.hotkey_combo["shift"] = True
        else:
            self.hotkey_combo["shift"] = False
            
        # Check for Alt (only 0x20000, removed 0x0008 as it was causing false positives)
        if event.state & 0x20000:
            modifiers.append("Alt")
            self.hotkey_combo["alt"] = True
        else:
            self.hotkey_combo["alt"] = False
        
        # Get the key - always use keysym for consistency
        key = event.keysym.lower()
        self.hotkey_combo["key"] = key
        
        # Build display string
        if len(key) == 1:
            display_key = key.upper()
        else:
            display_key = key.capitalize()
        
        if modifiers:
            combo_str = "+".join(modifiers + [display_key])
        else:
            combo_str = display_key
            
        self.hotkey_var.set(combo_str)
        self.hotkey_entry.config(state="readonly")
        self.root.focus_set()
        self.save_settings()  # Save when hotkey is changed
        return "break"

    def get_button(self):
        """Returns tuple of (type, key_code) where type is 'mouse' or 'keyboard'"""
        b = self.button_var.get()
        
        # Mouse buttons
        if b == "Left Click":
            return ('mouse', win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP)
        if b == "Right Click":
            return ('mouse', win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP)
        if b == "Middle Click":
            return ('mouse', win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_MIDDLEUP)
        
        # Keyboard keys (VK codes)
        key_map = {
            "Space": 0x20,
            "E": 0x45,
            "F": 0x46,
            "R": 0x52,
            "Enter": 0x0D
        }
        if b in key_map:
            return ('keyboard', key_map[b])
        
        # Default to left click
        return ('mouse', win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP)

    def get_cps(self):
        try:
            val = float(self.cps_var.get())
            return max(0.1, val)
        except Exception:
            return 1.0

    def click_loop(self):
        while self._running.is_set():
            button_info = self.get_button()
            interval = 1.0 / self.get_cps()
            
            if button_info[0] == 'mouse':
                # Mouse clicking
                down, up = button_info[1], button_info[2]
                win32api.mouse_event(down, 0, 0, 0, 0)
                time.sleep(random.uniform(0.005, 0.015))
                win32api.mouse_event(up, 0, 0, 0, 0)
            else:
                # Keyboard pressing
                vk_code = button_info[1]
                win32api.keybd_event(vk_code, 0, 0, 0)  # Key down
                time.sleep(random.uniform(0.005, 0.015))
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
            
            # Add slight random variation to interval (±10%) to seem more human
            varied_interval = interval * random.uniform(0.9, 1.1)
            time.sleep(max(0.001, varied_interval))

    def start_clicking(self):
        if self._thread and self._thread.is_alive():
            return
        self._running.set()
        self._thread = threading.Thread(target=self.click_loop, daemon=True)
        self._thread.start()
        self.status_var.set("✦ ACTIVE ✦")
        self.status_label.config(fg="#00ff88", font=("Segoe UI", 13, "bold"))
        # Play activation sound (high pitch beep)
        threading.Thread(target=lambda: winsound.Beep(1200, 100), daemon=True).start()

    def stop_clicking(self):
        if not self._running.is_set():
            return
        self._running.clear()
        self.status_var.set("STANDBY")
        self.status_label.config(fg="#4dd0e1", font=("Segoe UI", 13, "bold"))
        # Play deactivation sound (low pitch beep)
        threading.Thread(target=lambda: winsound.Beep(800, 100), daemon=True).start()

    def toggle(self):
        if self._running.is_set():
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_keyboard_listener(self):
        """Start keyboard listener for hotkey toggle - non-suppressing mode"""
        self._current_modifiers = {"ctrl": False, "shift": False, "alt": False}
        
        def on_press(key):
            try:
                # Track modifier keys
                if key == pynput_keyboard.Key.ctrl_l or key == pynput_keyboard.Key.ctrl_r:
                    self._current_modifiers["ctrl"] = True
                    return True  # Don't suppress
                elif key == pynput_keyboard.Key.shift or key == pynput_keyboard.Key.shift_r:
                    self._current_modifiers["shift"] = True
                    return True  # Don't suppress
                elif key == pynput_keyboard.Key.alt_l or key == pynput_keyboard.Key.alt_r:
                    self._current_modifiers["alt"] = True
                    return True  # Don't suppress
                
                # Ignore hotkey when typing in entry fields
                if self._entry_focused:
                    return True  # Don't suppress
                
                # Get the key string - handle Ctrl combinations properly
                key_str = None
                
                # For regular character keys, use vk code to get the letter
                if hasattr(key, 'vk') and key.vk:
                    # VK codes 65-90 are A-Z
                    if 65 <= key.vk <= 90:
                        key_str = chr(key.vk).lower()
                    # VK codes 48-57 are 0-9
                    elif 48 <= key.vk <= 57:
                        key_str = chr(key.vk).lower()
                
                # Fallback to char if not a control character
                if not key_str and hasattr(key, 'char') and key.char and key.char.isprintable():
                    key_str = key.char.lower()
                
                # Fallback to name for special keys
                if not key_str and hasattr(key, 'name'):
                    key_str = key.name.lower()
                
                # Final fallback
                if not key_str:
                    try:
                        key_str = str(key).replace("'", "").lower()
                    except:
                        return True  # Don't suppress
                
                # Check if current key + modifiers match the hotkey combo
                if (key_str and key_str == self.hotkey_combo["key"] and
                    self._current_modifiers["ctrl"] == self.hotkey_combo["ctrl"] and
                    self._current_modifiers["shift"] == self.hotkey_combo["shift"] and
                    self._current_modifiers["alt"] == self.hotkey_combo["alt"]):
                    self.root.after(0, self.toggle)
                
                return True  # Don't suppress any keys
            except Exception:
                return True  # Don't suppress even on error
        
        def on_release(key):
            try:
                # Release modifier keys
                if key == pynput_keyboard.Key.ctrl_l or key == pynput_keyboard.Key.ctrl_r:
                    self._current_modifiers["ctrl"] = False
                elif key == pynput_keyboard.Key.shift or key == pynput_keyboard.Key.shift_r:
                    self._current_modifiers["shift"] = False
                elif key == pynput_keyboard.Key.alt_l or key == pynput_keyboard.Key.alt_r:
                    self._current_modifiers["alt"] = False
                return True  # Don't suppress
            except Exception:
                return True  # Don't suppress even on error
        
        # Create listener with suppress=False to ensure it never blocks keyboard input
        self._listener = pynput_keyboard.Listener(
            on_press=on_press, 
            on_release=on_release,
            suppress=False
        )
        self._listener.start()

    def on_close(self):
        try:
            if self._listener:
                self._listener.stop()
        except Exception:
            pass
        self.stop_clicking()
        self.save_settings()  # Save settings before closing
        self.root.destroy()


def main():
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
