#!/bin/bash

# Exit script if any command fails
set -e

# Check if virtual environment exists; if not, create it
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
source env/bin/activate

# Install dependencies from requirements.txt if it exists
if [[ -f requirements.txt ]]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping dependency installation."
fi

echo "Setup completed successfully!"
