from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QStyleFactory


def apply_app_style(app: QApplication) -> None:
    app.setStyle(QStyleFactory.create("Fusion"))

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f3f5f7"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1f2933"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f6f8fa"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#111827"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1f2933"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1f2933"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2563eb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QMainWindow, QDialog {
            background: #f7f7f7;
            color: #202020;
        }

        QWidget#snipLauncher {
            background: #f7f7f7;
        }

        QPushButton#primarySnipButton {
            background: #0067c0;
            border-color: #0067c0;
            color: #ffffff;
            font-weight: 600;
            min-height: 32px;
            min-width: 92px;
        }

        QPushButton#primarySnipButton:hover {
            background: #005a9e;
            border-color: #005a9e;
        }

        QToolBar {
            background: #f7f7f7;
            border: 0;
            border-bottom: 1px solid #e5e5e5;
            spacing: 4px;
            padding: 7px 10px;
        }

        QToolBar#editToolbar {
            background: #fbfbfb;
            padding-top: 5px;
            padding-bottom: 5px;
        }

        QToolBar::separator {
            background: #d8d8d8;
            width: 1px;
            margin: 6px 8px;
        }

        QToolButton {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            padding: 5px 8px;
            color: #1f2933;
        }

        QToolButton:hover {
            background: #eeeeee;
            border-color: #d1d1d1;
        }

        QToolButton:pressed, QToolButton:checked {
            background: #e5f1fb;
            border-color: #8cc8ff;
            color: #003e73;
        }

        QPushButton {
            background: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 7px;
            padding: 6px 10px;
            min-height: 28px;
        }

        QPushButton:hover {
            border-color: #b8b8b8;
            background: #f4f4f4;
        }

        QComboBox, QSpinBox, QLineEdit {
            background: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 7px;
            padding: 5px 8px;
            min-height: 28px;
        }

        QComboBox:hover, QSpinBox:hover, QLineEdit:hover {
            border-color: #b8b8b8;
        }

        QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
            border-color: #0067c0;
        }

        QScrollArea#editorScroll {
            border: 0;
            background: #ededed;
        }

        QScrollArea#editorScroll > QWidget > QWidget {
            background: #ededed;
        }

        QWidget#toolOptions {
            background: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 7px;
        }

        QPushButton#colorSwatch {
            border: 1px solid #9aa7b5;
            border-radius: 6px;
            min-width: 34px;
            max-width: 34px;
            min-height: 24px;
            padding: 0;
        }

        QStatusBar {
            background: #f7f7f7;
            border-top: 1px solid #e5e5e5;
            color: #606060;
        }

        QDialog QLabel {
            color: #344454;
        }
        """
    )
