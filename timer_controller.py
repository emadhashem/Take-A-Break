from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TimerController(QObject):
    break_triggered = pyqtSignal()

    def __init__(self, interval_minutes: int):
        super().__init__()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.break_triggered)
        self._interval_ms = interval_minutes * 60 * 1000

    def set_interval(self, minutes: int):
        self._interval_ms = minutes * 60 * 1000
        if self._timer.isActive():
            self._timer.stop()
            self._timer.start(self._interval_ms)

    def start(self):
        self._timer.start(self._interval_ms)

    def stop(self):
        self._timer.stop()

    def is_running(self) -> bool:
        return self._timer.isActive()

    def restart(self):
        self._timer.stop()
        self._timer.start(self._interval_ms)
