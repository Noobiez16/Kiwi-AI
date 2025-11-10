#!/bin/bash
# Helper script to run Kiwi AI Trading System

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run with Streamlit
streamlit run run_kiwi.py

