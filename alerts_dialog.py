import uuid
from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QScrollArea, QWidget, QCheckBox, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from alert_manager import AlertManager
from alert_editor import AlertEditor


class AlertsDialog(QDialog):
    def __init__(self, manager: AlertManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Manage Alerts")
        self.setFixedSize(500, 480)
        self.setStyleSheet(STYLE)
        self._build_ui()
        self.manager.alerts_changed.connect(self._rebuild_list)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Alerts")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        add_btn = QPushButton("+ Add Alert")
        add_btn.setFixedWidth(110)
        add_btn.clicked.connect(self._add_alert)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.list_widget = QWidget()
        self.list_widget.setObjectName("listContainer")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()

        self.scroll_area.setWidget(self.list_widget)
        layout.addWidget(self.scroll_area)

        self._rebuild_list()

    def _rebuild_list(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        alerts = self.manager.alerts()
        if not alerts:
            empty = QLabel("No alerts yet. Click '+ Add Alert' to create one.")
            empty.setObjectName("empty")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.insertWidget(0, empty)
            return

        for alert in alerts:
            self.list_layout.insertWidget(self.list_layout.count() - 1, self._make_row(alert))

    def _make_row(self, alert: dict) -> QWidget:
        row = QFrame()
        row.setObjectName("alertRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 10, 12, 10)
        row_layout.setSpacing(10)

        toggle = QCheckBox()
        toggle.blockSignals(True)
        toggle.setChecked(alert["enabled"])
        toggle.blockSignals(False)
        toggle.clicked.connect(lambda checked, aid=alert["id"]: self.manager.set_enabled(aid, checked))

        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(alert["name"])
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        msg_text = alert["message"]
        if len(msg_text) > 45:
            msg_text = msg_text[:45] + "..."
        detail_lbl = QLabel(f'Every {alert["interval_minutes"]} min  •  {msg_text}')
        detail_lbl.setObjectName("detail")
        info.addWidget(name_lbl)
        info.addWidget(detail_lbl)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedWidth(60)
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(lambda _, a=alert: self._edit_alert(a))

        del_btn = QPushButton("Delete")
        del_btn.setFixedWidth(65)
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(lambda _, aid=alert["id"]: self._delete_alert(aid))

        row_layout.addWidget(toggle)
        row_layout.addLayout(info, stretch=1)
        row_layout.addWidget(edit_btn)
        row_layout.addWidget(del_btn)

        return row

    def _add_alert(self):
        dlg = AlertEditor(parent=self)
        if dlg.exec():
            alert = dlg.get_alert()
            alert["id"] = str(uuid.uuid4())
            self.manager.add(alert)

    def _edit_alert(self, alert: dict):
        current = next((a for a in self.manager.alerts() if a["id"] == alert["id"]), alert)
        dlg = AlertEditor(alert=current, parent=self)
        if dlg.exec():
            updated = dlg.get_alert()
            updated["id"] = alert["id"]
            self.manager.update(alert["id"], updated)

    def _delete_alert(self, alert_id: str):
        msg = QMessageBox(self)
        msg.setWindowTitle("Delete Alert")
        msg.setText("Delete this alert?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        msg.setStyleSheet(MSGBOX_STYLE)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.manager.remove(alert_id)


STYLE = """
    QDialog {
        background-color: #2b2d31;
        color: #ffffff;
    }
    QLabel { color: #dcddde; }
    QLabel#empty { color: #6d6f78; font-size: 12px; padding: 40px; }
    QFrame#alertRow {
        background-color: #1e1f22;
        border-radius: 8px;
    }
    QLabel#detail { color: #b5bac1; font-size: 11px; }
    QScrollArea, QWidget#listContainer { background-color: transparent; border: none; }
    QPushButton {
        background-color: #5865f2;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 12px;
    }
    QPushButton:hover { background-color: #4752c4; }
    QPushButton#secondary { background-color: #3f4147; }
    QPushButton#secondary:hover { background-color: #4f545c; }
    QPushButton#danger { background-color: #ed4245; }
    QPushButton#danger:hover { background-color: #c03537; }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid #5865f2;
        background: #1e1f22;
    }
    QCheckBox::indicator:checked { background: #5865f2; }
"""

MSGBOX_STYLE = """
    QMessageBox {
        background-color: #2b2d31;
        color: #ffffff;
    }
    QLabel { color: #dcddde; }
    QPushButton {
        background-color: #5865f2;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 6px 20px;
        min-width: 70px;
    }
    QPushButton:hover { background-color: #4752c4; }
"""
