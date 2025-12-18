#!/bin/bash

echo "===================================="
echo "  FINAL_VERSION Setup Script"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python installation
echo "[1/5] Checking Python installation..."
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}ERROR: Python not found! Please install Python 3.12+${NC}"
        exit 1
    fi
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version
echo ""

# Remove old venv if exists
echo "[2/5] Removing old virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
    echo -e "${GREEN}Old venv removed.${NC}"
else
    echo "No old venv found."
fi
echo ""

# Create new venv
echo "[3/5] Creating new virtual environment..."
$PYTHON_CMD -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to create venv!${NC}"
    exit 1
fi
echo -e "${GREEN}Virtual environment created successfully!${NC}"
echo ""

# Activate venv and upgrade pip
echo "[4/5] Activating venv and upgrading pip..."
source venv/Scripts/activate || source venv/bin/activate
python -m pip install --upgrade pip
echo ""

# Install dependencies
echo "[5/5] Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install dependencies!${NC}"
    exit 1
fi
echo ""

echo "===================================="
echo -e "  ${GREEN}Setup completed successfully!${NC}"
echo "===================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/Scripts/activate"
echo ""
echo "To run the application:"
echo "  uvicorn main:app --reload"
echo ""
