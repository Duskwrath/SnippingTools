# OpenSnip

OpenSnip is a PySide6/Qt 6 screenshot and image-annotation tool for Ubuntu. It provides selection snips, image opening/saving, clipboard copy, editable annotations, crop, undo/redo, command-line capture options, and persisted user defaults.

## Ubuntu 24.04 install from DEB

Build the Debian package:

```bash
sh packaging/build_deb.sh
```

Install the generated package:

```bash
sudo apt install ./dist/opensnip_0.1.0-1_all.deb
```

Run OpenSnip:

```bash
opensnip
```

The package installs the app to `/opt/opensnip`, adds `/usr/bin/opensnip`, and creates a desktop launcher. On first run, `opensnip` creates a private Python environment in `~/.local/share/opensnip/venv` and installs PySide6 there. This keeps system Python untouched, but the first run needs internet access for `pip`.

To publish a downloadable build, attach `dist/opensnip_0.1.0-1_all.deb` to a GitHub release or provide it from your download page. Users can install it with:

```bash
sudo apt install ./opensnip_0.1.0-1_all.deb
```

## Ubuntu 24.04 manual setup

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv gnome-screenshot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Python 3.12+ is the target. PySide6 supplies Qt 6 through pip.

To run after manual setup:

```bash
source .venv/bin/activate
python main.py
```
## Use

Use **New** to start a selection snip, then annotate in the canvas. Save defaults to PNG; Save As supports PNG, JPEG, and WebP when the installed Qt image plugins support it. Visible tools include eraser, rectangle, arrow, text, crop, delete, undo, and redo.

CLI examples:

```bash
python main.py --new
python main.py --fullscreen --delay 5 --copy
python main.py --fullscreen --output ~/Pictures/capture.png
opensnip --new
```

## GNOME keyboard shortcut

OpenSnip deliberately does not install unreliable Wayland global hotkeys. In GNOME Settings -> Keyboard -> View and Customize Shortcuts -> Custom Shortcuts, create a shortcut whose command is:

```bash
opensnip --new
```

## Capture backends and Linux limitations

On an **X11** session OpenSnip uses Qt `QScreen.grabWindow(0)`, including a transparent in-app rectangular selection overlay. Multi-monitor screenshots are assembled into a virtual desktop image.

On **GNOME Wayland**, direct screen reads are restricted by design. OpenSnip uses the desktop-approved `gnome-screenshot` command (`-a` for area, `-f` for fullscreen, `-w` for the currently selected window). Its selection UI is owned by GNOME. Freeform capture falls back to rectangular selection in this MVP.

`xdg-desktop-portal` has an isolated backend placeholder, but is intentionally not represented as working. Other Wayland desktops without `gnome-screenshot` report a clear dependency/implementation error rather than claiming a capture succeeded.

Required system package for the GNOME Wayland MVP: `gnome-screenshot`.
