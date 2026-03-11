"""
Worker Thread — Runs the Brain without blocking the GUI.

PyQt6 requires long-running operations to happen on background threads
to keep the UI responsive. This worker runs the Brain's think() method
and emits signals when responses are ready.
"""

from PyQt6.QtCore import QThread, pyqtSignal


class BrainWorker(QThread):
    """Background thread that runs the Brain."""

    # Signals emitted back to the main window
    response_received = pyqtSignal(str)
    thinking_started = pyqtSignal()
    tool_called = pyqtSignal(str, dict)  # tool_name, args
    error_occurred = pyqtSignal(str)

    def __init__(self, brain, user_message: str):
        super().__init__()
        self.brain = brain
        self.user_message = user_message

    def run(self):
        """Execute the brain's think() method on this background thread."""
        try:
            self.thinking_started.emit()
            response = self.brain.think(self.user_message)
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))
