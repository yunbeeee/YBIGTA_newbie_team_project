from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_url = os.getenv("MONGO_URL")

mongo_client = MongoClient(mongo_url)

# mongodbcompass에서 database 이름을 "review_db"으로 지정하고
# 해당 데이터베이스 안에 컬렉션으로 다이닝코드, 구글맵, 카카오맵 크롤링 데이터를 넣어줌.
# uvicorn app.main:app --reload 실행 후 터미널이나 cmd에서 아래 명령어 실행
# curl -X POST "http://127.0.0.1:8000/review/preprocess/{site_name}"

DB_NAME = "review_db"
mongo_db = mongo_client[DB_NAME]

