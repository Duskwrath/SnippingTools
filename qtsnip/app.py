from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .models import LaunchOptions
from .settings import AppSettings
from .style import apply_app_style


def parse_args(argv: list[str]) -> LaunchOptions:
    parser = argparse.ArgumentParser(description="OpenSnip Linux screenshot tool")
    parser.add_argument("--new", action="store_true", help="Start a new snip immediately")
    parser.add_argument("--fullscreen", action="store_true", help="Capture fullscreen immediately")
    parser.add_argument("--output", type=Path, help="Save the captured image directly to this path")
    parser.add_argument("--copy", action="store_true", help="Copy the capture to the clipboard")
    args = parser.parse_args(argv)
    return LaunchOptions(args.new, args.fullscreen, args.output, args.copy)


def main(argv: list[str] | None = None) -> int:
    launch = parse_args(argv if argv is not None else sys.argv[1:])
    app = QApplication(sys.argv)
    app.setApplicationName("OpenSnip"); app.setOrganizationName("OpenSnip")
    apply_app_style(app)
    window = MainWindow(AppSettings(), launch)
    window.show()
    return app.exec()
