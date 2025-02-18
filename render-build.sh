#!/bin/bash

echo "🔧 Installing Chromium and ChromeDriver..."
apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    chromium \
    chromium-driver

echo "✅ Chromium & ChromeDriver Installed"
echo "📍 Checking versions..."
chromium --version
chromedriver --version

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
