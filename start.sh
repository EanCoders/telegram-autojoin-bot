#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting Telegram Auto-Join Bot..."
python main.py
