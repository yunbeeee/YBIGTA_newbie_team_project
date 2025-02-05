FROM python:3.9

# 컨테이너 내부 작업 디렉토리를 /app으로 설정 
WORKDIR /app

# requirements.txt 파일을 먼저 복사하고 의존성 설치
COPY requirements.txt .

# no cache 없어도 되기는 하는데 이거 하면 캐시 데이터를 남기지 않도록 할 수 있음 다만 빌드 할 때 조금 느려짐
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 애플리케이션 복사
COPY . .

# 컨테이너가 8000 포트를 열도록 설정 (외부 접근은 -p 옵션 필요)
EXPOSE 8000

# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
