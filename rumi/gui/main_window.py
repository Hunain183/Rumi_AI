"""
Main Window — The root GUI application.

Combines chat, system monitoring, and memory viewing in one elegant desktop app.
"""

import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QTabWidget, QPushButton, QStatusBar, QSplitter,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon

from rumi.brain import Brain
from rumi.memory import Memory
from rumi.display import Display
from rumi.gui import styles
from rumi.gui.widgets import ChatWindow, SystemMonitor, MemoryViewer, SettingsDialog
from rumi.gui.worker import BrainWorker
import config


class RumiMainWindow(QMainWindow):
    """Main application window for RUMI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RUMI — Personal AI Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(styles.STYLESHEET)

        # ─── Initialize Backend ─────────────────────────────
        self.memory = Memory(config.MEMORY_DB)
        self.display = Display()  # For compatibility, though we use GUI
        self.brain = Brain(memory=self.memory, display=self.display)

        # ─── UI Components ──────────────────────────────────
        self.chat_window = None
        self.system_monitor = None
        self.memory_viewer = None
        self.brain_worker = None

        self.init_ui()
        self.init_timers()

        # ─── Graceful Shutdown ──────────────────────────────
        self.closing = False

    def init_ui(self):
        """Build the UI layout."""
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ─── Left Side: Chat ─────────────────────────────────
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Title
        title = QLabel("RUMI")
        title.setFont(QFont("Courier", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {styles.CYAN_PRIMARY};")
        left_layout.addWidget(title)

        # Chat window
        self.chat_window = ChatWindow()
        self.chat_window.send_message.connect(self._on_user_message)
        left_layout.addWidget(self.chat_window, 1)

        left_panel.setLayout(left_layout)

        # ─── Right Side: Tabs (Monitor, Memory, Settings) ────
        right_tabs = QTabWidget()
        right_tabs.setMaximumWidth(280)

        # System Monitor Tab
        self.system_monitor = SystemMonitor()
        right_tabs.addTab(self.system_monitor, "Monitor")

        # Memory Tab
        self.memory_viewer = MemoryViewer(self.memory)
        right_tabs.addTab(self.memory_viewer, "Memory")

        # Settings Tab (placeholder)
        settings_label = QLabel("Settings\n\nMore options coming soon...")
        settings_label.setStyleSheet(f"color: {styles.TEXT_SECONDARY};")
        right_tabs.addTab(settings_label, "Settings")

        # ─── Combine Left & Right ────────────────────────────
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_tabs, 0)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # ─── Status Bar ──────────────────────────────────────
        status = self.statusBar()
        status.setStyleSheet(f"background-color: {styles.DARK_PANEL}; color: {styles.TEXT_SECONDARY};")
        status.showMessage(f"Connected to {config.LLM_MODEL} • Voice: {'ON' if config.VOICE_ENABLED else 'OFF'}")

    def init_timers(self):
        """Set up background timers for system monitoring."""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_monitor)
        self.monitor_timer.start(2000)  # Update every 2 seconds

    def _on_user_message(self, message: str):
        """Callback when user sends a message."""
        # Add to chat display
        self.chat_window.add_message(message, is_user=True)

        # Disable input while processing
        self.chat_window.input_field.setEnabled(False)
        self.chat_window.send_btn.setText("Processing...")
        self.chat_window.send_btn.setEnabled(False)

        # Run the brain in a background thread
        self.brain_worker = BrainWorker(self.brain, message)
        self.brain_worker.response_received.connect(self._on_brain_response)
        self.brain_worker.thinking_started.connect(self._on_brain_thinking)
        self.brain_worker.error_occurred.connect(self._on_brain_error)
        self.brain_worker.start()

    def _on_brain_thinking(self):
        """Called when the brain starts processing."""
        pass  # The "Processing..." text is already shown

    def _on_brain_response(self, response: str):
        """Callback when the brain has a response."""
        self.chat_window.add_message(response, is_user=False)

        # Re-enable input
        self.chat_window.input_field.setEnabled(True)
        self.chat_window.send_btn.setText("Send")
        self.chat_window.send_btn.setEnabled(True)
        self.chat_window.input_field.setFocus()

        # Refresh memory viewer if facts changed
        self.memory_viewer.refresh_facts()

    def _on_brain_error(self, error: str):
        """Callback when the brain encounters an error."""
        self.chat_window.add_message(f"⚠ Error: {error}", is_user=False)

        # Re-enable input
        self.chat_window.input_field.setEnabled(True)
        self.chat_window.send_btn.setText("Send")
        self.chat_window.send_btn.setEnabled(True)

    def _update_monitor(self):
        """Update system monitor stats."""
        if self.system_monitor:
            self.system_monitor.update_stats()

    def closeEvent(self, event):
        """Handle graceful shutdown."""
        self.memory.close()
        event.accept()


def launch_gui():
    """Start the RUMI GUI application."""
    app = QApplication(sys.argv)

    window = RumiMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()
