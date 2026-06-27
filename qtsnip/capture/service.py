from __future__ import annotations

from PySide6.QtGui import QImage

from .base import CaptureError, ScreenshotBackend
from .gnome_backend import GnomeScreenshotBackend
from .portal_backend import PortalBackend
from .x11_backend import X11Backend
from ..models import CaptureMode
from ..utils.platform_utils import current_desktop, gnome_screenshot_available, session_type


class CaptureService:
    def __init__(self) -> None:
        self.backend = self._select_backend()

    @staticmethod
    def _select_backend() -> ScreenshotBackend:
        session = session_type()
        desktop = current_desktop()
        if session == "x11":
            return X11Backend()
        if session == "wayland" and "gnome" in desktop and gnome_screenshot_available():
            return GnomeScreenshotBackend()
        if session == "wayland":
            return PortalBackend()
        if gnome_screenshot_available():
            return GnomeScreenshotBackend()
        raise CaptureError(
            "No supported screenshot backend was found. On GNOME install gnome-screenshot; "
            "on X11 start the application inside an X11 session."
        )

    def capture(self, mode: CaptureMode) -> QImage:
        return self.backend.capture(mode)
