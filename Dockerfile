# ✅ Chrome이 포함된 안정적인 Docker 이미지 사용
FROM selenium/standalone-chrome:124.0

# ✅ 작업 디렉토리 설정
WORKDIR /app

# ✅ 프로젝트 코드 복사 및 권한 수정
COPY . /app
RUN chmod -R 777 /app

# ✅ Python 패키지 설치 (기본 포함된 Python 사용)
RUN pip3 install --no-cache-dir -r requirements.txt

# ✅ Flask 앱 실행
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
