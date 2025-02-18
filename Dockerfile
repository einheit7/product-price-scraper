# ✅ Chrome 및 ChromeDriver가 포함된 공식 이미지 사용
FROM selenium/standalone-chrome:124.0

# ✅ 작업 디렉토리 설정
WORKDIR /app

# ✅ 시스템 패키지 업데이트 및 Python 설치
RUN apt-get update && apt-get install -y python3 python3-pip

# ✅ 프로젝트 코드 및 의존성 복사
COPY . /app
RUN pip3 install --no-cache-dir -r requirements.txt

# ✅ Flask 앱 실행
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
