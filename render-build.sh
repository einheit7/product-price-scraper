#!/bin/bash

echo "🔧 Downloading and Installing Chromium & ChromeDriver..."

# ✅ Chrome 설치 (Render의 Home 디렉터리에 저장)
mkdir -p /home/render/.local/bin
wget -q -O /home/render/.local/bin/chrome "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
dpkg -i /home/render/.local/bin/chrome || apt-get -fy install

# ✅ ChromeDriver 설치 (Render의 Home 디렉터리에 저장)
wget -q -O /home/render/.local/bin/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chromedriver-linux64.zip"
unzip -o /home/render/.local/bin/chromedriver.zip -d /home/render/.local/bin/
chmod +x /home/render/.local/bin/chrome /home/render/.local/bin/chromedriver

echo "✅ Chromium & ChromeDriver Installed"

echo "📍 Checking versions..."
/home/render/.local/bin/chrome --version || echo "Chromium installation failed"
/home/render/.local/bin/chromedriver --version || echo "ChromeDriver installation failed"

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
