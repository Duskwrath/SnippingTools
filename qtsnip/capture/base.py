from __future__ import annotations

from abc import ABC, abstractmethod

from PySide6.QtGui import QImage

from ..models import CaptureMode


class CaptureError(RuntimeError):
    pass


class ScreenshotBackend(ABC):
    name: str

    @abstractmethod
    def capture(self, mode: CaptureMode) -> QImage:
        raise NotImplementedError
