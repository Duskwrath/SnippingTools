from __future__ import annotations

from PySide6.QtCore import QEventLoop, QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget


class SelectionOverlay(QWidget):
    finished = Signal()

    def __init__(self, screenshot: QImage, desktop_geometry: QRect) -> None:
        super().__init__(None)
        self._screenshot = screenshot
        self._desktop_geometry = desktop_geometry
        self._start: QPoint | None = None
        self._selection = QRect()
        self._accepted = False
        self.setGeometry(desktop_geometry)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

    @classmethod
    def select(cls, screenshot: QImage, desktop_geometry: QRect) -> QImage | None:
        overlay = cls(screenshot, desktop_geometry)
        loop = QEventLoop()
        overlay.finished.connect(loop.quit)
        overlay.show()
        overlay.raise_()
        loop.exec()
        if not overlay._accepted or overlay._selection.isEmpty():
            return None
        return screenshot.copy(overlay._selection)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 70))
        if not self._selection.isEmpty():
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self._selection, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.drawRect(self._selection)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._selection = QRect(self._start, self._start)

    def mouseMoveEvent(self, event) -> None:
        if self._start is not None:
            self._selection = QRect(self._start, event.position().toPoint()).normalized()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._start is not None:
            self._selection = QRect(self._start, event.position().toPoint()).normalized()
            self._accepted = not self._selection.isEmpty()
            self.close()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        self.finished.emit()
        super().closeEvent(event)
