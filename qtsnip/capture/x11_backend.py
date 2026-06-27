from __future__ import annotations

from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication, QImage, QPainter

from .base import CaptureError, ScreenshotBackend
from ..models import CaptureMode
from ..widgets.selection_overlay import SelectionOverlay


class X11Backend(ScreenshotBackend):
    name = "Qt/X11"

    def _desktop_image(self) -> tuple[QImage, QRect]:
        screens = QGuiApplication.screens()
        if not screens:
            raise CaptureError("Qt could not find a screen.")
        geometry = QRect()
        for screen in screens:
            geometry = geometry.united(screen.geometry())
        image = QImage(geometry.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(0)
        painter = QPainter(image)
        for screen in screens:
            pixmap = screen.grabWindow(0)
            painter.drawPixmap(screen.geometry().topLeft() - geometry.topLeft(), pixmap)
        painter.end()
        return image, geometry

    def capture(self, mode: CaptureMode) -> QImage:
        image, geometry = self._desktop_image()
        if mode is CaptureMode.FULLSCREEN:
            return image
        if mode is CaptureMode.WINDOW:
            raise CaptureError("Window capture is not implemented for Qt/X11 yet; use Rectangular Snip.")
        # Freeform currently uses the same reliable rectangular selector.
        selected = SelectionOverlay.select(image, geometry)
        if selected is None:
            raise CaptureError("Capture cancelled.")
        return selected
