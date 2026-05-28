import sys
from PyQt6.QtWidgets import QApplication
import config
from alert_manager import AlertManager
from main_window import MainWindow
from tray import TrayIcon
from notification import BreakNotification


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    alerts = config.load()
    manager = AlertManager(alerts)
    window = MainWindow(manager)
    tray = TrayIcon(window, manager)
    tray.show()

    def on_break(alert: dict):
        window.update_status(f"Break time! ({alert['name']})")
        notif = BreakNotification(
            alert["message"],
            alert.get("sound_path", ""),
            alert.get("sound_volume", 0.8),
        )
        notif.exec()
        window.update_status("Timer is running...")

    manager.alert_triggered.connect(on_break)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
