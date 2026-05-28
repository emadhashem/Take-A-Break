from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import audio


class BreakNotification(QDialog):
    def __init__(self, message: str, sound_path: str, volume: float):
        super().__init__()
        self.setWindowTitle("Take a Break")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setFixedSize(420, 200)
        self._center_on_screen()
        self._build_ui(message)
        audio.play(sound_path, volume)

    def _center_on_screen(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def _build_ui(self, message: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.setStyleSheet("""
            QDialog {
                background-color: #2b2d31;
                border: 2px solid #5865f2;
                border-radius: 12px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #5865f2;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)

        title = QLabel("Break Time!")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        msg = QLabel(message)
        msg.setFont(QFont("Segoe UI", 11))
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)

        btn = QPushButton("Got it")
        btn.setFixedWidth(120)
        btn.clicked.connect(self.accept)

        btn_layout_wrapper = QVBoxLayout()
        btn_layout_wrapper.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(msg)
        layout.addLayout(btn_layout_wrapper)

        # auto-close after 30 seconds
        QTimer.singleShot(30_000, self.accept)
