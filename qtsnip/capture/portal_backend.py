from __future__ import annotations

from PySide6.QtGui import QImage

from .base import CaptureError, ScreenshotBackend
from ..models import CaptureMode


class PortalBackend(ScreenshotBackend):
    """Future xdg-desktop-portal implementation point; intentionally not simulated."""

    name = "xdg-desktop-portal (not implemented)"

    def capture(self, mode: CaptureMode) -> QImage:
        raise CaptureError(
            "The xdg-desktop-portal screenshot backend is not implemented yet. "
            "Install gnome-screenshot for the GNOME Wayland MVP backend."
        )
