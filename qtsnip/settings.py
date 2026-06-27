from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor

from .models import DEFAULT_IMAGE_FORMAT, DrawingOptions


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
        color = self.value("stroke_color", self.value("pen_color", "#e53935"))
        width = self.value("stroke_width", self.value("pen_width", 3))
        return DrawingOptions(
            QColor(str(color)),
            int(width),
        )

    def save_drawing_options(self, options: DrawingOptions) -> None:
        self._settings.setValue("stroke_color", options.stroke_color.name())
        self._settings.setValue("stroke_width", options.stroke_width)
