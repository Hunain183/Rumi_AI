"""
GUI Widgets — Custom UI components for RUMI.

Includes chat bubbles, system monitor cards, memory viewers, etc.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QTextEdit, QFrame, QGridLayout, QDialog,
    QTableWidget, QTableWidgetItem,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextCursor
from datetime import datetime
import psutil

from rumi.gui import styles


class ChatMessage(QFrame):
    """A single chat message bubble (user or RUMI)."""

    def __init__(self, text: str, is_user: bool):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.setLineWidth(0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Courier", 10))

        # Styling
        if is_user:
            self.setStyleSheet(
                f"background-color: {styles.CYAN_PRIMARY}; "
                f"color: #000; border-radius: 12px 2px 12px 12px; padding: 10px;"
            )
            label.setStyleSheet("color: #000;")
        else:
            self.setStyleSheet(
                f"background-color: {styles.DARK_PANEL}; "
                f"color: {styles.TEXT_PRIMARY}; border-radius: 2px 12px 12px 12px; "
                f"border: 1px solid {styles.CYAN_DARK}; padding: 10px;"
            )

        layout.addWidget(label)
        self.setLayout(layout)


class ChatWindow(QWidget):
    """The main chat display and input area."""

    send_message = pyqtSignal(str)  # Emitted when user sends a message

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.messages = []  # List of {'role': 'user'|'assistant', 'text': str}

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ─── Chat Display ───────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ background-color: {styles.DARK_BG}; border: none; }}"
        )

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch()
        self.chat_container.setLayout(self.chat_layout)
        scroll.setWidget(self.chat_container)

        layout.addWidget(scroll, 1)

        # ─── Input Area ─────────────────────────────────────
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText(
            "Ask RUMI anything... (Ctrl+Enter to send)"
        )
        self.input_field.setMaximumHeight(60)
        self.input_field.keyPressEvent = self._on_input_key

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._on_send_clicked)
        self.send_btn.setMaximumWidth(100)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

        self.setLayout(layout)

    def add_message(self, text: str, is_user: bool):
        """Add a message to the chat display."""
        self.messages.append({"role": "user" if is_user else "assistant", "text": text})
        msg = ChatMessage(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg)

    def get_input(self) -> str:
        """Get and clear the input field."""
        text = self.input_field.toPlainText().strip()
        self.input_field.clear()
        return text

    def _on_send_clicked(self):
        text = self.get_input()
        if text:
            self.send_message.emit(text)

    def _on_input_key(self, event):
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._on_send_clicked()
        else:
            QTextEdit.keyPressEvent(self.input_field, event)


class SystemMonitor(QWidget):
    """Real-time system resource monitoring."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # ─── CPU Meter ──────────────────────────────────────
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU:")
        cpu_label.setFont(QFont("Courier", 10, QFont.Weight.Bold))
        self.cpu_value = QLabel("0%")
        self.cpu_value.setStyleSheet(f"color: {styles.ACCENT_GREEN};")
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_value)
        cpu_layout.addStretch()
        layout.addLayout(cpu_layout)

        # ─── RAM Meter ──────────────────────────────────────
        ram_layout = QHBoxLayout()
        ram_label = QLabel("RAM:")
        ram_label.setFont(QFont("Courier", 10, QFont.Weight.Bold))
        self.ram_value = QLabel("0%")
        self.ram_value.setStyleSheet(f"color: {styles.ACCENT_GREEN};")
        ram_layout.addWidget(ram_label)
        ram_layout.addWidget(self.ram_value)
        ram_layout.addStretch()
        layout.addLayout(ram_layout)

        # ─── Disk Meter ─────────────────────────────────────
        disk_layout = QHBoxLayout()
        disk_label = QLabel("Disk:")
        disk_label.setFont(QFont("Courier", 10, QFont.Weight.Bold))
        self.disk_value = QLabel("0%")
        self.disk_value.setStyleSheet(f"color: {styles.ACCENT_GREEN};")
        disk_layout.addWidget(disk_label)
        disk_layout.addWidget(self.disk_value)
        disk_layout.addStretch()
        layout.addLayout(disk_layout)

        # ─── Temperature (if available) ──────────────────────
        temp_layout = QHBoxLayout()
        temp_label = QLabel("Temp:")
        temp_label.setFont(QFont("Courier", 10, QFont.Weight.Bold))
        self.temp_value = QLabel("N/A")
        self.temp_value.setStyleSheet(f"color: {styles.TEXT_SECONDARY};")
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_value)
        temp_layout.addStretch()
        layout.addLayout(temp_layout)

        layout.addStretch()
        self.setLayout(layout)

    def update_stats(self):
        """Refresh system statistics."""
        # CPU
        cpu = psutil.cpu_percent(interval=0.1)
        color = styles.ACCENT_GREEN if cpu < 70 else styles.ACCENT_RED
        self.cpu_value.setText(f"{cpu}%")
        self.cpu_value.setStyleSheet(f"color: {color};")

        # RAM
        mem = psutil.virtual_memory()
        color = styles.ACCENT_GREEN if mem.percent < 70 else styles.ACCENT_RED
        self.ram_value.setText(f"{mem.percent}%")
        self.ram_value.setStyleSheet(f"color: {color};")

        # Disk
        disk = psutil.disk_usage("/")
        color = styles.ACCENT_GREEN if disk.percent < 80 else styles.ACCENT_RED
        self.disk_value.setText(f"{disk.percent}%")
        self.disk_value.setStyleSheet(f"color: {color};")

        # Temperature
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                first_temp = list(temps.values())[0][0].current
                self.temp_value.setText(f"{first_temp}°C")
        except:
            pass


class MemoryViewer(QWidget):
    """Display stored facts and conversation history."""

    def __init__(self, memory):
        super().__init__()
        self.memory = memory
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # ─── Facts Section ──────────────────────────────────
        facts_label = QLabel("Stored Facts")
        facts_label.setFont(QFont("Courier", 10, QFont.Weight.Bold))
        facts_label.setStyleSheet(f"color: {styles.CYAN_PRIMARY};")
        layout.addWidget(facts_label)

        self.facts_table = QTableWidget()
        self.facts_table.setColumnCount(2)
        self.facts_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.facts_table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {styles.DARK_PANEL};
                gridline-color: {styles.DARK_BG};
            }}
            QHeaderView::section {{
                background-color: {styles.DARK_BG};
                color: {styles.CYAN_PRIMARY};
                padding: 4px;
                border: none;
            }}
            """
        )
        self.facts_table.setMaximumHeight(150)
        layout.addWidget(self.facts_table)

        self.refresh_facts()

        layout.addStretch()
        self.setLayout(layout)

    def refresh_facts(self):
        """Reload facts from memory."""
        facts = self.memory.get_facts()
        self.facts_table.setRowCount(len(facts))

        for i, (key, value) in enumerate(facts.items()):
            self.facts_table.setItem(i, 0, QTableWidgetItem(key))
            self.facts_table.setItem(i, 1, QTableWidgetItem(str(value)[:100]))

        self.facts_table.resizeColumnsToContents()


class SettingsDialog(QDialog):
    """Settings and configuration modal."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RUMI Settings")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet(styles.STYLESHEET)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Placeholder for settings
        info = QLabel("Settings coming soon...")
        info.setStyleSheet(f"color: {styles.TEXT_SECONDARY};")
        layout.addWidget(info)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)
