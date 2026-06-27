from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QImage


def load_image(path: Path) -> QImage:
    image = QImage(str(path))
    if image.isNull():
        raise ValueError(f"Could not read image: {path}")
    return image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)


def normalized_output_path(path: Path, default_format: str) -> Path:
    return path if path.suffix else path.with_suffix(f".{default_format}")
