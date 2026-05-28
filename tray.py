from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt6.QtCore import QSize


def _make_default_icon() -> QIcon:
    """Generate a simple colored square icon when no icon file is present."""
    px = QPixmap(QSize(64, 64))
    px.fill(QColor("#5865f2"))
    painter = QPainter(px)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(painter.font())
    painter.drawText(px.rect(), 0x84, "B")  # AlignCenter
    painter.end()
    return QIcon(px)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, app_window, timer_controller):
        icon_path = "assets/icon.png"
        try:
            icon = QIcon(icon_path)
            if icon.isNull():
                raise FileNotFoundError
        except Exception:
            icon = _make_default_icon()

        super().__init__(icon)
        self._window = app_window
        self._timer = timer_controller

        self._build_menu()
        self.activated.connect(self._on_activated)
        self.setToolTip("Take a Break")

    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2d31;
                color: #ffffff;
                border: 1px solid #3f4147;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item { padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background-color: #5865f2; }
            QMenu::separator { height: 1px; background: #3f4147; margin: 4px 0; }
        """)

        open_action = menu.addAction("Open")
        open_action.triggered.connect(self._show_window)

        menu.addSeparator()

        self.pause_action = menu.addAction("Pause Timer")
        self.pause_action.triggered.connect(self._toggle_pause)

        menu.addSeparator()

        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()

    def _toggle_pause(self):
        if self._timer.is_running():
            self._timer.stop()
            self.pause_action.setText("Resume Timer")
        else:
            self._timer.start()
            self.pause_action.setText("Pause Timer")
