#!/bin/bash

echo "🔧 Downloading and Installing Chromium & ChromeDriver..."

# ✅ Chrome 및 ChromeDriver 다운로드 (직접 URL 사용)
wget -q -O /usr/bin/chromium "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
dpkg -i /usr/bin/chromium || apt-get -fy install

wget -q -O /usr/bin/chromedriver "https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chromedriver-linux64.zip"
unzip -o /usr/bin/chromedriver -d /usr/bin/
chmod +x /usr/bin/chromium /usr/bin/chromedriver

echo "✅ Chromium & ChromeDriver Installed"

echo "📍 Checking versions..."
/usr/bin/chromium --version || echo "Chromium installation failed"
/usr/bin/chromedriver --version || echo "ChromeDriver installation failed"

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
