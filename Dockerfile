# Railway 배포용 설정
# 1. 파이썬 3.10 버전(안정적인 Debian Bookworm 기반)을 사용합니다.
FROM python:3.10-slim-bookworm

# 2. 작업 폴더를 설정합니다.
WORKDIR /app

# 3. 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. 필요한 라이브러리 설치 (requirements.txt 복사 및 설치)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 현재 폴더의 모든 파일을 서버로 복사합니다.
COPY . .

# 6. Streamlit이 사용할 포트를 열어줍니다.
EXPOSE 8501

# 7. 헬스체크 (서버가 잘 살아있는지 확인)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 8. 실행 명령어 (Railway가 $PORT를 주면 그걸 쓰고, 아니면 8501을 씁니다)
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
