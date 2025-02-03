#!/bin/bash

OS_NAME=$(uname -s)
USB_PATH=""

# Detect USB path based on OS
case "$OS_NAME" in
    Linux*)
        USB_PATH=$(findmnt -n -o TARGET -S $(mount | awk '/\/media\// {print $1}' | head -1)) ;;
    Darwin*)
        USB_PATH=$(system_profiler SPUSBDataType | grep "Mount Point" | awk -F ": " '{print $2}' | head -1) ;;
    *)
        echo "Unsupported OS: $OS_NAME"
        exit 1 ;;
esac

[ -z "$USB_PATH" ] && { echo "USB drive not detected"; exit 1; }

# Create optimized Python environment
PYTHON_DIR="$USB_PATH/network_security_usb/portable_env/python"
mkdir -p "$PYTHON_DIR"

# Platform-specific Python binaries
case "$OS_NAME" in
    Linux*)
        PYTHON_URL="https://www.python.org/ftp/python/3.9.7/python-3.9.7-embed-amd64.zip" ;;
    Darwin*)
        PYTHON_URL="https://www.python.org/ftp/python/3.9.7/python-3.9.7-macos11.pkg" ;;
esac

# Download and extract Python
curl -L "$PYTHON_URL" -o "$PYTHON_DIR/python_pkg"
if [ $? -ne 0 ]; then
    echo "Python download failed"
    exit 1
fi

# Setup lightweight virtual environment
"$PYTHON_DIR/bin/python3" -m venv --copies --without-pip "$PYTHON_DIR/venv"
source "$PYTHON_DIR/venv/bin/activate"

# Install optimized dependencies
pip install --no-cache-dir -r "$USB_PATH/network_security_usb/requirements.txt"
