import os
from gtts import gTTS
import tempfile

class TextToSpeech:
    """Generate speech audio from text using gTTS."""

    def __init__(self, lang: str = "en", slow: bool = False):
        self.lang = lang
        self.slow = slow

    def speak(self, text: str) -> str:
        """Convert text to speech and return the audio file path."""
        tts = gTTS(text=text, lang=self.lang, slow=self.slow)
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        tts.save(path)
        return path

