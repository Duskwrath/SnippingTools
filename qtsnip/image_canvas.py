from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QImage, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QInputDialog, QWidget

from .models import DrawingOptions, Tool
from .tools import draw_arrow, pixelate


@dataclass
class Annotation:
    kind: Tool
    color: QColor
    width: int
    start: QPoint
    end: QPoint | None = None
    text: str = ""
    font_size: int = 12
    points: list[QPoint] = field(default_factory=list)
    alpha: int = 255

    def copy(self) -> Annotation:
        return Annotation(
            kind=self.kind,
            color=QColor(self.color),
            width=self.width,
            start=QPoint(self.start),
            end=QPoint(self.end) if self.end is not None else None,
            text=self.text,
            font_size=self.font_size,
            points=[QPoint(point) for point in self.points],
            alpha=self.alpha,
        )

    def translated(self, delta: QPoint) -> Annotation:
        item = self.copy()
        item.start += delta
        if item.end is not None:
            item.end += delta
        item.points = [point + delta for point in item.points]
        return item


class ImageCanvas(QWidget):
    image_changed = Signal()
    history_changed = Signal(bool, bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._image = QImage()
        self._tool = Tool.PEN
        self.options = DrawingOptions()
        self._annotations: list[Annotation] = []
        self._undo: list[tuple[QImage, list[Annotation]]] = []
        self._redo: list[tuple[QImage, list[Annotation]]] = []
        self._start: QPoint | None = None
        self._last: QPoint | None = None
        self._preview_end: QPoint | None = None
        self._pending_stroke: list[QPoint] = []
        self._selected_annotation: int | None = None
        self._drag_start: QPoint | None = None
        self._drag_original: Annotation | None = None
        self.setMinimumSize(640, 420)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_options(self, options: DrawingOptions) -> None:
        self.options = options

    def set_tool(self, tool: Tool) -> None:
        self._tool = tool
        self._start = self._last = self._preview_end = None
        self._pending_stroke = []
        self.setCursor(Qt.CursorShape.CrossCursor if tool is not Tool.TEXT else Qt.CursorShape.IBeamCursor)
        self.update()

    @property
    def current_tool(self) -> Tool:
        return self._tool

    def image(self) -> QImage:
        image = self._image.copy()
        if not image.isNull():
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            for annotation in self._annotations:
                self._draw_annotation(painter, annotation)
            painter.end()
        return image

    def set_image(self, image: QImage) -> None:
        self._image = image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
        self._annotations.clear()
        self._selected_annotation = None
        self._undo.clear()
        self._redo.clear()
        self._resize_to_image()
        self.image_changed.emit()
        self._emit_history()
        self.update()

    def _resize_to_image(self) -> None:
        if not self._image.isNull():
            self.setFixedSize(self._image.size())

    def _annotation_copies(self) -> list[Annotation]:
        return [annotation.copy() for annotation in self._annotations]

    def _push_snapshot(self) -> None:
        if not self._image.isNull():
            self._undo.append((self._image.copy(), self._annotation_copies()))
            if len(self._undo) > 30:
                self._undo.pop(0)
            self._redo.clear()

    def _emit_history(self) -> None:
        self.history_changed.emit(bool(self._undo), bool(self._redo))

    def undo(self) -> None:
        if self._undo:
            self._redo.append((self._image.copy(), self._annotation_copies()))
            self._image, self._annotations = self._undo.pop()
            self._selected_annotation = None
            self.image_changed.emit(); self._emit_history(); self.update()

    def redo(self) -> None:
        if self._redo:
            self._undo.append((self._image.copy(), self._annotation_copies()))
            self._image, self._annotations = self._redo.pop()
            self._selected_annotation = None
            self.image_changed.emit(); self._emit_history(); self.update()

    def delete_selected(self) -> None:
        if self._selected_annotation is None:
            return
        self._push_snapshot()
        del self._annotations[self._selected_annotation]
        self._selected_annotation = None
        self.image_changed.emit(); self._emit_history(); self.update()

    def _point(self, event) -> QPoint:
        point = event.position().toPoint()
        rect = self.rect()
        return QPoint(
            max(rect.left(), min(point.x(), rect.right())),
            max(rect.top(), min(point.y(), rect.bottom())),
        )

    def _text_rect(self, annotation: Annotation) -> QRect:
        metrics = QFontMetrics(QFont("Sans Serif", annotation.font_size))
        return QRect(
            annotation.start.x(),
            annotation.start.y() - metrics.ascent(),
            metrics.horizontalAdvance(annotation.text),
            metrics.height(),
        ).adjusted(-6, -5, 6, 5)

    def _annotation_rect(self, annotation: Annotation) -> QRect:
        if annotation.kind is Tool.TEXT:
            return self._text_rect(annotation)
        if annotation.kind in {Tool.PEN, Tool.HIGHLIGHTER} and annotation.points:
            left = min(point.x() for point in annotation.points)
            right = max(point.x() for point in annotation.points)
            top = min(point.y() for point in annotation.points)
            bottom = max(point.y() for point in annotation.points)
            margin = max(8, annotation.width)
            return QRect(QPoint(left, top), QPoint(right, bottom)).normalized().adjusted(-margin, -margin, margin, margin)
        end = annotation.end or annotation.start
        margin = max(8, annotation.width * 2)
        return QRect(annotation.start, end).normalized().adjusted(-margin, -margin, margin, margin)

    def _annotation_at(self, point: QPoint) -> int | None:
        for index in range(len(self._annotations) - 1, -1, -1):
            if self._annotation_rect(self._annotations[index]).contains(point):
                return index
        return None

    def _draw_annotation(self, painter: QPainter, annotation: Annotation) -> None:
        color = QColor(annotation.color)
        color.setAlpha(annotation.alpha)
        pen = QPen(color, annotation.width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        if annotation.kind is Tool.TEXT:
            painter.setFont(QFont("Sans Serif", annotation.font_size))
            painter.drawText(annotation.start, annotation.text)
        elif annotation.kind is Tool.RECTANGLE and annotation.end is not None:
            painter.drawRect(QRect(annotation.start, annotation.end).normalized())
        elif annotation.kind is Tool.CIRCLE and annotation.end is not None:
            painter.drawEllipse(QRect(annotation.start, annotation.end).normalized())
        elif annotation.kind is Tool.ARROW and annotation.end is not None:
            draw_arrow(painter, annotation.start, annotation.end, color, annotation.width)
        elif annotation.kind in {Tool.PEN, Tool.HIGHLIGHTER} and len(annotation.points) > 1:
            path = QPainterPath(annotation.points[0])
            for point in annotation.points[1:]:
                path.lineTo(point)
            painter.drawPath(path)

    def _draw_selection(self, painter: QPainter) -> None:
        if self._selected_annotation is None:
            return
        annotation = self._annotations[self._selected_annotation]
        rect = self._annotation_rect(annotation)
        color = QColor(annotation.color)
        color.setAlpha(220)
        painter.setPen(QPen(color, max(1, annotation.width), Qt.PenStyle.DashLine))
        painter.drawRect(rect)

    def _preview_color(self) -> QColor:
        if self._tool is Tool.HIGHLIGHTER:
            color = QColor(self.options.highlighter_color)
            color.setAlpha(180)
            return color
        return QColor(self.options.pen_color)

    def mousePressEvent(self, event) -> None:
        if self._image.isNull() or event.button() != Qt.MouseButton.LeftButton:
            return
        self.setFocus()
        point = self._point(event)
        selected = self._annotation_at(point)
        if selected is not None:
            self._push_snapshot()
            self._selected_annotation = selected
            self._drag_start = point
            self._drag_original = self._annotations[selected].copy()
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            self.update()
            return
        self._selected_annotation = None
        if self._tool is Tool.TEXT:
            text, ok = QInputDialog.getText(self, "Add text", "Text:")
            if ok and text:
                self._push_snapshot()
                self._annotations.append(Annotation(Tool.TEXT, QColor(self.options.pen_color), self.options.pen_width, point, text=text, font_size=max(12, self.options.pen_width * 5)))
                self._selected_annotation = len(self._annotations) - 1
                self.image_changed.emit(); self._emit_history(); self.update()
            return
        self._push_snapshot()
        self._start = self._last = point
        self._preview_end = point
        self._pending_stroke = [point] if self._tool in {Tool.PEN, Tool.HIGHLIGHTER} else []

    def mouseMoveEvent(self, event) -> None:
        point = self._point(event)
        if self._drag_start is not None and self._drag_original is not None and self._selected_annotation is not None:
            self._annotations[self._selected_annotation] = self._drag_original.translated(point - self._drag_start)
            self.update()
            return
        if self._start is None or self._image.isNull():
            self.setCursor(Qt.CursorShape.SizeAllCursor if self._annotation_at(point) is not None else (Qt.CursorShape.CrossCursor if self._tool is not Tool.TEXT else Qt.CursorShape.IBeamCursor))
            return
        if self._tool in {Tool.PEN, Tool.HIGHLIGHTER, Tool.ERASER}:
            if self._tool is Tool.ERASER:
                painter = QPainter(self._image)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                pen = QPen(Qt.GlobalColor.transparent, self.options.pen_width * 3)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen); painter.drawLine(self._last, point); painter.end()
            else:
                self._pending_stroke.append(point)
            self._last = point
        self._preview_end = point
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._drag_start is not None:
            self._drag_start = None
            self._drag_original = None
            self.setCursor(Qt.CursorShape.CrossCursor if self._tool is not Tool.TEXT else Qt.CursorShape.IBeamCursor)
            self.image_changed.emit(); self._emit_history(); self.update()
            return
        if self._start is None or self._image.isNull() or event.button() != Qt.MouseButton.LeftButton:
            return
        end = self._point(event)
        rect = QRect(self._start, end).normalized()
        if self._tool is Tool.RECTANGLE:
            self._annotations.append(Annotation(Tool.RECTANGLE, QColor(self.options.pen_color), self.options.pen_width, QPoint(self._start), QPoint(end)))
            self._selected_annotation = len(self._annotations) - 1
        elif self._tool is Tool.CIRCLE:
            self._annotations.append(Annotation(Tool.CIRCLE, QColor(self.options.pen_color), self.options.pen_width, QPoint(self._start), QPoint(end)))
            self._selected_annotation = len(self._annotations) - 1
        elif self._tool is Tool.ARROW:
            self._annotations.append(Annotation(Tool.ARROW, QColor(self.options.pen_color), self.options.pen_width, QPoint(self._start), QPoint(end)))
            self._selected_annotation = len(self._annotations) - 1
        elif self._tool in {Tool.PEN, Tool.HIGHLIGHTER} and len(self._pending_stroke) > 1:
            color = QColor(self.options.highlighter_color if self._tool is Tool.HIGHLIGHTER else self.options.pen_color)
            width = self.options.highlighter_width if self._tool is Tool.HIGHLIGHTER else self.options.pen_width
            alpha = 110 if self._tool is Tool.HIGHLIGHTER else 255
            self._annotations.append(Annotation(self._tool, color, width, QPoint(self._pending_stroke[0]), points=[QPoint(point) for point in self._pending_stroke], alpha=alpha))
            self._selected_annotation = len(self._annotations) - 1
        elif self._tool is Tool.CROP and rect.width() > 1 and rect.height() > 1:
            self._image = self.image().copy(rect)
            self._annotations.clear()
            self._selected_annotation = None
            self._resize_to_image()
        elif self._tool is Tool.REDACT:
            self._image = self.image()
            self._annotations.clear()
            self._selected_annotation = None
            pixelate(self._image, rect)
        self._start = self._last = self._preview_end = None
        self._pending_stroke = []
        self.image_changed.emit(); self._emit_history(); self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._start = self._last = self._preview_end = self._drag_start = None
            self._drag_original = None
            self._pending_stroke = []
            self.update()
        elif event.key() in {Qt.Key.Key_Delete, Qt.Key.Key_Backspace} and self._selected_annotation is not None:
            self.delete_selected()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._image.isNull():
            painter.fillRect(self.rect(), QColor("#f8fafc"))
            placeholder = self.rect().adjusted(18, 18, -18, -18)
            painter.setPen(QPen(QColor("#bcc8d4"), 1, Qt.PenStyle.DashLine))
            painter.drawRoundedRect(placeholder, 8, 8)
            painter.setPen(QColor("#667789"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Capture or open an image to start editing")
            return
        painter.drawImage(0, 0, self._image)
        for annotation in self._annotations:
            self._draw_annotation(painter, annotation)
        if len(self._pending_stroke) > 1:
            color = QColor(self.options.highlighter_color if self._tool is Tool.HIGHLIGHTER else self.options.pen_color)
            width = self.options.highlighter_width if self._tool is Tool.HIGHLIGHTER else self.options.pen_width
            alpha = 110 if self._tool is Tool.HIGHLIGHTER else 255
            self._draw_annotation(painter, Annotation(self._tool, color, width, QPoint(self._pending_stroke[0]), points=self._pending_stroke, alpha=alpha))
        self._draw_selection(painter)
        if self._start is not None and self._preview_end is not None and self._tool in {Tool.RECTANGLE, Tool.CIRCLE, Tool.ARROW, Tool.CROP, Tool.REDACT}:
            rect = QRect(self._start, self._preview_end).normalized()
            color = self._preview_color()
            painter.setPen(QPen(color, max(1, self.options.pen_width), Qt.PenStyle.DashLine))
            if self._tool is Tool.ARROW:
                draw_arrow(painter, self._start, self._preview_end, color, max(1, self.options.pen_width))
            elif self._tool is Tool.CIRCLE:
                painter.drawEllipse(rect)
            else:
                painter.drawRect(rect)
