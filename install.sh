#!/usr/bin/env bash
set -e

# Configuration
INSTALL_DIR="$HOME/.specimen/venv"
BIN_DIR="$HOME/.local/bin"
BIN_NAME="spec"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEV_MODE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dev|-d)
        DEV_MODE=true
        shift
        ;;
    esac
done

echo "=== Specimen Installer (Linux) ==="

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3.11+."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]; }; then
    echo "Error: Python 3.11+ is required. Found Python $PYTHON_VERSION."
    exit 1
fi

# 2. Check/create directories
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# 3. Create virtual environment
echo "Creating isolated virtual environment..."
python3 -m venv "$INSTALL_DIR"

# 4. Install Specimen in the virtual environment
echo "Installing dependencies..."
"$INSTALL_DIR/bin/pip" install --upgrade pip

if [ "$DEV_MODE" = true ]; then
    echo "Installing Specimen in DEVELOPMENT (editable) mode..."
    "$INSTALL_DIR/bin/pip" install -e "$REPO_DIR[dev]"
else
    echo "Installing Specimen in STANDARD mode..."
    "$INSTALL_DIR/bin/pip" install "$REPO_DIR"
fi

# 5. Create symlink in ~/.local/bin
echo "Creating symlink in $BIN_DIR/$BIN_NAME"
rm -f "$BIN_DIR/$BIN_NAME"
ln -s "$INSTALL_DIR/bin/$BIN_NAME" "$BIN_DIR/$BIN_NAME"

echo "=== Installation Completed Successfully ==="
echo ""
echo "You can now run 'spec' from anywhere!"
echo ""

# Check if BIN_DIR is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "WARNING: $BIN_DIR is not in your PATH."
    echo "To be able to run 'spec' from any terminal, add the following line to your shell configuration file:"
    echo ""
    echo "For Bash/Zsh (e.g. ~/.bashrc or ~/.zshrc):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "For Fish shell (e.g. ~/.config/fish/config.fish):"
    echo "  fish_add_path \$HOME/.local/bin"
    echo ""
fi
