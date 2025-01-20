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

## Crawling 및 review_analysis 실행 방법
 - 다이닝코드에서 명동교자 본점 리뷰 크롤링 실행 방법 
    - python main.py -o {output_path} -c diningcode
 - 크롤링 사이트 링크  
    - https://www.diningcode.com/profile.php?rid=L4miF0diqkcW
 - 데이터 구조 및 개수 
    - 평점, 날짜, 리뷰 총 3개의 열과 408개의 행으로 이루어져 있음.




 - 카카오맵, 구글맵, 다이닝코드 전체 리뷰 크롤링 실행 방법
    - python main.py -o {output_path} --all

