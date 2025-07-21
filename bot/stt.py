import os
import subprocess
import tempfile
import speech_recognition as sr

class SpeechToText:
    """Transcribe audio files using SpeechRecognition."""

    def __init__(self, lang: str = "en-US"):
        self.recognizer = sr.Recognizer()
        self.lang = lang

    def transcribe(self, path: str) -> str:
        """Return the transcription of the given audio file."""
        tmp_path = None
        if not path.lower().endswith(".wav"):
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
            os.close(tmp_fd)
            cmd = ["ffmpeg", "-y", "-i", path, tmp_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            use_path = tmp_path
        else:
            use_path = path
        with sr.AudioFile(use_path) as source:
            audio = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_sphinx(audio, language=self.lang)
        except Exception:
            text = ""
        if tmp_path:
            os.remove(tmp_path)
        return text
