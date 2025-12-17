#  Plastdrakes Autoclicker 

A modern, sleek autoclicker for Windows with a sci-fi themed interface. Built for gaming and automation tasks with support for both mouse and keyboard clicking.

## Features

- **Modern UI** - Glowing cyan sci-fi design with rounded corners
- **Mouse & Keyboard** - Click any mouse button OR spam keyboard keys (Space, E, F, R, Enter)
- **Custom Hotkeys** - Set any key combination (Ctrl+X, Shift+F, etc.) to toggle clicking
- **Adjustable Speed** - Configure clicks per second (CPS)
- **Game Compatible** - Uses low-level Windows API for maximum compatibility
- **Randomized Timing** - Slight variations to avoid detection as a bot

## Installation

### Option 1: Download Pre-built Executable
Download `Plastdrakes Autoclicker.exe` from the [Releases](../../releases) page.

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/plastdrakes-autoclicker.git
cd plastdrakes-autoclicker

# Install Python 3.11+ and dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 3: Build Executable Yourself
```bash
pip install -r requirements.txt
pyinstaller --onefile --windowed --name "Plastdrakes Autoclicker" main.py
```

The executable will be in the `dist/` folder.

## Usage

1. **Launch** the application
2. **Configure Settings**:
   - Set your desired Clicks Per Second
   - Choose Mouse Button (Left/Right/Middle Click) OR Keyboard Key (Space/E/F/R/Enter)
   - Click the Hotkey field and press your desired key combination
3. **Position** your cursor where you want to click (for mouse) or focus the window (for keyboard)
4. **Press your hotkey** to start/stop the autoclicker
5. Status will show " ACTIVE " in green when clicking

## Hotkey Examples

- Single key: `X`, `F`, `Space`
- With Ctrl: `Ctrl+X`, `Ctrl+F`
- With Shift: `Shift+E`, `Shift+Space`
- With Alt: `Alt+R`
- Combinations: `Ctrl+Shift+F`

## Technical Details

- **Language**: Python 3.11
- **GUI Framework**: Tkinter
- **Input Simulation**: pywin32 (win32api)
- **Keyboard Listener**: pynput
- **Executable Packaging**: PyInstaller

## Requirements

- Windows 10/11
- Python 3.11+ (if running from source)

## License

This project is open source and available for personal use.

## Disclaimer

This tool is for educational and personal automation purposes. Use responsibly and in accordance with the terms of service of any games or applications you use it with.
