#!/bin/bash

echo "🔧 Installing Chromium and ChromeDriver..."
apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    chromium \
    chromium-driver

echo "✅ Chromium & ChromeDriver Installed"

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
