from review_analysis.preprocessing.base_processor import BaseDataProcessor
# from base_processor import BaseDataProcessor
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import timedelta
from transformers import BertTokenizer, BertModel
import torch

class KakaomapProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = pd.read_csv(input_path)

        # BERT 모델과 토크나이저 로드
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')


    def preprocess(self):
        # 컬럼명 수정 (CSV 파일에 맞게)
        self.df.rename(columns={'content': 'review_text'}, inplace=True)
        
        # 날짜 전처리: '2024.04.17.' -> '2024-04'
        self.df['date'] = self.df['date'].apply(self._normalize_date_format)
        
        # 계절 파생변수 생성: season 컬럼 추가
        self.df['season'] = self.df['date'].apply(self._add_season_column)

        # 결측치 처리: 리뷰 내용 결측시 별점에 따라 문구로 대체
        self.df['review_text'] = self.df['review_text'].fillna(self.df['rating'].apply(self._generate_review_text))

        # 특수문자 제거: review_text 컬럼에서 특수문자 제거
        self.df['review_text'] = self.df['review_text'].apply(self._remove_limit_review_text)

    def feature_engineering(self):
        # 새로운 특성: 리뷰 길이
        self.df['review_length'] = self.df['review_text'].apply(len)

        # BERT 임베딩 벡터화
        self.df['review_vector_bert'] = self.df['review_text'].apply(self.get_bert_vector)

        # TF-IDF 벡터화
        tfidf = TfidfVectorizer(stop_words='english', max_features=500)
        tfidf_matrix = tfidf.fit_transform(self.df['review_text'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())

        # TF-IDF 특성 추가
        self.df = pd.concat([self.df, tfidf_df], axis=1)

    def save_to_database(self):
        output_file = f"{self.output_dir}/preprocessed_reviews_kakaomap.csv"
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')

    def _normalize_date_format(self, date):
        if isinstance(date, str):
            # '2024.04.17.' -> '2024-04'
            date_parts = date.split('.')
            if len(date_parts) > 1:
                return f"{date_parts[0]}-{date_parts[1].zfill(2)}"
        return date

    def _add_season_column(self, date):
        if isinstance(date, str):
            month = int(date.split('-')[1])

            # 월을 기준으로 계절 분류
            if month in [12, 1, 2]:  # 겨울
                return 'Winter'
            elif month in [3, 4, 5]:  # 봄
                return 'Spring'
            elif month in [6, 7, 8]:  # 여름
                return 'Summer'
            else:  # 가을
                return 'Fall'
        return None

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
        
    def _remove_limit_review_text(self, text, max_length=300):
        # 정규 표현식으로 특수문자 제거 (영어 알파벳, 숫자, 한글, 공백만 남김)
        cleaned_text = re.sub(r'[^A-Za-z0-9가-힣\s]', '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # 연속된 공백을 하나로 줄임
        cleaned_text = cleaned_text.strip()  # 앞뒤 공백 제거

        # 텍스트 길이 제한 (단어 기준)
        words = cleaned_text.split()
        if len(words) > max_length:
            return ' '.join(words[:max_length])  # 최대 길이만큼 자르기
        else:
            return cleaned_text

    def get_bert_vector(self, text):
        # 문장을 BERT 임베딩 벡터로 변환환
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()  # 문장 벡터의 평균 사용