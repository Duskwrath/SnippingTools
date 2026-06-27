from __future__ import annotations

import os
import shutil


def session_type() -> str:
    return os.environ.get("XDG_SESSION_TYPE", "").lower()


def current_desktop() -> str:
    return os.environ.get("XDG_CURRENT_DESKTOP", "").lower()


def gnome_screenshot_available() -> bool:
    return shutil.which("gnome-screenshot") is not None
