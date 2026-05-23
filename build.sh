#!/usr/bin/env bash
set -e

# Render's Ubuntu image already has tesseract-ocr pre-installed
# Just install Python dependencies
pip install -r requirements.txt
