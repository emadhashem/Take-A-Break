# Take a Break

A lightweight cross-platform desktop app (Windows / macOS) that reminds you to take breaks at custom intervals. It lives in your system tray, plays a sound, and shows a popup — similar to how Discord or qBittorrent stay alive in the background when you close the window.

---

## Features

- Create **multiple named alerts**, each with its own interval, message, and sound
- Enable or disable individual alerts without deleting them
- Set a custom reminder interval per alert (1–480 minutes)
- Write your own break message per alert
- Pick any audio file (MP3, WAV, OGG, FLAC) as the reminder sound per alert
- Control volume per alert, with a Test button to preview
- Countdown timer with progress bar showing the soonest-firing alert
- Alert name displayed below the countdown so you always know which one is next
- Pause and resume all timers at any time
- Clicking X hides the window to the system tray — the app keeps running
- Double-click the tray icon to reopen the window
- Right-click the tray icon for quick Pause / Resume / Quit
- Settings are saved automatically to your home directory
- Automatic migration from the old single-alert config format

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
├── alert_manager.py      # Manages multiple alert timers (add/update/remove/pause)
├── alert_editor.py       # Dialog for creating or editing a single alert
├── alerts_dialog.py      # Dialog listing all alerts with toggle/edit/delete
├── notification.py       # Break popup that appears on screen
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
| Countdown (e.g. `24:13`) | Time remaining until the next alert fires |
| Alert name (below countdown) | Name of the alert that will fire next |
| Progress bar | Visual fill showing how far through the interval you are |
| Pause / Resume button | Stops or restarts all alert timers |
| Manage Alerts button | Opens the Alerts dialog to create, edit, or delete alerts |
| X (close button) | Hides the window to the system tray — does **not** quit |

### System Tray

Right-click the tray icon for the quick menu:

| Option | What it does |
|---|---|
| Open | Brings the main window back |
| Pause Timer / Resume Timer | Toggle all timers without opening the window |
| Quit | Fully exits the app |

Double-clicking the tray icon also reopens the main window.

### Manage Alerts Dialog

Open it with the **Manage Alerts** button in the main window. It shows a scrollable list of all your alerts.

| Control | What it does |
|---|---|
| Checkbox | Enable or disable an alert without deleting it |
| Alert name + detail | Name, interval, and a preview of the message |
| Edit | Opens the Alert Editor for that alert |
| Delete | Removes the alert after a confirmation prompt |
| + Add Alert | Opens the Alert Editor to create a new alert |

### Alert Editor

Used for both creating and editing a single alert.

| Field | Description |
|---|---|
| Alert Name | A short label shown in the main window and the break notification (required) |
| Reminder Interval | How many minutes between each reminder for this alert (1–480) |
| Reminder Message | The text shown on the popup when the alert fires |
| Sound File | Browse for any MP3, WAV, OGG, or FLAC file; Clear to remove |
| Volume | Slider from 0–100%, with a Test button to preview the sound |

Click **Save** to apply. The timer for that alert restarts immediately with the new interval.

### Break Notification

When an alert fires:
- A popup appears centered on screen, always on top of other windows
- The alert's chosen sound plays
- Click **Got it** to dismiss it, or it auto-closes after 30 seconds

---

## Configuration File

Settings are saved automatically to:

- **Windows:** `C:\Users\<you>\.take-a-break\config.json`
- **macOS/Linux:** `~/.take-a-break/config.json`

Example `config.json`:

```json
{
  "alerts": [
    {
      "id": "default",
      "name": "Take a Break",
      "interval_minutes": 25,
      "message": "Time to take a break! Stand up and stretch.",
      "sound_path": "C:/Users/you/Music/bell.mp3",
      "sound_volume": 0.8,
      "enabled": true
    },
    {
      "id": "a1b2c3d4-...",
      "name": "Drink Water",
      "interval_minutes": 60,
      "message": "Drink a glass of water!",
      "sound_path": "",
      "sound_volume": 0.5,
      "enabled": true
    }
  ]
}
```

You can edit this file manually if needed. It is created on first save.

> **Migrating from an older version:** If your `config.json` uses the old single-alert format (`interval_minutes`, `message`, etc. at the top level), it is automatically converted to the new multi-alert format on the next launch. Your settings are preserved.

---

## Code Walkthrough

### `main.py` — Entry Point

Creates the `QApplication`, loads the alerts list from config, instantiates `AlertManager`, `MainWindow`, and `TrayIcon`, then connects `manager.alert_triggered` to the break notification handler. Sets `setQuitOnLastWindowClosed(False)` so the app stays alive when the window is hidden.

### `config.py` — Config Management

`load()` reads `config.json` and returns a list of alert dicts. If the file contains the old single-alert format, it is silently migrated. `save()` writes the current alerts list under the `"alerts"` key. The config lives in the user's home directory so it persists across sessions.

### `alert_manager.py` — Alert Manager

Replaces the old `timer_controller.py`. Manages one `QTimer` per enabled alert. Emits `alert_triggered(dict)` when an alert fires and `alerts_changed()` after any mutation. Exposes `add()`, `update()`, `remove()`, `set_enabled()`, `pause_all()`, `resume_all()`, and `next_alert()` (returns the soonest-firing alert and its remaining milliseconds). The manager is the single source of truth for alert state.

### `alerts_dialog.py` — Alerts List UI

A scrollable dialog that lists all alerts as card-style rows. Each row has an enable/disable checkbox, a name + detail label, an Edit button, and a Delete button (with confirmation). An **+ Add Alert** button in the header opens the `AlertEditor`. Rebuilds the list automatically whenever `alerts_changed` fires.

### `alert_editor.py` — Alert Editor UI

A form dialog used for both creating and editing a single alert. Fields: name, interval, message, sound file (with Browse / Clear), and volume (with a Test button). Validates that the name is not empty before accepting. Returns the filled-in alert dict via `get_alert()`.

### `main_window.py` — Main UI

The main window displays a countdown and the name of the next-firing alert. A 1-second `QTimer` calls `manager.next_alert()` each tick to refresh the display. The **Manage Alerts** button (replaces the old **Settings** button) opens `AlertsDialog`. The `closeEvent` is overridden to `hide()` instead of closing, keeping the app in the tray.

### `tray.py` — System Tray

Creates a `QSystemTrayIcon` with a right-click context menu. Pause/Resume now calls `manager.pause_all()` / `manager.resume_all()` and also syncs the main window's button label and status text. Generates a fallback colored icon if no `assets/icon.png` is found.

### `notification.py` — Break Popup

A frameless `QDialog` with `WindowStaysOnTopHint` so it appears above everything. A `QTimer.singleShot` auto-dismisses it after 30 seconds. Plays audio immediately on creation.

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
- Check that the file path in the Alert Editor is still valid
- Use the Test button in the Alert Editor to verify the file works
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
