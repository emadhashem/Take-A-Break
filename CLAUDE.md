# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```powershell
# Windows
.\venv\Scripts\python.exe main.py

# macOS / Linux
./venv/bin/python main.py
```

## Setup

```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

## Building a Standalone Executable

```powershell
# Windows — produces dist\TakeABreak.exe
.\venv\Scripts\pyinstaller.exe --noconsole --onefile --name "TakeABreak" main.py

# With a custom icon (.ico on Windows, .icns on macOS)
.\venv\Scripts\pyinstaller.exe --noconsole --onefile --name "TakeABreak" --icon "assets\icon.ico" main.py
```

PyInstaller cannot cross-compile — build on the target OS. The existing `TakeABreak.spec` captures the last build configuration.

## Architecture

The app is a PyQt6 system-tray utility with no server or build step beyond PyInstaller packaging.

### Signal flow

```
AlertManager.alert_triggered  →  main.py:on_break  →  BreakNotification (modal dialog)
AlertManager.alerts_changed   →  AlertsDialog (rebuilds list)
                              →  MainWindow (implicit via manager queries)
```

### Key design points

**`AlertManager` (`alert_manager.py`) is the single source of truth.** It owns one `QTimer` per enabled alert. Every mutation (`add`, `update`, `remove`, `set_enabled`, `pause_all`, `resume_all`) immediately persists via `config.save()` and emits `alerts_changed`. Callers never write config directly.

**`next_alert()`** queries `QTimer.remainingTime()` across all active timers to find the soonest-firing alert. `MainWindow` polls this every second via its own 1-second `QTimer` to drive the countdown display.

**`config.py`** handles migration from the old single-alert flat format automatically on `load()`. The config file lives at `~/.take-a-break/config.json`.

**`audio.py`** initializes `pygame.mixer` lazily and plays sound in a daemon thread to avoid blocking the Qt event loop.

**`notification.py`** is a frameless `QDialog` with `WindowStaysOnTopHint`. It auto-dismisses after 30 seconds via `QTimer.singleShot`. Audio starts immediately on construction.

**`tray.py`** generates a fallback colored icon at runtime if `assets/icon.png` is absent.

**`app.setQuitOnLastWindowClosed(False)`** (set in `main.py`) is what keeps the process alive when the user closes the main window — the app hides to the tray instead of exiting.

### Alert dict schema

```json
{
  "id": "uuid-string",
  "name": "string",
  "interval_minutes": 25,
  "message": "string",
  "sound_path": "absolute path or empty string",
  "sound_volume": 0.8,
  "enabled": true
}
```

The `"default"` id is reserved for the built-in alert created on first run.
