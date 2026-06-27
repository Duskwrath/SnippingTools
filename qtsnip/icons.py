from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap

from .models import Tool


class OpenSnipIcons:
    """Small icon factory for OpenSnip toolbar actions."""

    ink = QColor("#263340")
    accent = QColor("#2563eb")

    @classmethod
    def tool(cls, tool: Tool) -> QIcon:
        pixmap = QPixmap(28, 28)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(cls.ink, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        if tool is Tool.ERASER:
            painter.drawLine(9, 18, 18, 9)
            painter.drawLine(12, 21, 21, 12)
            painter.drawLine(9, 18, 12, 21)
            painter.drawLine(18, 9, 21, 12)
        elif tool is Tool.RECTANGLE:
            painter.drawRect(7, 8, 15, 13)
        elif tool is Tool.CIRCLE:
            painter.drawEllipse(7, 7, 15, 15)
        elif tool is Tool.ARROW:
            painter.drawLine(7, 20, 21, 8)
            painter.drawLine(21, 8, 20, 15)
            painter.drawLine(21, 8, 14, 9)
        elif tool is Tool.TEXT:
            painter.drawLine(8, 8, 20, 8)
            painter.drawLine(14, 8, 14, 22)
        elif tool is Tool.CROP:
            painter.drawLine(9, 5, 9, 20)
            painter.drawLine(5, 16, 20, 16)
            painter.drawLine(19, 8, 19, 23)
            painter.drawLine(8, 21, 23, 21)

        painter.end()
        return QIcon(pixmap)

    @classmethod
    def command(cls, name: str) -> QIcon:
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(cls.ink, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        if name == "selection":
            painter.setPen(QPen(cls.ink, 1.8, Qt.PenStyle.DashLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawRoundedRect(5, 5, 12, 12, 2, 2)
            painter.setPen(QPen(cls.accent, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(15, 15, 21, 21)
            painter.drawLine(21, 21, 18, 21)
            painter.drawLine(21, 21, 21, 18)
        elif name == "open":
            painter.drawRoundedRect(4, 8, 16, 10, 2, 2)
            painter.drawLine(6, 8, 9, 5)
            painter.drawLine(9, 5, 13, 5)
        elif name == "save":
            painter.drawRoundedRect(5, 4, 14, 16, 2, 2)
            painter.drawLine(8, 5, 16, 5)
            painter.drawRect(8, 13, 8, 5)
            painter.fillRect(9, 6, 5, 4, cls.accent)
        elif name == "copy":
            painter.drawRoundedRect(7, 5, 11, 14, 2, 2)
            painter.drawRoundedRect(4, 8, 11, 12, 2, 2)
        elif name == "undo":
            painter.drawLine(8, 8, 4, 12)
            painter.drawLine(4, 12, 8, 16)
            painter.drawLine(5, 12, 18, 12)
        elif name == "redo":
            painter.drawLine(16, 8, 20, 12)
            painter.drawLine(20, 12, 16, 16)
            painter.drawLine(6, 12, 19, 12)
        elif name == "delete":
            painter.drawLine(8, 8, 16, 16)
            painter.drawLine(16, 8, 8, 16)
            painter.drawLine(7, 5, 17, 5)
            painter.drawLine(10, 4, 14, 4)
        elif name == "settings":
            painter.drawEllipse(8, 8, 8, 8)
            painter.drawEllipse(11, 11, 2, 2)
            painter.drawLine(12, 3, 12, 6)
            painter.drawLine(12, 18, 12, 21)
            painter.drawLine(3, 12, 6, 12)
            painter.drawLine(18, 12, 21, 12)
            painter.drawLine(6, 6, 8, 8)
            painter.drawLine(16, 16, 18, 18)
            painter.drawLine(18, 6, 16, 8)
            painter.drawLine(8, 16, 6, 18)

        painter.end()
        return QIcon(pixmap)
