#!/bin/bash

# Chrome 및 ChromeDriver 설치
echo "🔧 Installing Chromium and ChromeDriver..."
apt-get update && apt-get install -y chromium chromium-driver

# 필요한 Python 패키지 설치
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
