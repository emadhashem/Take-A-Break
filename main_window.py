from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QProgressBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCloseEvent
from alert_manager import AlertManager
from alerts_dialog import AlertsDialog


class MainWindow(QMainWindow):
    def __init__(self, manager: AlertManager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("Take a Break")
        self.setFixedSize(400, 300)
        self.setStyleSheet(STYLE)
        self._build_ui()
        self._start_tick()
        self.manager.alerts_changed.connect(self._refresh_display)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("Take a Break")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.alert_name_label = QLabel("")
        self.alert_name_label.setFont(QFont("Segoe UI", 10))
        self.alert_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alert_name_label.setObjectName("alertname")

        self.countdown_label = QLabel("--:--")
        self.countdown_label.setFont(QFont("Segoe UI Semibold", 22, QFont.Weight.Bold))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setObjectName("countdown")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)

        self.status_label = QLabel("Timer is running...")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("status")

        btn_row = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self._toggle_pause)
        alerts_btn = QPushButton("Manage Alerts")
        alerts_btn.setObjectName("secondary")
        alerts_btn.clicked.connect(self._open_alerts)
        btn_row.addWidget(self.pause_btn)
        btn_row.addWidget(alerts_btn)

        layout.addWidget(title)
        layout.addWidget(self.alert_name_label)
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addLayout(btn_row)

    def _start_tick(self):
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._refresh_display)
        self._tick_timer.start(1000)

    def _refresh_display(self):
        if self.manager.is_paused():
            return

        alert, remaining_ms = self.manager.next_alert()

        if alert is None:
            self.alert_name_label.setText("No active alerts")
            self.countdown_label.setText("--:--")
            self.progress.setValue(0)
            return

        total_ms = alert["interval_minutes"] * 60 * 1000
        mins, secs = divmod(remaining_ms // 1000, 60)
        pct = max(0, min(100, int(((total_ms - remaining_ms) / total_ms) * 100)))

        self.alert_name_label.setText(alert["name"])
        self.countdown_label.setText(f"{mins:02d}:{secs:02d}")
        self.progress.setValue(pct)

    def _toggle_pause(self):
        if not self.manager.is_paused():
            self.manager.pause_all()
            self.pause_btn.setText("Resume")
            self.status_label.setText("Timer paused.")
            self.countdown_label.setText("--:--")
            self.progress.setValue(0)
        else:
            self.manager.resume_all()
            self.pause_btn.setText("Pause")
            self.status_label.setText("Timer is running...")

    def _open_alerts(self):
        AlertsDialog(self.manager, parent=self).exec()

    def update_status(self, text: str):
        self.status_label.setText(text)

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()


STYLE = """
    QMainWindow, QWidget {
        background-color: #2b2d31;
        color: #ffffff;
    }
    QLabel { color: #dcddde; }
    QLabel#countdown { color: #5865f2; }
    QLabel#alertname { color: #b5bac1; font-size: 11px; }
    QLabel#status { color: #b5bac1; }
    QProgressBar {
        background-color: #1e1f22;
        border: none;
        border-radius: 4px;
    }
    QProgressBar::chunk {
        background-color: #5865f2;
        border-radius: 4px;
    }
    QPushButton {
        background-color: #5865f2;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 13px;
    }
    QPushButton:hover { background-color: #4752c4; }
    QPushButton#secondary {
        background-color: #3f4147;
    }
    QPushButton#secondary:hover { background-color: #4f545c; }
"""
