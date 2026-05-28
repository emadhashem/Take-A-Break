from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import config


class AlertManager(QObject):
    alert_triggered = pyqtSignal(dict)
    alerts_changed = pyqtSignal()

    def __init__(self, alerts: list):
        super().__init__()
        self._alerts = alerts
        self._timers: dict[str, QTimer] = {}
        self._paused = False
        for alert in self._alerts:
            if alert["enabled"]:
                self._start_timer(alert)

    def _start_timer(self, alert: dict):
        timer = QTimer(self)
        timer.timeout.connect(lambda a=alert: self._fire(a))
        timer.start(alert["interval_minutes"] * 60 * 1000)
        self._timers[alert["id"]] = timer

    def _fire(self, alert: dict):
        current = next((a for a in self._alerts if a["id"] == alert["id"]), None)
        if current and current["enabled"]:
            self.alert_triggered.emit(current)

    def _stop_timer(self, alert_id: str):
        timer = self._timers.pop(alert_id, None)
        if timer:
            timer.stop()
            timer.deleteLater()

    # --- Queries ---

    def alerts(self) -> list:
        return self._alerts

    def is_paused(self) -> bool:
        return self._paused

    def next_alert(self) -> tuple:
        """Returns (alert_dict, remaining_ms) for the soonest-firing enabled alert."""
        best_alert = None
        best_remaining = float("inf")
        for alert in self._alerts:
            if not alert["enabled"]:
                continue
            timer = self._timers.get(alert["id"])
            if timer and timer.isActive():
                remaining = timer.remainingTime()
                if remaining < best_remaining:
                    best_remaining = remaining
                    best_alert = alert
        return best_alert, int(best_remaining) if best_alert else 0

    # --- Mutations ---

    def add(self, alert: dict):
        self._alerts.append(alert)
        if alert["enabled"] and not self._paused:
            self._start_timer(alert)
        config.save(self._alerts)
        self.alerts_changed.emit()

    def update(self, alert_id: str, updated: dict):
        for i, a in enumerate(self._alerts):
            if a["id"] == alert_id:
                self._alerts[i] = updated
                self._stop_timer(alert_id)
                if updated["enabled"] and not self._paused:
                    self._start_timer(updated)
                config.save(self._alerts)
                self.alerts_changed.emit()
                return

    def remove(self, alert_id: str):
        self._stop_timer(alert_id)
        self._alerts = [a for a in self._alerts if a["id"] != alert_id]
        config.save(self._alerts)
        self.alerts_changed.emit()

    def set_enabled(self, alert_id: str, enabled: bool):
        for a in self._alerts:
            if a["id"] == alert_id:
                a["enabled"] = enabled
                if enabled and not self._paused:
                    self._start_timer(a)
                else:
                    self._stop_timer(alert_id)
                config.save(self._alerts)
                self.alerts_changed.emit()
                return

    # --- Pause / Resume ---

    def pause_all(self):
        self._paused = True
        for timer in self._timers.values():
            timer.stop()

    def resume_all(self):
        self._paused = False
        for alert in self._alerts:
            if alert["enabled"]:
                timer = self._timers.get(alert["id"])
                if timer:
                    timer.start(alert["interval_minutes"] * 60 * 1000)
                else:
                    self._start_timer(alert)
