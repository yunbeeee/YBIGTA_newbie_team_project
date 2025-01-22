# YBIGTA_newbie_team_project

## 팀 소개
 - 저희 팀은 5조입니다.

## 팀원 소개
 - 조태연
    - 연세대학교 응용통계학과 20학번
 - 조석희
    - 연세대학교 문헌정보학과 20학번
 - 엄윤희
    - 연세대학교 컴퓨터과학과 22학번
      
## app 프로젝트 실행방법
 - bash에서 실행
    - pip install -r requirements.txt
    - uvicorn app.main:app --reload
 - 브라우저에서 다음 주소로 접속
    - http://127.0.0.1:8000
  
## PNG 
 - branch_protection.png
    - <img width="547" alt="branch_protection" src="https://github.com/user-attachments/assets/d8555ec4-4c49-4700-95ab-bad78c23b334" />
 - push_rejected.png
    - <img width="547" alt="push_rejected" src="https://github.com/user-attachments/assets/e1b453e1-d49c-49c6-82b0-6a3fea6fae92" />
 - merged.png
    - <img width="547" alt="merged_lupin0326" src="https://github.com/user-attachments/assets/b40b7f0d-6a0f-453c-9fa6-51fb9ac9186e" />
    - <img width="547" alt="merged_joetae" src="https://github.com/user-attachments/assets/b183ce4d-115a-4355-ac2e-7247190c6b8d" />
    - <img width="547" alt="merged_yunbeeee" src="https://github.com/user-attachments/assets/0bcb2a76-c69d-40fe-8e92-5d9153ec3200" />

## 크롤링 실행 방법 및 데이터 소개

1. **다이닝코드 리뷰 크롤링**
   - **실행 명령**:
     ```bash
     python main.py -o {output_path} -c diningcode
     ```
   - **크롤링 사이트 링크**: [https://www.diningcode.com/profile.php?rid=L4miF0diqkcW](https://www.diningcode.com/profile.php?rid=L4miF0diqkcW)
   - **리뷰 수**: 총 408개

2. **구글맵스 리뷰 크롤링**
   - **실행 명령**:
     ```bash
     python main.py -o {output_path} -c googlemaps
     ```
   - **크롤링 사이트 링크**: [https://www.google.co.kr/maps/?hl=ko](https://www.google.co.kr/maps)
   - **리뷰 수**: 총 360개

3. **카카오맵 리뷰 크롤링**
   - **실행 명령**:
     ```bash
     python main.py -o {output_path} -c kakaomap
     ```
   - **크롤링 사이트 링크**: [https://map.kakao.com](https://map.kakao.com)
   - **데이터 개수**: 총 n개

4. **전체 크롤링 실행**
   - **실행 명령**:
     ```bash
     python main.py -o {output_path} --all
     ```
   - **설명**: 다이닝코드, 구글맵스, 카카오맵 리뷰 크롤러가 순차적으로 실행되며 모든 데이터는 지정한 `output_path`에 저장됩니다.
 
  - **크롤링 대상**: 명동교자 본점 리뷰 데이터
  - **데이터 구조**: `rating`, `date`, `content`의 3개 열로 구성
  - **데이터 저장 형식**: 모든 크롤링 데이터는 CSV 파일로 저장됩니다.
  - **저장 파일명**:
    - 다이닝코드: `reviews_diningcode.csv`
    - 구글맵스: `reviews_googlemaps.csv`
    - 카카오맵: `reviews_kakaomap.csv`

## EDA 그래프와 설명
- **특성**:
   - 1점~5점 내에 분포하는 별점
   - 각기 다른 형식으로 표현된 날짜(현재 시점 기준 상대적인 시간 표현)

- **결측치, 이상치 탐색**:
   - 별점, 날짜만 존재하며 내용은 작성되지 않은 경우
   - 정확한 날짜가 나타나 있지 않은 경우

## 전처리/FE 결과
- **결측치**: 내용이 없는 리뷰의 경우 별점에 따라 긍/부정이 나타나는 내용으로 대체
- **이상치**: 형식에 맞지 않은 날짜를 정규화하여 일관되게 표현
- **텍스트데이터 전처리**: 내용의 특수 문자 제거, 비정상적으로 긴 리뷰 길이 제한
- **파생변수**: 계절에 따른 파생변수 생성
- **FE**: 문맥 파악에 용이한 BERT 모델을 사용하여 텍스트 벡터화