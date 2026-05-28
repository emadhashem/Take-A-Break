from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QProgressBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCloseEvent
import config
from settings_dialog import SettingsDialog
from timer_controller import TimerController


class MainWindow(QMainWindow):
    def __init__(self, cfg: dict, timer: TimerController):
        super().__init__()
        self.cfg = cfg
        self.timer = timer
        self._elapsed_ms = 0
        self._total_ms = cfg["interval_minutes"] * 60 * 1000

        self.setWindowTitle("Take a Break")
        self.setFixedSize(400, 300)
        self.setStyleSheet(STYLE)
        self._build_ui()
        self._start_progress_tick()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        title = QLabel("Take a Break")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Timer is running...")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("status")

        self.countdown_label = QLabel("")
        self.countdown_label.setFont(QFont("Segoe UI Semibold", 22, QFont.Weight.Bold))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setObjectName("countdown")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)

        btn_row = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self._toggle_pause)
        settings_btn = QPushButton("Settings")
        settings_btn.setObjectName("secondary")
        settings_btn.clicked.connect(self._open_settings)
        btn_row.addWidget(self.pause_btn)
        btn_row.addWidget(settings_btn)

        layout.addWidget(title)
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addLayout(btn_row)

    def _start_progress_tick(self):
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(1000)

    def _tick(self):
        if not self.timer.is_running():
            return
        self._elapsed_ms += 1000
        remaining = max(0, self._total_ms - self._elapsed_ms)
        pct = int((self._elapsed_ms / self._total_ms) * 100) if self._total_ms else 0
        self.progress.setValue(min(pct, 100))

        mins, secs = divmod(remaining // 1000, 60)
        self.countdown_label.setText(f"{mins:02d}:{secs:02d}")

        if remaining <= 0:
            self._elapsed_ms = 0

    def reset_progress(self):
        self._elapsed_ms = 0
        self._total_ms = self.cfg["interval_minutes"] * 60 * 1000
        self.progress.setValue(0)

    def _toggle_pause(self):
        if self.timer.is_running():
            self.timer.stop()
            self.pause_btn.setText("Resume")
            self.status_label.setText("Timer paused.")
        else:
            self.timer.start()
            self.pause_btn.setText("Pause")
            self.status_label.setText("Timer is running...")

    def _open_settings(self):
        dlg = SettingsDialog(self.cfg, parent=self)
        if dlg.exec():
            self.cfg = dlg.get_config()
            self.timer.set_interval(self.cfg["interval_minutes"])
            self.reset_progress()
            self._total_ms = self.cfg["interval_minutes"] * 60 * 1000

    def closeEvent(self, event: QCloseEvent):
        # Minimize to tray instead of quitting
        event.ignore()
        self.hide()

    def update_status(self, text: str):
        self.status_label.setText(text)


STYLE = """
    QMainWindow, QWidget {
        background-color: #2b2d31;
        color: #ffffff;
    }
    QLabel { color: #dcddde; }
    QLabel#countdown { color: #5865f2; }
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
