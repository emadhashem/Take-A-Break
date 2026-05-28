# Take a Break

A lightweight cross-platform desktop app (Windows / macOS) that reminds you to take breaks at custom intervals. It lives in your system tray, plays a sound, and shows a popup — similar to how Discord or qBittorrent stay alive in the background when you close the window.

---

## Features

- Set a custom reminder interval (e.g. every 25 minutes)
- Write your own break message
- Pick any audio file (MP3, WAV, OGG, FLAC) as the reminder sound
- Control volume from the settings
- Countdown timer with progress bar visible in the main window
- Pause and resume the timer at any time
- Clicking X hides the window to the system tray — the app keeps running
- Double-click the tray icon to reopen the window
- Right-click the tray icon for quick Pause / Resume / Quit
- Settings are saved automatically to your home directory

---

## Requirements

- Python 3.10 or higher
- Windows 10+ or macOS 12+
- No global packages needed — everything runs inside a virtual environment

---

## Project Structure

```
take-a-break/
├── main.py               # Entry point — wires everything together
├── main_window.py        # Main UI window with countdown and controls
├── tray.py               # System tray icon and context menu
├── timer_controller.py   # Interval timer with pause/resume support
├── notification.py       # Break popup that appears on screen
├── settings_dialog.py    # Settings window (interval, message, sound)
├── audio.py              # Sound playback using pygame
├── config.py             # Load and save user config to disk
├── requirements.txt      # Python dependencies
├── assets/
│   └── sounds/           # Place your custom sound files here
└── venv/                 # Virtual environment (not committed to git)
```

---

## How to Set Up

### Step 1 — Clone or download the project

```
F:\My Staff\python\take-a-break\
```

### Step 2 — Create the virtual environment

Open a terminal inside the project folder and run:

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**macOS / Linux:**
```bash
python3 -m venv venv
```

### Step 3 — Install dependencies

**Windows:**
```powershell
.\venv\Scripts\pip install -r requirements.txt
```

**macOS / Linux:**
```bash
./venv/bin/pip install -r requirements.txt
```

This installs:
- `PyQt6` — the GUI framework (windows, tray, dialogs)
- `pygame` — audio playback
- `pyinstaller` — for building a standalone executable (optional)

> Nothing is installed globally on your machine. All packages stay inside the `venv/` folder.

---

## How to Run

**Windows:**
```powershell
.\venv\Scripts\python.exe main.py
```

**macOS / Linux:**
```bash
./venv/bin/python main.py
```

The app will open its main window and start counting down immediately.

---

## How to Use

### Main Window

| Element | What it does |
|---|---|
| Countdown (e.g. `24:13`) | Time remaining until the next break |
| Progress bar | Visual fill showing how far through the interval you are |
| Pause / Resume button | Stops or restarts the countdown |
| Settings button | Opens the settings dialog |
| X (close button) | Hides the window to the system tray — does **not** quit |

### System Tray

Right-click the tray icon for the quick menu:

| Option | What it does |
|---|---|
| Open | Brings the main window back |
| Pause Timer / Resume Timer | Toggle the countdown without opening the window |
| Quit | Fully exits the app |

Double-clicking the tray icon also reopens the main window.

### Settings Dialog

Open it with the **Settings** button in the main window.

| Setting | Description |
|---|---|
| Interval | How many minutes between each break reminder (1–480) |
| Break Message | The text shown on the popup when the timer fires |
| Sound File | Browse for any MP3, WAV, OGG, or FLAC file on your computer |
| Volume | Slider from 0–100%, with a Test button to preview |

Click **Save** to apply changes. The new interval takes effect immediately and the countdown resets.

### Break Notification

When the timer fires:
- A popup appears centered on screen, always on top of other windows
- Your chosen sound plays
- Click **Got it** to dismiss it, or it auto-closes after 30 seconds

---

## Configuration File

Settings are saved automatically to:

- **Windows:** `C:\Users\<you>\.take-a-break\config.json`
- **macOS/Linux:** `~/.take-a-break/config.json`

Example `config.json`:

```json
{
  "interval_minutes": 25,
  "message": "Time to take a break! Stand up and stretch.",
  "sound_path": "C:/Users/you/Music/bell.mp3",
  "sound_volume": 0.8
}
```

You can edit this file manually if needed. It is created on first save.

---

## Code Walkthrough

### `main.py` — Entry Point

Creates the `QApplication`, loads config, instantiates all components, and connects the timer signal to the break notification. Sets `setQuitOnLastWindowClosed(False)` so the app stays alive when the window is hidden.

### `config.py` — Config Management

Two simple functions: `load()` reads `config.json` and merges it with defaults, `save()` writes the current settings to disk. The config lives in the user's home directory so it persists across sessions.

### `timer_controller.py` — Timer

Wraps Qt's `QTimer`. Emits a `break_triggered` signal when the interval elapses. Exposes `start()`, `stop()`, `restart()`, and `set_interval()`. The signal/slot pattern means the timer is decoupled from the UI — it just fires and doesn't care what listens.

### `main_window.py` — Main UI

The main window has a separate 1-second `QTimer` that ticks the countdown display independently of the break timer. The `closeEvent` is overridden to call `event.ignore()` and `self.hide()` instead of closing — this is what makes the X button minimize to tray rather than quit.

### `tray.py` — System Tray

Creates a `QSystemTrayIcon` with a right-click context menu. Generates a fallback colored icon if no `assets/icon.png` is found. Double-click activates the show-window handler.

### `notification.py` — Break Popup

A frameless `QDialog` with `WindowStaysOnTopHint` so it appears above everything. A `QTimer.singleShot` auto-dismisses it after 30 seconds. Plays audio immediately on creation.

### `settings_dialog.py` — Settings UI

Reads the current config into form fields on open, writes back to the config dict on Save, and calls `config.save()` to persist. The sound Test button calls `audio.play()` directly so you can hear the sound without waiting for a break.

### `audio.py` — Audio Playback

Uses `pygame.mixer` loaded lazily on first use. Playback runs in a daemon thread so it never blocks the UI. Volume is clamped to `[0.0, 1.0]` before passing to pygame.

---

## Building a Standalone Executable

If you want a single file you can distribute without Python installed, use PyInstaller (already in the venv).

> **Important:** PyInstaller cannot cross-compile. Build on Windows to get a `.exe`, build on macOS to get a `.app`. You cannot build a Mac version from Windows or vice versa.

---

### Windows — `.exe`

Run this from the project folder in PowerShell:

```powershell
.\venv\Scripts\pyinstaller.exe `
  --noconsole `
  --onefile `
  --name "TakeABreak" `
  main.py
```

| Flag | What it does |
|---|---|
| `--noconsole` | Hides the black terminal window behind the GUI |
| `--onefile` | Bundles everything into a single `.exe` |
| `--name` | Name of the output file |

Output: `dist\TakeABreak.exe`

To include a custom icon (must be a `.ico` file):

```powershell
.\venv\Scripts\pyinstaller.exe `
  --noconsole `
  --onefile `
  --name "TakeABreak" `
  --icon "assets\icon.ico" `
  main.py
```

---

### macOS — `.app`

Run this from the project folder in Terminal:

```bash
# Single binary (no installer needed, just run it)
./venv/bin/pyinstaller \
  --noconsole \
  --onefile \
  --name "TakeABreak" \
  main.py
```

For a proper `.app` bundle you can drag into `/Applications`:

```bash
./venv/bin/pyinstaller \
  --windowed \
  --name "TakeABreak" \
  main.py
```

| Flag | What it does |
|---|---|
| `--noconsole` / `--windowed` | Hides the terminal, shows only the GUI |
| `--onefile` | Single binary output |
| `--name` | Name of the output app |

Output: `dist/TakeABreak` (binary) or `dist/TakeABreak.app` (bundle)

To include a custom icon (must be a `.icns` file):

```bash
./venv/bin/pyinstaller \
  --windowed \
  --name "TakeABreak" \
  --icon "assets/icon.icns" \
  main.py
```

To install it as a proper Mac app, drag the output to `/Applications`:

```bash
cp -r dist/TakeABreak.app /Applications/
```

---

### Output Structure After Build

```
take-a-break/
├── dist/
│   └── TakeABreak.exe   # Windows  (or TakeABreak.app on macOS)
├── build/               # PyInstaller temp files — safe to delete
└── TakeABreak.spec      # Build spec — keep if you want to rebuild later
```

The `dist/` folder is what you distribute. Everything else (`build/`, `.spec`) is build scaffolding.

---

## Adding a Custom Tray Icon

Place a `64x64` PNG file at:

```
assets/icon.png
```

The app loads it automatically. If the file is missing, a purple square with a "B" is used as the fallback.

---

## Troubleshooting

**App doesn't appear in the tray after closing the window**
Make sure you used the X button on the window, not Quit from the tray menu. The tray icon should be visible in the system tray area (bottom-right on Windows, top-right on macOS).

**No sound plays**
- Check that the file path in Settings is still valid
- Use the Test button in Settings to verify the file works
- Supported formats: MP3, WAV, OGG, FLAC

**Settings aren't saving**
The config is written to `~/.take-a-break/config.json`. Make sure your user account has write access to your home directory.

**PyQt6 or pygame import errors**
Make sure you are running with the venv Python, not the system Python:
```powershell
# Correct
.\venv\Scripts\python.exe main.py

# Wrong — uses system Python which has no packages
python main.py
```
