# Abstract base detector interface
from abc import ABC, abstractmethod

class BaseDetector(ABC):
    @abstractmethod
    def analyze(self, image_path: str) -> dict:
        """Analyzes an image and returns a dictionary of results."""
        pass
