from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class CaptureMode(str, Enum):
    RECTANGLE = "rectangle"
    FULLSCREEN = "fullscreen"
    WINDOW = "window"
    FREEFORM = "freeform"

    @property
    def label(self) -> str:
        return {
            self.RECTANGLE: "Rectangle mode",
            self.FULLSCREEN: "Full screen mode",
            self.WINDOW: "Window mode",
            self.FREEFORM: "Freeform mode",
        }[self]


class Tool(str, Enum):
    ERASER = "eraser"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    ARROW = "arrow"
    TEXT = "text"
    CROP = "crop"


@dataclass
class DrawingOptions:
    stroke_color: QColor = field(default_factory=lambda: QColor("#e53935"))
    stroke_width: int = 3


@dataclass
class LaunchOptions:
    new: bool = False
    fullscreen: bool = False
    output: Path | None = None
    copy: bool = False


IMAGE_FILTER = "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;WebP Image (*.webp)"
DEFAULT_IMAGE_FORMAT = "png"
TRANSPARENT = Qt.GlobalColor.transparent
