#!/bin/sh
set -eu

VERSION="0.1.0"
REVISION="1"
PACKAGE="opensnip"
ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build/deb/${PACKAGE}_${VERSION}-${REVISION}_all"
DIST_DIR="$ROOT_DIR/dist"

rm -rf "$BUILD_DIR"
mkdir -p \
    "$BUILD_DIR/DEBIAN" \
    "$BUILD_DIR/opt/opensnip" \
    "$BUILD_DIR/usr/bin" \
    "$BUILD_DIR/usr/share/applications" \
    "$BUILD_DIR/usr/share/doc/opensnip"

cp "$ROOT_DIR/main.py" "$BUILD_DIR/opt/opensnip/"
cp "$ROOT_DIR/requirements.txt" "$BUILD_DIR/opt/opensnip/"
cp -R "$ROOT_DIR/qtsnip" "$BUILD_DIR/opt/opensnip/"
find "$BUILD_DIR/opt/opensnip" -type d -name "__pycache__" -prune -exec rm -rf {} +

cp "$ROOT_DIR/packaging/opensnip" "$BUILD_DIR/usr/bin/opensnip"
chmod 0755 "$BUILD_DIR/usr/bin/opensnip"
cp "$ROOT_DIR/packaging/opensnip.desktop" "$BUILD_DIR/usr/share/applications/opensnip.desktop"
cp "$ROOT_DIR/README.md" "$BUILD_DIR/usr/share/doc/opensnip/README.md"
cp "$ROOT_DIR/LICENSE" "$BUILD_DIR/usr/share/doc/opensnip/LICENSE"

cat > "$BUILD_DIR/DEBIAN/control" <<EOF
Package: opensnip
Version: ${VERSION}-${REVISION}
Section: graphics
Priority: optional
Architecture: all
Maintainer: OpenSnip Maintainers <maintainer@example.com>
Depends: python3 (>= 3.12), python3-venv, python3-pip, gnome-screenshot
Homepage: https://github.com/
Description: Selection screenshot and annotation tool
 OpenSnip is a PySide6 screenshot utility for Ubuntu. It captures a selected
 screen area and provides simple editable annotations, crop, save, and copy.
 The launcher creates a private per-user Python environment for PySide6 on
 first run.
EOF

cat > "$BUILD_DIR/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
exit 0
EOF
chmod 0755 "$BUILD_DIR/DEBIAN/postinst"

cat > "$BUILD_DIR/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
exit 0
EOF
chmod 0755 "$BUILD_DIR/DEBIAN/postrm"

mkdir -p "$DIST_DIR"
dpkg-deb --build --root-owner-group "$BUILD_DIR" "$DIST_DIR/${PACKAGE}_${VERSION}-${REVISION}_all.deb"
