"""
Main Window — The root GUI application.

Combines chat, system monitoring, and memory viewing in one elegant desktop app.
"""

import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QTabWidget, QPushButton, QStatusBar, QSplitter, QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup, QPauseAnimation
from PyQt6.QtGui import QFont, QIcon

from rumi.brain import Brain
from rumi.memory import Memory
from rumi.display import Display
from rumi.gui import styles
from rumi.gui.widgets import ChatWindow, SystemMonitor, MemoryViewer, SettingsDialog, JarvisCoreWidget, CommandHudWidget
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
        self._startup_group = None
        self.command_hud = None

        self.init_ui()
        self.init_timers()

        # ─── Graceful Shutdown ──────────────────────────────
        self.closing = False

    def init_ui(self):
        """Build the UI layout."""
        main_widget = QWidget()
        main_widget.setObjectName("rootPanel")
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ─── Left Side: Chat ─────────────────────────────────
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        # Title
        title = QLabel("RUMI // AI COMMAND INTERFACE")
        title.setObjectName("hudTitle")
        title.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        left_layout.addWidget(title)

        subtitle = QLabel("NEURAL LINK ACTIVE")
        subtitle.setObjectName("hudSubtitle")
        left_layout.addWidget(subtitle)

        # Chat window
        self.chat_window = ChatWindow()
        self.chat_window.send_message.connect(self._on_user_message)
        left_layout.addWidget(self.chat_window, 1)

        left_panel.setLayout(left_layout)
        self.left_panel = left_panel

        # ─── Center: JARVIS Core ───────────────────────────
        center_panel = QWidget()
        center_panel.setObjectName("leftPanel")
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(12, 12, 12, 12)
        center_layout.setSpacing(10)

        center_title = QLabel("ARC REACTOR CORE")
        center_title.setObjectName("hudSubtitle")
        center_layout.addWidget(center_title, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.jarvis_core = JarvisCoreWidget()
        center_layout.addWidget(self.jarvis_core, alignment=Qt.AlignmentFlag.AlignCenter)

        center_hint = QLabel("REAL-TIME COGNITIVE PROCESSING")
        center_hint.setObjectName("hudSubtitle")
        center_layout.addWidget(center_hint, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.command_hud = CommandHudWidget()
        self.command_hud.setMaximumHeight(220)
        center_layout.addWidget(self.command_hud)

        center_layout.addStretch()
        center_panel.setLayout(center_layout)
        self.center_panel = center_panel

        # ─── Right Side: Tabs (Monitor, Memory, Settings) ────
        right_tabs = QTabWidget()
        right_tabs.setObjectName("rightPanel")
        right_tabs.setMaximumWidth(280)
        self.right_tabs = right_tabs

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
        main_layout.addWidget(left_panel, 3)
        main_layout.addWidget(center_panel, 2)
        main_layout.addWidget(right_tabs, 0)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # ─── Status Bar ──────────────────────────────────────
        status = self.statusBar()
        status.showMessage(f"CONNECTED {config.LLM_MODEL} // VOICE {'ON' if config.VOICE_ENABLED else 'OFF'} // READY")

        self._run_startup_animation()

    def _fade_widget(self, widget, delay_ms: int):
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.0)
        widget.setGraphicsEffect(effect)

        sequence = QSequentialAnimationGroup(self)
        sequence.addAnimation(QPauseAnimation(delay_ms, self))

        fade = QPropertyAnimation(effect, b"opacity", self)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setDuration(520)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        sequence.addAnimation(fade)
        return sequence

    def _run_startup_animation(self):
        """Stagger panel reveal and restart center core boot scan."""
        self._startup_group = QParallelAnimationGroup(self)
        self._startup_group.addAnimation(self._fade_widget(self.left_panel, 50))
        self._startup_group.addAnimation(self._fade_widget(self.center_panel, 220))
        self._startup_group.addAnimation(self._fade_widget(self.right_tabs, 390))
        self._startup_group.start()
        self.jarvis_core.start_boot_sequence()

    def init_timers(self):
        """Set up background timers for system monitoring."""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_monitor)
        self.monitor_timer.start(2000)  # Update every 2 seconds

    def _on_user_message(self, message: str):
        """Callback when user sends a message."""
        self.jarvis_core.trigger_wake_word()

        confidence = self._estimate_command_confidence(message)
        source = "MIC" if config.VOICE_ENABLED and message.lower().startswith(("hey rumi", "rumi")) else "TEXT"
        self.command_hud.add_command(message, confidence, source=source)

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

    def _estimate_command_confidence(self, message: str) -> float:
        """Simple confidence heuristic for HUD display."""
        text = message.strip()
        if not text:
            return 0.35

        words = len(text.split())
        confidence = 0.68

        if 2 <= words <= 16:
            confidence += 0.14
        if text.endswith("?"):
            confidence += 0.05
        if len(text) > 140:
            confidence -= 0.12
        if any(token in text.lower() for token in ["maybe", "sort of", "idk"]):
            confidence -= 0.08

        return max(0.35, min(0.97, confidence))
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
