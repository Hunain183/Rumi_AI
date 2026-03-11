"""
Voice — RUMI's ears and mouth.

Handles speech recognition (listening) and text-to-speech (speaking).
Gracefully falls back to text-only mode if audio hardware is missing.
Voice is 100% optional — RUMI works perfectly without it.
"""

import config


class Voice:
    """Voice I/O — listen via microphone, speak via TTS."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.available = False
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None

        if not enabled:
            return

        # ─── Set up speech recognition (ears) ────────────────
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            # Calibrate for background noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except (ImportError, OSError):
            self.recognizer = None
            self.microphone = None

        # ─── Set up text-to-speech (mouth) ───────────────────
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty("rate", config.VOICE_RATE)
            # Try to select a female voice (like Friday)
            voices = self.tts_engine.getProperty("voices")
            for voice in voices:
                if "female" in voice.name.lower():
                    self.tts_engine.setProperty("voice", voice.id)
                    break
        except (ImportError, OSError, RuntimeError):
            self.tts_engine = None

        # Both STT and TTS must work for voice mode
        self.available = (self.recognizer is not None and self.tts_engine is not None)

    def listen(self) -> str | None:
        """Listen for speech and convert it to text. Returns None on failure."""
        if not self.recognizer or not self.microphone:
            return None

        import speech_recognition as sr

        try:
            print("  🎤 Listening...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)

            text = self.recognizer.recognize_google(audio)
            print(f"  [Heard: {text}]")
            return text

        except sr.UnknownValueError:
            return None  # Couldn't understand the speech
        except sr.WaitTimeoutError:
            return None  # No speech detected
        except sr.RequestError as e:
            print(f"  [Speech recognition error: {e}]")
            return None

    def speak(self, text: str):
        """Convert text to speech and play it aloud."""
        if not self.tts_engine:
            return

        # Strip markdown formatting for cleaner speech
        clean = text.replace("**", "").replace("*", "").replace("`", "")
        clean = clean.replace("#", "").replace("•", "").replace("─", "")

        try:
            self.tts_engine.say(clean)
            self.tts_engine.runAndWait()
        except RuntimeError:
            pass  # TTS engine busy or crashed
