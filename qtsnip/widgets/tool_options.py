from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QWidget

from ..models import DrawingOptions, Tool


class ToolOptions(QWidget):
    options_changed = Signal()

    def __init__(self, options: DrawingOptions, parent=None) -> None:
        super().__init__(parent)
        self.options = options
        self.setObjectName("toolOptions")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(6)
        self.color_button = QPushButton()
        self.color_button.setObjectName("colorSwatch")
        self.color_button.setToolTip("Tool color")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 80)
        self.width_spin.setToolTip("Stroke width")
        self.width_spin.setFixedWidth(68)
        label = QLabel("Width")
        label.setToolTip("Stroke width")
        layout.addWidget(self.color_button)
        layout.addWidget(label)
        layout.addWidget(self.width_spin)
        self._tool = Tool.PEN
        self.color_button.clicked.connect(self.choose_color)
        self.width_spin.valueChanged.connect(self._width_changed)
        self.set_tool(Tool.PEN)

    def set_tool(self, tool: Tool) -> None:
        self._tool = tool
        highlighter = tool is Tool.HIGHLIGHTER
        self.width_spin.setValue(self.options.highlighter_width if highlighter else self.options.pen_width)
        self._update_color_button(self.options.highlighter_color if highlighter else self.options.pen_color)

    def _active_color(self) -> QColor:
        return self.options.highlighter_color if self._tool is Tool.HIGHLIGHTER else self.options.pen_color

    def _update_color_button(self, color: QColor) -> None:
        self.color_button.setStyleSheet(f"background: {color.name()};")

    def choose_color(self) -> None:
        color = QColorDialog.getColor(self._active_color(), self, "Choose tool color")
        if not color.isValid():
            return
        if self._tool is Tool.HIGHLIGHTER:
            self.options.highlighter_color = color
        else:
            self.options.pen_color = color
        self._update_color_button(color)
        self.options_changed.emit()

    def _width_changed(self, width: int) -> None:
        if self._tool is Tool.HIGHLIGHTER:
            self.options.highlighter_width = width
        else:
            self.options.pen_width = width
        self.options_changed.emit()
