from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor

from .models import CaptureMode, DEFAULT_IMAGE_FORMAT, DrawingOptions


class AppSettings:
    """Small typed facade around QSettings."""

    def __init__(self) -> None:
        self._settings = QSettings("OpenSnip", "OpenSnip")

    def value(self, key: str, default: object) -> object:
        return self._settings.value(key, default)

    @property
    def save_directory(self) -> Path:
        default = str(Path.home() / "Pictures")
        return Path(str(self.value("save_directory", default)))

    @save_directory.setter
    def save_directory(self, directory: Path) -> None:
        self._settings.setValue("save_directory", str(directory))

    @property
    def image_format(self) -> str:
        return str(self.value("image_format", DEFAULT_IMAGE_FORMAT)).lower()

    @image_format.setter
    def image_format(self, value: str) -> None:
        self._settings.setValue("image_format", value.lower())

    @property
    def capture_mode(self) -> CaptureMode:
        try:
            return CaptureMode(str(self.value("capture_mode", CaptureMode.RECTANGLE.value)))
        except ValueError:
            return CaptureMode.RECTANGLE

    @capture_mode.setter
    def capture_mode(self, mode: CaptureMode) -> None:
        self._settings.setValue("capture_mode", mode.value)

    @property
    def delay(self) -> int:
        return int(self.value("delay", 0))

    @delay.setter
    def delay(self, seconds: int) -> None:
        self._settings.setValue("delay", seconds)

    @property
    def auto_copy(self) -> bool:
        return str(self.value("auto_copy", False)).lower() in {"true", "1"}

    @auto_copy.setter
    def auto_copy(self, enabled: bool) -> None:
        self._settings.setValue("auto_copy", enabled)

    @property
    def auto_save(self) -> bool:
        return str(self.value("auto_save", False)).lower() in {"true", "1"}

    @auto_save.setter
    def auto_save(self, enabled: bool) -> None:
        self._settings.setValue("auto_save", enabled)

    def drawing_options(self) -> DrawingOptions:
        return DrawingOptions(
            QColor(str(self.value("pen_color", "#e53935"))),
            int(self.value("pen_width", 3)),
            QColor(str(self.value("highlighter_color", "#fff176"))),
            int(self.value("highlighter_width", 18)),
        )

    def save_drawing_options(self, options: DrawingOptions) -> None:
        self._settings.setValue("pen_color", options.pen_color.name())
        self._settings.setValue("pen_width", options.pen_width)
        self._settings.setValue("highlighter_color", options.highlighter_color.name())
        self._settings.setValue("highlighter_width", options.highlighter_width)
