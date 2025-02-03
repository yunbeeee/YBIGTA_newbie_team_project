from fastapi import APIRouter, HTTPException
from database.mongodb_connection import mongo_db
from review_analysis.preprocessing.diningcode_processor import DiningcodeProcessor
from review_analysis.preprocessing.googlemaps_processor import GooglemapsProcessor
from review_analysis.preprocessing.kakaomap_processor import KakaomapProcessor

review = APIRouter()

PROCESSORS = {
    "diningcode": DiningcodeProcessor("diningcode"),
    "googlemaps": GooglemapsProcessor("googlemaps"),
    "kakaomap": KakaomapProcessor("kakaomap"),
}

@review.post("/review/preprocess/{site_name}")
def preprocess_reviews(site_name: str):
    # MongoDB 컬렉션 선택
    if site_name not in ["diningcode", "googlemaps", "kakaomap"]:
        return {"error": "지원되지 않는 사이트입니다."}

    processor = PROCESSORS[site_name]
    processor.preprocess()
    processor.feature_engineering()
    processor.save_to_database()

    return {"message": f"{site_name} 데이터 전처리 및 저장 완료!"}