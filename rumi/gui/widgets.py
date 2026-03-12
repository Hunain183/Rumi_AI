"""
GUI Widgets — Custom UI components for RUMI.

Includes chat bubbles, system monitor cards, memory viewers, etc.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QTextEdit, QFrame, QGridLayout, QDialog,
    QTableWidget, QTableWidgetItem, QApplication, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QTextCursor, QPainter, QPen, QPainterPath, QPolygonF
import audioop
import math
import time
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
            self.setStyleSheet(styles.get_chat_message_css(True))
            label.setStyleSheet(f"color: {styles.CYAN_PRIMARY};")
        else:
            self.setStyleSheet(styles.get_chat_message_css(False))

        layout.addWidget(label)
        self.setLayout(layout)


class JarvisCoreWidget(QWidget):
    """Animated circular HUD core."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(220, 220)
        self.phase = 0
        self.boot_started_at = time.time()
        self.boot_duration = 2.8
        self.boot_scan_angle = 0
        self.audio_level = 0.0
        self.peak_level = 0.0
        self.levels = [0.15] * 48
        self.wake_pulse = 0.0
        self.wake_rings = []

        self._audio_stream = None
        self._audio_engine = None
        self._audio_enabled = False
        self._init_audio_input()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(40)

    def _init_audio_input(self):
        """Try to open microphone stream for visualizer input."""
        try:
            import pyaudio

            self._audio_engine = pyaudio.PyAudio()
            self._audio_stream = self._audio_engine.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024,
                stream_callback=self._on_audio_frame,
            )
            self._audio_stream.start_stream()
            self._audio_enabled = True
        except Exception:
            self._audio_stream = None
            self._audio_engine = None
            self._audio_enabled = False

    def _on_audio_frame(self, in_data, frame_count, time_info, status):
        """Process incoming PCM audio and keep a smoothed level."""
        try:
            import pyaudio

            rms = audioop.rms(in_data, 2) / 32768.0
            target = min(1.0, rms * 6.5)
            self.audio_level = (self.audio_level * 0.78) + (target * 0.22)
            return (None, pyaudio.paContinue)
        except Exception:
            return (None, 0)

    def _tick(self):
        self.phase = (self.phase + 2) % 360
        self.boot_scan_angle = (self.boot_scan_angle + 6) % 360

        # Fallback pulse if mic input is unavailable.
        if not self._audio_enabled:
            synthetic = (math.sin(math.radians(self.phase * 1.6)) + 1.0) * 0.35
            self.audio_level = (self.audio_level * 0.8) + (synthetic * 0.2)

        self.peak_level = max(self.audio_level, self.peak_level * 0.90)
        self.wake_pulse *= 0.90

        if self.wake_pulse > 0.5 and len(self.wake_rings) < 4:
            self.wake_rings.append(0.0)

        for i in range(len(self.wake_rings)):
            self.wake_rings[i] += 0.04
        self.wake_rings = [ring for ring in self.wake_rings if ring <= 1.2]

        base = max(0.08, min(1.0, self.audio_level))
        for i in range(len(self.levels)):
            wave = (math.sin(math.radians(self.phase * 2.0 + (i * 17))) + 1.0) * 0.5
            target = 0.12 + (base * 0.85 * wave)
            self.levels[i] = (self.levels[i] * 0.72) + (target * 0.28)

        self.update()

    def start_boot_sequence(self):
        """Restart startup scan effect."""
        self.boot_started_at = time.time()
        for delay in (0, 220, 460):
            QTimer.singleShot(delay, QApplication.beep)

    def trigger_wake_word(self):
        """Simulate a wake-word pulse burst around the core."""
        self.wake_pulse = 1.0
        self.wake_rings = [0.0]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self.height())
        cx = self.width() / 2
        cy = self.height() / 2

        outer = size * 0.43
        middle = size * 0.32
        core = size * 0.18
        bar_base = size * 0.47
        bar_max = size * 0.11

        painter.fillRect(self.rect(), QColor(styles.HUD_BG))

        flash = min(1.0, self.peak_level * 1.2)
        ring_color = QColor(
            int(68 + (187 * flash)),
            int(240 + (15 * flash)),
            255,
        )
        ring_soft = QColor(styles.CYAN_DARK)

        pen_outer = QPen(ring_color, 2)
        painter.setPen(pen_outer)
        painter.drawEllipse(int(cx - outer), int(cy - outer), int(outer * 2), int(outer * 2))

        pen_middle = QPen(ring_soft, 2)
        painter.setPen(pen_middle)
        painter.drawEllipse(int(cx - middle), int(cy - middle), int(middle * 2), int(middle * 2))

        # Circular audio bars around the outer ring.
        bar_pen = QPen(QColor(styles.CYAN_PRIMARY), 2)
        painter.setPen(bar_pen)
        for idx, level in enumerate(self.levels):
            angle = (360 / len(self.levels)) * idx
            rad = math.radians(angle)
            sx = cx + math.cos(rad) * bar_base
            sy = cy + math.sin(rad) * bar_base
            ex = cx + math.cos(rad) * (bar_base + (bar_max * level))
            ey = cy + math.sin(rad) * (bar_base + (bar_max * level))
            painter.drawLine(int(sx), int(sy), int(ex), int(ey))

        # Rotating arc gives the core a live scanning effect.
        arc_pen = QPen(ring_color, 4)
        painter.setPen(arc_pen)
        painter.drawArc(
            int(cx - outer),
            int(cy - outer),
            int(outer * 2),
            int(outer * 2),
            self.phase * 16,
            72 * 16,
        )

        elapsed = time.time() - self.boot_started_at
        if elapsed < self.boot_duration:
            progress = elapsed / self.boot_duration
            scan_alpha = int((1.0 - progress) * 220)
            scan_pen = QPen(QColor(68, 240, 255, scan_alpha), 5)
            painter.setPen(scan_pen)
            painter.drawArc(
                int(cx - outer * 1.02),
                int(cy - outer * 1.02),
                int((outer * 1.02) * 2),
                int((outer * 1.02) * 2),
                self.boot_scan_angle * 16,
                36 * 16,
            )

        if self.wake_pulse > 0.04:
            for ring in self.wake_rings:
                radius_scale = 1.0 + (ring * 0.55)
                alpha = max(0, int((1.0 - ring) * 190))
                pulse_pen = QPen(QColor(98, 255, 159, alpha), 2)
                painter.setPen(pulse_pen)
                ring_radius = outer * radius_scale
                painter.drawEllipse(
                    int(cx - ring_radius),
                    int(cy - ring_radius),
                    int(ring_radius * 2),
                    int(ring_radius * 2),
                )

        pulse = int((self.phase % 180) / 180 * 80) + 90
        center_color = QColor(
            int(68 + (170 * flash)),
            int(240 + (15 * flash)),
            255,
            pulse,
        )
        painter.setBrush(center_color)
        painter.setPen(QPen(QColor(styles.CYAN_PRIMARY), 1))
        painter.drawEllipse(int(cx - core), int(cy - core), int(core * 2), int(core * 2))

        cross_pen = QPen(QColor(styles.CYAN_DARK), 1)
        painter.setPen(cross_pen)
        painter.drawLine(int(cx - outer * 0.9), int(cy), int(cx + outer * 0.9), int(cy))
        painter.drawLine(int(cx), int(cy - outer * 0.9), int(cx), int(cy + outer * 0.9))

        status_text = "LISTENING" if self.audio_level > 0.14 else "IDLE"
        status_color = QColor(styles.ACCENT_GREEN) if status_text == "LISTENING" else QColor(styles.TEXT_SECONDARY)
        painter.setPen(QPen(status_color, 1))
        painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        painter.drawText(
            int(cx - 72),
            int(cy + outer + 26),
            144,
            20,
            int(Qt.AlignmentFlag.AlignCenter),
            f"AUDIO: {status_text}",
        )

    def closeEvent(self, event):
        """Release microphone resources when widget closes."""
        try:
            if self._audio_stream is not None:
                self._audio_stream.stop_stream()
                self._audio_stream.close()
            if self._audio_engine is not None:
                self._audio_engine.terminate()
        except Exception:
            pass
        super().closeEvent(event)


class SparklineWidget(QWidget):
    """Lightweight holographic sparkline for telemetry."""

    def __init__(self, color: str, points: int = 48):
        super().__init__()
        self.setMinimumHeight(42)
        self._color = QColor(color)
        self._points = points
        self._history = [0.0] * points

    def set_value(self, value: float):
        value = max(0.0, min(100.0, float(value)))
        self._history.append(value)
        if len(self._history) > self._points:
            self._history = self._history[-self._points:]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.fillRect(rect, QColor(10, 27, 47, 120))

        grid_pen = QPen(QColor(20, 155, 180, 70), 1)
        painter.setPen(grid_pen)
        thirds = [rect.top() + rect.height() // 3, rect.top() + (2 * rect.height()) // 3]
        for y in thirds:
            painter.drawLine(rect.left(), y, rect.right(), y)

        if len(self._history) < 2:
            return

        step = rect.width() / max(1, len(self._history) - 1)
        points = QPolygonF()
        for idx, value in enumerate(self._history):
            x = rect.left() + (idx * step)
            y = rect.bottom() - ((value / 100.0) * rect.height())
            points.append(Qt.QPointF(x, y))

        line_pen = QPen(self._color, 2)
        painter.setPen(line_pen)
        painter.drawPolyline(points)

        glow_pen = QPen(QColor(self._color.red(), self._color.green(), self._color.blue(), 70), 5)
        painter.setPen(glow_pen)
        painter.drawPolyline(points)


class CommandHudWidget(QWidget):
    """Overlay panel for command history and confidence indicators."""

    def __init__(self):
        super().__init__()
        self._max_items = 8
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title = QLabel("VOICE COMMAND HUD")
        title.setStyleSheet(f"color: {styles.CYAN_PRIMARY}; font-weight: bold;")
        layout.addWidget(title)

        self.command_list = QListWidget()
        self.command_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: rgba(7, 21, 35, 180);
                border: 1px solid {styles.CYAN_DARK};
                border-radius: 8px;
                padding: 4px;
            }}
            QListWidget::item {{
                border-bottom: 1px solid rgba(68, 240, 255, 40);
                padding: 4px;
            }}
            """
        )
        layout.addWidget(self.command_list)
        self.setLayout(layout)

    def add_command(self, text: str, confidence: float, source: str = "TEXT"):
        ts = datetime.now().strftime("%H:%M:%S")
        clean = " ".join(text.split())
        if len(clean) > 52:
            clean = clean[:49] + "..."

        conf_pct = int(max(0.0, min(1.0, confidence)) * 100)
        label = f"[{ts}] {source}  {conf_pct}%  |  {clean}"
        item = QListWidgetItem(label)

        if conf_pct >= 82:
            item.setForeground(QColor(styles.ACCENT_GREEN))
        elif conf_pct >= 60:
            item.setForeground(QColor(styles.CYAN_PRIMARY))
        else:
            item.setForeground(QColor(styles.ACCENT_RED))

        self.command_list.insertItem(0, item)
        while self.command_list.count() > self._max_items:
            self.command_list.takeItem(self.command_list.count() - 1)


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
            f"QScrollArea {{ background-color: {styles.HUD_BG}; border: 1px solid {styles.CYAN_DARK}; border-radius: 8px; }}"
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
        title = QLabel("SYSTEM TELEMETRY")
        title.setStyleSheet(f"color: {styles.CYAN_PRIMARY}; font-weight: bold;")
        layout.addWidget(title)

        self.cpu_graph = SparklineWidget(styles.ACCENT_GREEN)
        self.ram_graph = SparklineWidget(styles.CYAN_PRIMARY)
        self.disk_graph = SparklineWidget(styles.ACCENT_RED)

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
        layout.addWidget(self.cpu_graph)

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
        layout.addWidget(self.ram_graph)

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
        layout.addWidget(self.disk_graph)

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
        self.cpu_graph.set_value(cpu)

        # RAM
        mem = psutil.virtual_memory()
        color = styles.ACCENT_GREEN if mem.percent < 70 else styles.ACCENT_RED
        self.ram_value.setText(f"{mem.percent}%")
        self.ram_value.setStyleSheet(f"color: {color};")
        self.ram_graph.set_value(mem.percent)

        # Disk
        disk = psutil.disk_usage("/")
        color = styles.ACCENT_GREEN if disk.percent < 80 else styles.ACCENT_RED
        self.disk_value.setText(f"{disk.percent}%")
        self.disk_value.setStyleSheet(f"color: {color};")
        self.disk_graph.set_value(disk.percent)

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
                background-color: {styles.PANEL_BG};
                gridline-color: {styles.HUD_BG};
                border: 1px solid {styles.CYAN_DARK};
            }}
            QHeaderView::section {{
                background-color: {styles.HUD_BG};
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
