from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from .image_canvas import ImageCanvas


class EditorWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.canvas = ImageCanvas()
        scroll = QScrollArea()
        scroll.setObjectName("editorScroll")
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(False)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
