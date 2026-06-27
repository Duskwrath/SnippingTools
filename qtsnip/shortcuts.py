from __future__ import annotations

from PySide6.QtGui import QKeySequence, QShortcut


def install_shortcuts(window) -> list[QShortcut]:
    mapping = {
        QKeySequence.StandardKey.New: window.new_snip,
        QKeySequence("Ctrl+Shift+N"): window.selection_snip,
        QKeySequence.StandardKey.Save: window.save,
        QKeySequence("Ctrl+Shift+S"): window.save_as,
        QKeySequence.StandardKey.Copy: window.copy_to_clipboard,
        QKeySequence.StandardKey.Open: window.open_image,
        QKeySequence.StandardKey.Undo: window.undo,
        QKeySequence.StandardKey.Redo: window.redo,
        QKeySequence("Ctrl+Shift+Z"): window.redo,
        QKeySequence("Delete"): window.delete_selected,
        QKeySequence("Backspace"): window.delete_selected,
        QKeySequence("Esc"): window.cancel_current_operation,
    }
    return [QShortcut(key, window, activated=callback) for key, callback in mapping.items()]
