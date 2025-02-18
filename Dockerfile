# ✅ Python 3.11이 포함된 공식 이미지 사용
FROM python:3.11-slim

# ✅ 작업 디렉토리 설정
WORKDIR /app

# ✅ 필수 패키지 설치 (Chrome 및 Selenium 실행을 위한 라이브러리)
RUN apt-get update && apt-get install -y wget curl unzip \
    && wget -q -O /tmp/chrome.deb "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" \
    && dpkg -i /tmp/chrome.deb || apt-get -fy install \
    && wget -q -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chromedriver-linux64.zip" \
    && unzip -o /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# ✅ 프로젝트 코드 복사
COPY . /app

# ✅ Python 패키지 설치 (pip 사용)
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Flask 앱 실행
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
