from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QSpinBox, QSlider,
    QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import audio


class AlertEditor(QDialog):
    def __init__(self, alert: dict = None, parent=None):
        super().__init__(parent)
        self._alert = alert or {}
        self.setWindowTitle("Edit Alert" if alert else "New Alert")
        self.setFixedWidth(460)
        self.setStyleSheet(STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Edit Alert" if self._alert else "New Alert")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        name_group = QGroupBox("Alert Name")
        ng_layout = QHBoxLayout(name_group)
        self.name_edit = QLineEdit(self._alert.get("name", ""))
        self.name_edit.setPlaceholderText("e.g. Drink Water")
        ng_layout.addWidget(self.name_edit)
        layout.addWidget(name_group)

        interval_group = QGroupBox("Reminder Interval")
        ig_layout = QHBoxLayout(interval_group)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 480)
        self.interval_spin.setValue(self._alert.get("interval_minutes", 25))
        self.interval_spin.setSuffix(" min")
        ig_layout.addWidget(QLabel("Every"))
        ig_layout.addWidget(self.interval_spin)
        ig_layout.addStretch()
        layout.addWidget(interval_group)

        msg_group = QGroupBox("Reminder Message")
        mg_layout = QVBoxLayout(msg_group)
        self.msg_edit = QLineEdit(self._alert.get("message", ""))
        self.msg_edit.setPlaceholderText("Enter your reminder message...")
        mg_layout.addWidget(self.msg_edit)
        layout.addWidget(msg_group)

        sound_group = QGroupBox("Sound (optional)")
        sg_layout = QVBoxLayout(sound_group)

        file_row = QHBoxLayout()
        self.sound_path_edit = QLineEdit(self._alert.get("sound_path", ""))
        self.sound_path_edit.setPlaceholderText("No sound selected")
        self.sound_path_edit.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse)
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(60)
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(lambda: self.sound_path_edit.setText(""))
        file_row.addWidget(self.sound_path_edit)
        file_row.addWidget(browse_btn)
        file_row.addWidget(clear_btn)

        vol_row = QHBoxLayout()
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(self._alert.get("sound_volume", 0.8) * 100))
        self.vol_value_label = QLabel(f"{self.vol_slider.value()}%")
        self.vol_slider.valueChanged.connect(lambda v: self.vol_value_label.setText(f"{v}%"))
        test_btn = QPushButton("Test")
        test_btn.setFixedWidth(60)
        test_btn.setObjectName("secondary")
        test_btn.clicked.connect(self._test_sound)
        vol_row.addWidget(QLabel("Volume:"))
        vol_row.addWidget(self.vol_slider)
        vol_row.addWidget(self.vol_value_label)
        vol_row.addWidget(test_btn)

        sg_layout.addLayout(file_row)
        sg_layout.addLayout(vol_row)
        layout.addWidget(sound_group)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Sound File", "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)"
        )
        if path:
            self.sound_path_edit.setText(path)

    def _test_sound(self):
        audio.play(self.sound_path_edit.text(), self.vol_slider.value() / 100.0)

    def _save(self):
        if not self.name_edit.text().strip():
            self.name_edit.setFocus()
            return
        self.accept()

    def get_alert(self) -> dict:
        name = self.name_edit.text().strip()
        return {
            "name": name,
            "interval_minutes": self.interval_spin.value(),
            "message": self.msg_edit.text().strip() or f"Time for: {name}",
            "sound_path": self.sound_path_edit.text().strip(),
            "sound_volume": self.vol_slider.value() / 100.0,
            "enabled": self._alert.get("enabled", True),
        }


STYLE = """
    QDialog, QGroupBox {
        background-color: #2b2d31;
        color: #ffffff;
    }
    QGroupBox {
        border: 1px solid #3f4147;
        border-radius: 8px;
        margin-top: 8px;
        padding: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        color: #b5bac1;
    }
    QLabel { color: #dcddde; }
    QLineEdit, QSpinBox {
        background-color: #1e1f22;
        color: #ffffff;
        border: 1px solid #3f4147;
        border-radius: 4px;
        padding: 5px 8px;
    }
    QSlider::groove:horizontal {
        height: 4px;
        background: #3f4147;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        background: #5865f2;
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }
    QSlider::sub-page:horizontal {
        background: #5865f2;
        border-radius: 2px;
    }
    QPushButton {
        background-color: #5865f2;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 7px 16px;
    }
    QPushButton:hover { background-color: #4752c4; }
    QPushButton#secondary {
        background-color: #3f4147;
    }
    QPushButton#secondary:hover { background-color: #4f545c; }
    QPushButton#cancel {
        background-color: #3f4147;
    }
    QPushButton#cancel:hover { background-color: #4f545c; }
"""
