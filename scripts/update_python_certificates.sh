#!/bin/bash

# Script to update Python certificates on a machine
# This script updates pip and the certifi package, which provides SSL certificates for Python

# Determine the correct pip command
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "pip not found. Please install Python and pip first."
    exit 1
fi

echo "Using $PIP_CMD to update pip..."
$PIP_CMD install --upgrade pip

echo "Updating certifi package..."
$PIP_CMD install --upgrade certifi

echo "Python certificates update completed."
echo "Note: If you're using a virtual environment, activate it before running this script."
echo "If you encounter permission errors, you may need to run with sudo (not recommended for system Python)."