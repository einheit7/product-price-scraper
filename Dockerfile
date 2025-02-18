# ✅ Python과 Chrome이 포함된 Docker 이미지 사용
FROM mcr.microsoft.com/playwright/python:v1.39.0-focal

# ✅ 작업 디렉토리 설정
WORKDIR /app

# ✅ 프로젝트 코드 복사
COPY . /app

# ✅ Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Flask 앱 실행
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
