from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from PySide6.QtGui import QImage

from .base import CaptureError, ScreenshotBackend
from ..models import CaptureMode
from ..utils.image_utils import load_image
from ..utils.platform_utils import gdbus_available


class GnomeShellBackend(ScreenshotBackend):
    """GNOME Shell D-Bus screenshot backend for modern GNOME Wayland sessions."""

    name = "GNOME Shell D-Bus"

    def capture(self, mode: CaptureMode) -> QImage:
        if not gdbus_available():
            raise CaptureError("gdbus is not installed. Run: sudo apt install libglib2.0-bin")
        if mode is CaptureMode.FREEFORM:
            mode = CaptureMode.RECTANGLE
        with tempfile.NamedTemporaryFile(prefix="opensnip-", suffix=".png", delete=False) as handle:
            destination = Path(handle.name)
        try:
            if mode is CaptureMode.RECTANGLE:
                x, y, width, height = self._select_area()
                self._call_shell("ScreenshotArea", str(x), str(y), str(width), str(height), "false", str(destination))
            elif mode is CaptureMode.WINDOW:
                self._call_shell("ScreenshotWindow", "true", "false", "false", str(destination))
            else:
                self._call_shell("Screenshot", "false", "false", str(destination))
            if not destination.exists() or destination.stat().st_size == 0:
                raise CaptureError("GNOME Shell did not create a screenshot.")
            return load_image(destination)
        finally:
            destination.unlink(missing_ok=True)

    def _select_area(self) -> tuple[int, int, int, int]:
        output = self._call_shell("SelectArea")
        values = [int(value) for value in re.findall(r"int32 (-?\d+)", output)]
        if len(values) != 4:
            raise CaptureError("GNOME Shell did not return a selected area.")
        x, y, width, height = values
        if width <= 0 or height <= 0:
            raise CaptureError("Capture cancelled.")
        return x, y, width, height

    @staticmethod
    def _call_shell(method: str, *args: str) -> str:
        completed = subprocess.run(
            [
                "gdbus",
                "call",
                "--session",
                "--dest",
                "org.gnome.Shell",
                "--object-path",
                "/org/gnome/Shell/Screenshot",
                "--method",
                f"org.gnome.Shell.Screenshot.{method}",
                *args,
            ],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "The capture was cancelled or rejected."
            raise CaptureError(f"GNOME Shell screenshot failed: {detail}")
        return completed.stdout.strip()
