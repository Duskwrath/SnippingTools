from __future__ import annotations

import math

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen


def draw_arrow(painter: QPainter, start: QPoint, end: QPoint, color: QColor, width: int) -> None:
    pen = QPen(color, width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(start, end)

    dx = end.x() - start.x()
    dy = end.y() - start.y()
    length = math.hypot(dx, dy)
    if length == 0:
        return

    angle = math.atan2(dy, dx)
    head_length = min(16 + width * 2, length * 0.45)
    spread = math.radians(28)
    left = QPointF(
        end.x() - head_length * math.cos(angle - spread),
        end.y() - head_length * math.sin(angle - spread),
    )
    right = QPointF(
        end.x() - head_length * math.cos(angle + spread),
        end.y() - head_length * math.sin(angle + spread),
    )

    path = QPainterPath(QPointF(end))
    path.lineTo(left)
    path.moveTo(end)
    path.lineTo(right)
    painter.drawPath(path)


def pixelate(image: QImage, rect) -> None:
    """Apply deterministic block pixelation without third-party image libraries."""
    rect = rect.intersected(image.rect())
    if rect.isEmpty():
        return
    block = max(6, min(18, min(rect.width(), rect.height()) // 10 or 6))
    painter = QPainter(image)
    for y in range(rect.top(), rect.bottom() + 1, block):
        for x in range(rect.left(), rect.right() + 1, block):
            sample = image.pixelColor(x, y)
            painter.fillRect(x, y, block, block, sample)
    painter.end()
