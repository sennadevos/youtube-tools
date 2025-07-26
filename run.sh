#!/bin/bash

if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Running setup.sh..."
    ./setup.sh
fi

# Check if arguments are provided
if [ $# -gt 0 ]; then
    # CLI mode - pass all arguments to the CLI script
    venv/bin/python youtube-tools-cli "$@"
else
    # GUI mode - no arguments
    venv/bin/python run.py
fi

