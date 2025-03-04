#!/usr/bin/env bash

# Script to install dependencies for the shop-lifter project

# Ensure script is executed from project root
if [ ! -f "CLAUDE.md" ]; then
    echo "Error: This script must be run from the project root directory."
    echo "Please run: bash scripts/setup/install_dependencies.sh"
    exit 1
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment. Please ensure python3-venv is installed."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -U pip setuptools wheel
pip install -r requirements.txt

# Install development dependencies if in dev mode
if [ "$1" == "--dev" ]; then
    echo "Installing development dependencies..."
    pip install black isort flake8 mypy pytest pytest-cov
fi

# Install RealSense SDK if requested
if [ "$1" == "--realsense" ] || [ "$2" == "--realsense" ]; then
    echo "Installing RealSense SDK dependencies..."
    # This is a placeholder - actual install commands depend on the OS
    echo "Please visit: https://github.com/IntelRealSense/librealsense/blob/master/doc/installation.md"
    echo "for detailed installation instructions for your platform."
fi

# Install ODrive tools if requested
if [ "$1" == "--odrive" ] || [ "$2" == "--odrive" ]; then
    echo "Installing ODrive dependencies..."
    pip install odrive
    echo "For firmware tools visit: https://docs.odriverobotics.com/v/latest/getting-started.html"
fi

echo "Setup complete! Activate the virtual environment with:"
echo "source .venv/bin/activate"