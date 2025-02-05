from review_analysis.preprocessing.base_processor import BaseDataProcessor
# from base_processor import BaseDataProcessor
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import timedelta
from transformers import BertTokenizer, BertModel
import torch

from database.mongodb_connection import mongo_db

class GooglemapsProcessor(BaseDataProcessor):
    def __init__(self, site_name: str):
        self.site_name = site_name
        self.collection = mongo_db[site_name]
        self.df = self.load_data()

        # BERT 모델과 토크나이저 로드
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')

    def load_data(self):
        """MongoDB에서 데이터를 불러와 DataFrame으로 변환"""
        data = list(self.collection.find({}, {'_id': 0}))  
        # MongoDB에서 _id 제외하고 모든 데이터 조회
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def preprocess(self):
        # 컬럼명 수정 (CSV 파일에 맞게)
        self.df.rename(columns={'content': 'review_text'}, inplace=True)

        # 날짜 전처리: 다양한 날짜 형식을 일관되게 처리
        self.df['date'] = self.df['date'].apply(self._normalize_date_format)  
       
        # 결측치 처리: 리뷰 내용 결측시 별점에 따라 문구로 대체
        self.df['review_text'] = self.df['review_text'].fillna(self.df['rating'].apply(self._generate_review_text))

        # 특수문자 제거: review_text 컬럼에서 특수문자 제거, 리뷰 길이 제한
        self.df['review_text'] = self.df['review_text'].apply(self._remove_limit_review_text)

    def feature_engineering(self):
        # 리뷰 길이 특성 생성
        self.df['review_length'] = self.df['review_text'].apply(len)

        # 리뷰 벡터화 (BERT 임베딩)
        self.df['review_vector_bert'] = self.df['review_text'].apply(self.get_bert_vector)

        # TF-IDF 벡터화
        tfidf = TfidfVectorizer(stop_words='english', max_features=500)
        tfidf_matrix = tfidf.fit_transform(self.df['review_text'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
        
        # TF-IDF 특성 추가
        self.df = pd.concat([self.df, tfidf_df], axis=1)

    def save_to_database(self):
        """
        output_file = f"{self.output_dir}/preprocessed_reviews_googlemaps.csv"
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        """
        if not self.df.empty:
            collection_name = f"preprocessed_{self.site_name}"
            collection = mongo_db[collection_name]

            # NumPy 배열을 리스트로 변환
            if 'review_vector_bert' in self.df.columns:
                self.df['review_vector_bert'] = self.df['review_vector_bert'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

            # 데이터 존재 여부 확인 후 추가
            for record in self.df.to_dict(orient="records"):
                if not collection.find_one({"review_text": record["review_text"]}):  # 중복 방지
                    collection.insert_one(record)


    def _generate_review_text(self, rating):
        # 별점에 따른 리뷰 문구 생성
        if rating == 5:
            return "정말 좋았어요"
        elif rating == 4:
            return "좋았어요"
        elif rating == 3:
            return "보통이었어요"
        elif rating == 2:
            return "불만족했어요"
        else:
            return "매우 불만족"
        
    def _normalize_date_format(self, date):
        # "3달 전", "2년 전", "3주 전" 형식의 날짜를 현재 날짜 기준으로 변환
        if isinstance(date, str):
            current_year = pd.to_datetime('today').year
            current_month = pd.to_datetime('today').month

            if '년' in date:
                # '2년 전' -> '2022'
                year_diff = int(re.search(r'(\d+)년 전', date).group(1))
                return str(current_year - year_diff)
            
            elif '달' in date:
                # '3달 전' -> '2024' (현재 시점 기준 변환)
                month_diff = int(re.search(r'(\d+)달 전', date).group(1))
                result_date = pd.to_datetime(f"{current_year}-{current_month}") - timedelta(days=30 * month_diff)
                return result_date.strftime('%Y')
            
            elif '주' in date:
                # '3주 전' -> '2024'
                week_diff = int(re.search(r'(\d+)주 전', date).group(1))
                result_date = pd.to_datetime('today') - timedelta(weeks=week_diff)
                return result_date.strftime('%Y')
            
            elif '일' in date:
                # '3일 전' -> '2025'
                day_diff = int(re.search(r'(\d+)일 전', date).group(1))
                result_date = pd.to_datetime('today') - timedelta(days=day_diff)
                return result_date.strftime('%Y')
            
        return date
    
    def _remove_limit_review_text(self, text, max_length=300):
        # 정규 표현식으로 특수문자 제거 (영어 알파벳, 숫자, 한글, 공백만 남김)
        cleaned_text = re.sub(r'[^A-Za-z0-9가-힣\s]', '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  
        cleaned_text = cleaned_text.strip()  # 앞뒤 공백 제거

        # 텍스트 길이 제한 (단어 기준)
        words = cleaned_text.split()
        if len(words) > max_length:
            return ' '.join(words[:max_length])
        else:
            return cleaned_text

    def get_bert_vector(self, text):
        # 문장을 BERT 임베딩 벡터로 변환
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()  # 문장 벡터의 평균 사용
