from review_analysis.preprocessing.base_processor import BaseDataProcessor
# from base_processor import BaseDataProcessor
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import timedelta
from transformers import BertTokenizer, BertModel
import torch

class DiningcodeProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = pd.read_csv(input_path, encoding='utf-8-sig')

        # BERT 모델과 토크나이저 로드
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')


    def preprocess(self):
        # 컬럼명 수정 (CSV 파일에 맞게)
        self.df.rename(columns={'review': 'review_text'}, inplace=True)

        # '점'이 포함된 별점에서 숫자 분리리
        self.df['rating'] = self.df['rating'].replace({'점': ''}, regex=True).astype(float)
        
        # 날짜 전처리: 다양한 날짜 형식을 일관되게 처리
        self.df['date'] = self.df['date'].apply(self._normalize_date_format)  

        # 계절 파생변수 생성: season 컬럼 추가
        self.df['season'] = self.df['date'].apply(self._add_season_column)  
       
        # 결측치 처리: 리뷰 내용 결측시 별점에 따라 문구로 대체
        self.df['review_text'] = self.df['review_text'].fillna(self.df['rating'].apply(self._generate_review_text))

        # 특수문자 제거: review_text 컬럼에서 특수문자 제거, 리뷰 길이 제한
        self.df['review_text'] = self.df['review_text'].apply(self._remove_limit_review_text)

    
    def feature_engineering(self):
        ######### BERT
        # 새로운 특성: 리뷰 길이
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
        output_file = f"{self.output_dir}/preprocessed_reviews_diningcode.csv"
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')

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
        # 정규 표현식 사용하여 다양한 날짜 형식 변환
        if isinstance(date, str):
            # '2024년 8월 16일' -> '2024-08'
            if '년' in date:
                date = re.sub(r'(\d{4})년 (\d{1,2})월 (\d{1,2})일', r'\1-\2', date)
                date_parts = date.split('-')
                if len(date_parts) > 1:
                    # 월과 일을 두 자릿수로 변환
                    date = f"{date_parts[0]}-{date_parts[1].zfill(2)}"
    
            # '8월 16일' -> '2024-08' (현재 연도 추가)
            elif '년' not in date:
                try:
                    date_parts = date.split('월')
                    if len(date_parts) > 1:
                        month = date_parts[0].zfill(2)  # '8' -> '08'
                        date = f"{pd.to_datetime('today').year}-{month}"
                    else:
                        # 날짜 형식이 잘못된 경우 예외 처리
                        date = pd.to_datetime('today').strftime('%Y-%m')
                except Exception as e:
                    print(f"날짜 형식 오류: {date} - {e}")
                    date = pd.to_datetime('today').strftime('%Y-%m')

            # '6일 전' -> '2024-08-10' (현재 날짜에서 6일 전으로 변환)
            if '일 전' in date:
                date = pd.to_datetime('today').strftime('%Y-%m')
            
        return date
    

    def _add_season_column(self, date):
        # 날짜 형식이 'YYYY-MM' 형식으로 되어 있다고 가정
        if isinstance(date, str):
            # 문자열을 datetime 객체로 변환
            date = pd.to_datetime(date)

            # 월을 기준으로 계절 분류
            month = date.month
            if month in [12, 1, 2]:  # 겨울
                return 'Winter'
            elif month in [3, 4, 5]:  # 봄
                return 'Spring'
            elif month in [6, 7, 8]:  # 여름
                return 'Summer'
            else:  # 가을
                return 'Fall'
        return None
    

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
        # 문장을 BERT 임베딩 벡터로 변환
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()  # 문장 벡터의 평균 사용
