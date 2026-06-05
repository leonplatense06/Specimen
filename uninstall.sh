#!/usr/bin/env bash
set -e

INSTALL_DIR="$HOME/.specimen/venv"
BIN_DIR="$HOME/.local/bin"
BIN_NAME="spec"

echo "=== Specimen Uninstaller ==="

if [ -L "$BIN_DIR/$BIN_NAME" ] || [ -f "$BIN_DIR/$BIN_NAME" ]; then
    echo "Removing symlink: $BIN_DIR/$BIN_NAME"
    rm -f "$BIN_DIR/$BIN_NAME"
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "Removing virtual environment and installed packages: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
fi

echo "=== Uninstall Completed ==="
