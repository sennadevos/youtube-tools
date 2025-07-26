#!/bin/bash

if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Running setup.sh..."
    ./setup.sh
fi

venv/bin/python run.py

