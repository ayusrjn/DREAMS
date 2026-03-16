#!/bin/bash
echo "Installing root dependencies for CPU..."
pip install -r requirements-cpu.txt

echo "Installing dream-integration dependencies for CPU..."
pip install -r dream-integration/requirements-cpu.txt
