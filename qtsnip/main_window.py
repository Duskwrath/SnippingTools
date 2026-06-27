from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSize, QTimer, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QFileDialog, QFormLayout, QHBoxLayout, QLineEdit,
                               QMainWindow, QMessageBox, QPushButton, QSizePolicy,
                               QSpinBox, QStackedWidget, QToolBar, QVBoxLayout,
                               QWidget)

from .capture.base import CaptureError
from .capture.service import CaptureService
from .editor_window import EditorWindow
from .models import CaptureMode, IMAGE_FILTER, LaunchOptions, Tool
from .settings import AppSettings
from .shortcuts import install_shortcuts
from .utils.image_utils import load_image, normalized_output_path
from .widgets.tool_options import ToolOptions


class SettingsDialog(QDialog):
    """The settings kept outside the compact toolbar."""

    def __init__(self, settings: AppSettings, options, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.options = options
        self.setWindowTitle("OpenSnip Settings")
        self.resize(560, 280)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)
        self.directory = QLineEdit(str(settings.save_directory))
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse)
        directory_row = QHBoxLayout(); directory_row.setContentsMargins(0, 0, 0, 0); directory_row.setSpacing(8); directory_row.addWidget(self.directory); directory_row.addWidget(browse)
        directory_holder = QWidget(); directory_holder.setLayout(directory_row)
        form.addRow("Default save directory", directory_holder)
        self.format = QComboBox(); self.format.addItems(["png", "jpg", "webp"]); self.format.setCurrentText(settings.image_format)
        self.delay = QComboBox(); self.delay.addItems(["0", "3", "5", "10"]); self.delay.setCurrentText(str(settings.delay))
        self.pen_width = QSpinBox(); self.pen_width.setRange(1, 80); self.pen_width.setValue(options.pen_width)
        self.highlighter_width = QSpinBox(); self.highlighter_width.setRange(1, 80); self.highlighter_width.setValue(options.highlighter_width)
        self.auto_copy = QCheckBox(); self.auto_copy.setChecked(settings.auto_copy)
        self.auto_save = QCheckBox(); self.auto_save.setChecked(settings.auto_save)
        form.addRow("Default format", self.format); form.addRow("Default delay (seconds)", self.delay)
        form.addRow("Pen width", self.pen_width); form.addRow("Highlighter width", self.highlighter_width)
        form.addRow("Auto-copy captures", self.auto_copy); form.addRow("Auto-save captures", self.auto_save)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self); layout.setContentsMargins(18, 18, 18, 18); layout.setSpacing(14); layout.addLayout(form); layout.addWidget(buttons)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose default save directory", self.directory.text())
        if path: self.directory.setText(path)

    def apply(self) -> None:
        self.settings.save_directory = Path(self.directory.text()).expanduser()
        self.settings.image_format = self.format.currentText()
        self.settings.delay = int(self.delay.currentText())
        self.settings.auto_copy = self.auto_copy.isChecked(); self.settings.auto_save = self.auto_save.isChecked()
        self.options.pen_width = self.pen_width.value(); self.options.highlighter_width = self.highlighter_width.value()
        self.settings.save_drawing_options(self.options)


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings, launch: LaunchOptions) -> None:
        super().__init__()
        self.settings = settings
        self.launch = launch
        self.capture_service: CaptureService | None = None
        self.current_path: Path | None = None
        self.dirty = False
        self.setWindowTitle("OpenSnip")
        self.resize(560, 168)
        self.editor = EditorWindow()
        self.launcher = self._build_launcher()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.launcher)
        self.stack.addWidget(self.editor)
        self.setCentralWidget(self.stack)
        self.options = settings.drawing_options()
        self.editor.canvas.set_options(self.options)
        self._actions: dict[str, QAction] = {}
        self._capture_bar: QToolBar | None = None
        self._tools_bar: QToolBar | None = None
        self._build_toolbar()
        self._show_launcher()
        self._shortcuts = install_shortcuts(self)
        self.editor.canvas.image_changed.connect(self._on_image_changed)
        self.editor.canvas.history_changed.connect(self._update_history_actions)
        QTimer.singleShot(0, self._apply_launch_options)

    def _action(self, text: str, callback, checkable: bool = False) -> QAction:
        action = QAction(text, self)
        action.setCheckable(checkable); action.triggered.connect(callback)
        self._actions[text] = action
        return action

    def _build_launcher(self) -> QWidget:
        launcher = QWidget()
        launcher.setObjectName("snipLauncher")
        launcher.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        new_button = QPushButton("New")
        new_button.setObjectName("primarySnipButton")
        new_button.setIcon(self._command_icon("selection"))
        new_button.clicked.connect(self.selection_snip)

        open_button = QPushButton("Open")
        open_button.setIcon(self._command_icon("open"))
        open_button.clicked.connect(self.open_image)

        settings_button = QPushButton("Settings")
        settings_button.setToolTip("Settings")
        settings_button.setIcon(self._command_icon("settings"))
        settings_button.clicked.connect(self.show_settings)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.addWidget(new_button)
        title_row.addWidget(open_button)
        title_row.addWidget(settings_button)

        layout = QVBoxLayout(launcher)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(0)
        layout.addLayout(title_row)
        return launcher

    def _tool_icon(self, tool: Tool) -> QIcon:
        pixmap = QPixmap(28, 28)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ink = QColor("#263340")
        accent = QColor("#2563eb")
        painter.setPen(QPen(ink, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        if tool is Tool.PEN:
            painter.drawLine(7, 21, 20, 8)
            painter.drawLine(18, 6, 22, 10)
            painter.setPen(QPen(accent, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(6, 22)
        elif tool is Tool.HIGHLIGHTER:
            painter.setPen(QPen(QColor("#f5c542"), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(7, 20, 21, 20)
            painter.setPen(QPen(ink, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(9, 16, 19, 6)
            painter.drawLine(17, 5, 22, 10)
        elif tool is Tool.ERASER:
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
            painter.setPen(QPen(ink, 2))
            painter.drawLine(8, 8, 20, 8)
            painter.drawLine(14, 8, 14, 22)
        elif tool is Tool.CROP:
            painter.drawLine(9, 5, 9, 20)
            painter.drawLine(5, 16, 20, 16)
            painter.drawLine(19, 8, 19, 23)
            painter.drawLine(8, 21, 23, 21)
        elif tool is Tool.REDACT:
            painter.fillRect(7, 9, 15, 11, QColor("#263340"))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawLine(9, 12, 20, 12)
            painter.drawLine(9, 16, 20, 16)

        painter.end()
        return QIcon(pixmap)

    def _command_icon(self, name: str) -> QIcon:
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ink = QColor("#263340")
        accent = QColor("#2563eb")
        painter.setPen(QPen(ink, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        if name == "snip":
            painter.drawRoundedRect(5, 5, 14, 14, 2, 2)
            painter.setPen(QPen(accent, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(4, 12, 20, 12)
            painter.drawLine(12, 4, 12, 20)
        elif name == "selection":
            painter.setPen(QPen(ink, 1.8, Qt.PenStyle.DashLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawRoundedRect(5, 5, 12, 12, 2, 2)
            painter.setPen(QPen(accent, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
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
            painter.fillRect(9, 6, 5, 4, accent)
        elif name == "save_as":
            painter.drawRoundedRect(4, 4, 13, 16, 2, 2)
            painter.drawLine(7, 5, 14, 5)
            painter.setPen(QPen(accent, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(14, 16, 20, 10)
            painter.drawLine(18, 10, 20, 10)
            painter.drawLine(20, 10, 20, 12)
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

    def _build_toolbar(self) -> None:
        bar = QToolBar("Capture", self)
        bar.setObjectName("captureToolbar")
        self._capture_bar = bar
        bar.setMovable(False)
        bar.setIconSize(QSize(20, 20))
        bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(bar)

        new_action = self._action("New", self.selection_snip)
        new_action.setIcon(self._command_icon("selection"))
        open_action = self._action("Open", self.open_image)
        open_action.setIcon(self._command_icon("open"))
        save_action = self._action("Save", self.save)
        save_action.setIcon(self._command_icon("save"))
        save_as_action = self._action("Save As", self.save_as)
        save_as_action.setIcon(self._command_icon("save_as"))
        copy_action = self._action("Copy", self.copy_to_clipboard)
        copy_action.setIcon(self._command_icon("copy"))
        settings_action = self._action("Settings", self.show_settings)
        settings_action.setIcon(self._command_icon("settings"))

        bar.addAction(new_action)
        bar.addAction(open_action)
        bar.addAction(copy_action)
        bar.addAction(save_action)
        bar.addAction(settings_action)

        tools = QToolBar("Annotate", self)
        tools.setObjectName("editToolbar")
        self._tools_bar = tools
        tools.setMovable(False)
        tools.setIconSize(QSize(24, 24))
        tools.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBarBreak()
        self.addToolBar(tools)
        for label, tool in [("Eraser", Tool.ERASER), ("Rectangle", Tool.RECTANGLE), ("Circle", Tool.CIRCLE), ("Arrow", Tool.ARROW), ("Text", Tool.TEXT), ("Crop", Tool.CROP)]:
            action = self._action(label, lambda checked=False, selected=tool: self.select_tool(selected), True)
            action.setIcon(self._tool_icon(tool))
            action.setToolTip(label)
            tools.addAction(action)
        self._actions["Rectangle"].setChecked(True)
        self.editor.canvas.set_tool(Tool.RECTANGLE)
        undo_action = self._action("Undo", self.undo)
        undo_action.setIcon(self._command_icon("undo"))
        redo_action = self._action("Redo", self.redo)
        redo_action.setIcon(self._command_icon("redo"))
        delete_action = self._action("Delete", self.delete_selected)
        delete_action.setIcon(self._command_icon("delete"))
        tools.addAction(undo_action); tools.addAction(redo_action); tools.addAction(delete_action)
        undo_action.setEnabled(False); redo_action.setEnabled(False)
        self.tool_options = ToolOptions(self.options)
        self.tool_options.options_changed.connect(lambda: self.settings.save_drawing_options(self.options))
        tools.addWidget(self.tool_options)
        self.statusBar().showMessage("Ready")

    def _show_launcher(self) -> None:
        self.stack.setCurrentWidget(self.launcher)
        if self._capture_bar is not None:
            self._capture_bar.hide()
        if self._tools_bar is not None:
            self._tools_bar.hide()
        self.statusBar().hide()
        self.setWindowTitle("OpenSnip")
        self.setMinimumSize(390, 82)
        self.resize(430, 92)

    def _show_editor(self) -> None:
        self.stack.setCurrentWidget(self.editor)
        if self._capture_bar is not None:
            self._capture_bar.show()
        if self._tools_bar is not None:
            self._tools_bar.show()
        self.statusBar().show()
        self.setMinimumSize(760, 520)
        self.resize(max(self.width(), 1100), max(self.height(), 760))
        self._update_title()

    def select_tool(self, tool: Tool) -> None:
        for action in self._actions.values():
            if action.isCheckable(): action.setChecked(False)
        self._actions[next(k for k, v in {"Eraser": Tool.ERASER, "Rectangle": Tool.RECTANGLE, "Circle": Tool.CIRCLE, "Arrow": Tool.ARROW, "Text": Tool.TEXT, "Crop": Tool.CROP}.items() if v is tool)].setChecked(True)
        self.tool_options.set_tool(tool); self.editor.canvas.set_tool(tool)

    def _apply_launch_options(self) -> None:
        if self.launch.delay is not None:
            seconds = self.launch.delay
            self.settings.delay = seconds
        if self.launch.fullscreen:
            self._start_capture(CaptureMode.FULLSCREEN)
        elif self.launch.new:
            self.new_snip()

    def new_snip(self) -> None:
        self.selection_snip()

    def selection_snip(self) -> None:
        self._start_capture(CaptureMode.RECTANGLE)

    def fullscreen_snip(self) -> None:
        self._start_capture(CaptureMode.FULLSCREEN)

    def _start_capture(self, mode: CaptureMode) -> None:
        self.hide()
        QTimer.singleShot(150, lambda selected=mode: self._capture_now(selected))

    def _capture_now(self, mode: CaptureMode | None = None) -> None:
        try:
            self.capture_service = self.capture_service or CaptureService()
            image = self.capture_service.capture(mode or CaptureMode.RECTANGLE)
            self.editor.canvas.set_image(image); self.current_path = None; self.dirty = True
            self._show_editor()
            self.show()
            self.raise_()
            self.statusBar().showMessage(f"Captured using {self.capture_service.backend.name}")
            if self.settings.auto_copy or self.launch.copy: self.copy_to_clipboard()
            if self.settings.auto_save: self._auto_save()
            if self.launch.output: self._save_to(self.launch.output)
        except CaptureError as exc:
            self.show()
            self.raise_()
            if self.editor.canvas.image().isNull():
                self._show_launcher()
            else:
                self._show_editor()
            if str(exc) != "Capture cancelled.": self._error("Could not capture screen", str(exc))

    def open_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Open image", str(self.settings.save_directory), IMAGE_FILTER)
        if not filename: return
        try:
            self.editor.canvas.set_image(load_image(Path(filename))); self.current_path = Path(filename); self.dirty = False; self._show_editor(); self._update_title()
        except ValueError as exc: self._error("Could not open image", str(exc))

    def save(self) -> None:
        if self.current_path is None: self.save_as()
        else: self._save_to(self.current_path)

    def save_as(self) -> None:
        suggested = self.current_path or self.settings.save_directory / f"OpenSnip-{datetime.now():%Y%m%d-%H%M%S}.{self.settings.image_format}"
        filename, _ = QFileDialog.getSaveFileName(self, "Save image", str(suggested), IMAGE_FILTER)
        if filename: self._save_to(normalized_output_path(Path(filename), self.settings.image_format))

    def _save_to(self, path: Path) -> None:
        image = self.editor.canvas.image()
        if image.isNull(): return
        path.parent.mkdir(parents=True, exist_ok=True)
        if not image.save(str(path)):
            self._error("Could not save image", f"Qt could not write {path}"); return
        self.current_path = path; self.dirty = False; self.settings.save_directory = path.parent; self.settings.image_format = path.suffix.lstrip(".") or "png"; self._update_title(); self.statusBar().showMessage(f"Saved {path}")

    def _auto_save(self) -> None:
        destination = self.settings.save_directory / f"OpenSnip-{datetime.now():%Y%m%d-%H%M%S}.{self.settings.image_format}"
        self._save_to(destination)

    def copy_to_clipboard(self) -> None:
        image = self.editor.canvas.image()
        if not image.isNull():
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setImage(image); self.statusBar().showMessage("Image copied to clipboard")

    def undo(self) -> None: self.editor.canvas.undo()
    def redo(self) -> None: self.editor.canvas.redo()
    def delete_selected(self) -> None: self.editor.canvas.delete_selected()
    def cancel_current_operation(self) -> None: self.editor.canvas.set_tool(Tool.RECTANGLE); self.select_tool(Tool.RECTANGLE)

    def show_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self.options, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.apply()
            self.tool_options.set_tool(self.editor.canvas.current_tool)

    def _on_image_changed(self) -> None:
        self.dirty = True; self.settings.save_drawing_options(self.options); self._update_title()
    def _update_history_actions(self, can_undo: bool, can_redo: bool) -> None:
        self._actions["Undo"].setEnabled(can_undo); self._actions["Redo"].setEnabled(can_redo)
    def _update_title(self) -> None: self.setWindowTitle(f"{'*' if self.dirty else ''}OpenSnip" + (f" — {self.current_path.name}" if self.current_path else ""))
    def _error(self, title: str, message: str) -> None: QMessageBox.critical(self, title, message)
