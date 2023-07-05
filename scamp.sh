#!/bin/bash

# Check if pip is installed
if ! command -v pip &>/dev/null; then
  echo "pip is not installed. Please install it using the following command:"
  echo "sudo apt install python3-pip"
  exit 1
fi

# Check if python3-venv is installed
if ! dpkg -s python3-venv &>/dev/null; then
  echo "python3-venv is not installed. Please install it using the following command:"
  echo "sudo apt install python3-venv"
  exit 1
fi

# Create the input and output directories if they don't exist
input_dir="input"
output_dir="output"

mkdir -p "$input_dir"
mkdir -p "$output_dir"

# Ensure the input directory is empty
if [ "$(ls -A $input_dir)" ]; then
  echo "Input directory is not empty. Please remove any files from the input directory."
  exit 1
fi

# Ensure the output directory is empty
if [ "$(ls -A $output_dir)" ]; then
  echo "Output directory is not empty. Please remove any files from the output directory."
  exit 1
fi

# Create a virtual environment if not already present
if [ ! -d "venv" ]; then
  # Create a virtual environment
  python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run emailMonitor.py
python emailMonitor.py