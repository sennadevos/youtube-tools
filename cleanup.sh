#!/bin/bash
echo "🧹 Cleaning up..."

# Remove virtual environment
if [ -d "venv" ]; then
    echo "Removing venv directory..."
    rm -rf venv
fi

# Remove Python cache files and __pycache__ folders
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Add any other cleanup you want here

echo "Cleanup done!"

