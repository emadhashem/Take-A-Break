import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import config
from timer_controller import TimerController
from main_window import MainWindow
from tray import TrayIcon
from notification import BreakNotification


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep alive when window is hidden

    cfg = config.load()

    timer = TimerController(cfg["interval_minutes"])
    window = MainWindow(cfg, timer)
    tray = TrayIcon(window, timer)
    tray.show()

    def on_break():
        window.reset_progress()
        window.update_status("Break time! See you in a moment...")
        notif = BreakNotification(
            cfg["message"],
            cfg.get("sound_path", ""),
            cfg.get("sound_volume", 0.8),
        )
        notif.exec()
        window.update_status("Timer is running...")

    timer.break_triggered.connect(on_break)
    timer.start()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
