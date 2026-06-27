from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PySide6.QtGui import QImage

from .base import CaptureError, ScreenshotBackend
from ..models import CaptureMode
from ..utils.image_utils import load_image
from ..utils.platform_utils import gnome_screenshot_available


class GnomeScreenshotBackend(ScreenshotBackend):
    """Desktop-approved command backend used by the Wayland MVP."""

    name = "gnome-screenshot"

    def capture(self, mode: CaptureMode) -> QImage:
        if not gnome_screenshot_available():
            raise CaptureError("gnome-screenshot is not installed. Run: sudo apt install gnome-screenshot")
        if mode is CaptureMode.FREEFORM:
            mode = CaptureMode.RECTANGLE
        with tempfile.NamedTemporaryFile(prefix="opensnip-", suffix=".png", delete=False) as handle:
            destination = Path(handle.name)
        args = ["gnome-screenshot"]
        if mode is CaptureMode.RECTANGLE:
            args.append("-a")
        elif mode is CaptureMode.WINDOW:
            args.append("-w")
        args.extend(["-f", str(destination)])
        try:
            completed = subprocess.run(args, capture_output=True, text=True, timeout=90, check=False)
            if completed.returncode != 0:
                detail = completed.stderr.strip() or "The capture was cancelled or rejected by the desktop."
                raise CaptureError(f"gnome-screenshot failed: {detail}")
            return load_image(destination)
        finally:
            destination.unlink(missing_ok=True)
