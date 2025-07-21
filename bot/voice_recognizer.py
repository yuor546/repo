import librosa
import numpy as np

class VoiceRecognizer:
    """Simple voice recognition using MFCC similarity."""

    def __init__(self, n_mfcc: int = 20):
        self.n_mfcc = n_mfcc

    def extract(self, path: str) -> np.ndarray:
        y, sr = librosa.load(path, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
        return np.mean(mfcc, axis=1)

    def distance(self, a: np.ndarray, b: np.ndarray) -> float:
        return np.linalg.norm(a - b)

