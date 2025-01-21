from review_analysis.crawling.base_crawler import BaseCrawler
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import sys
import os

# 현재 파일의 경로를 기준으로 utils 디렉토리 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))  # googlemaps_crawler.py 위치
utils_dir = os.path.join(current_dir, '..', '..', 'utils')  # utils 디렉토리 경로 설정

# utils 디렉토리를 sys.path에 추가
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

# logger.py에서 setup_logger 함수 임포트
from logger import setup_logger # type: ignore

class GoogleMapsCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://www.google.co.kr/maps/?hl=ko'
        self.review_data = []  # 크롤링 데이터를 저장할 변수
        log_file_name = 'googlemaps_crawler.log'
        self.logger = setup_logger(log_file=log_file_name)  # 로거 설정
        self.logger.info("GoogleMapsCrawler가 초기화되었습니다.")
        
    def start_browser(self):
        try: 
            options = Options()
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_experimental_option("detach", True)
            self.driver = webdriver.Chrome(options=options)
            self.logger.info("브라우저가 성공적으로 시작되었습니다.")
        except Exception as e:
            self.logger.error(f"브라우저 시작 중 오류 발생: {e}")
            raise
    
    def scrape_reviews(self, search_query: str = "명동교자", target_count: int = 1000):
        self.logger.info(f"'{search_query}'에 대한 리뷰 크롤링을 시작합니다.")
        try:
            self.start_browser()
            self.driver.get(self.base_url)
            self.driver.maximize_window() # 브라우저의 크기 전체화면으로 확대
            # 검색
            search_box = self.driver.find_element(By.ID, "searchboxinput")
            search_box.clear()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)

            # 페이지 로드 대기
            time.sleep(5)
            self.logger.info(f"'{search_query}'에 대한 검색이 완료되었습니다.")

            #첫 번째 리스트의 가게(본점) 클릭
            self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[3]/div/a').click()
            
            # 리뷰 버튼 클릭
            review_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='명동교자 본점 리뷰']"))
            )
            review_button.click()
            time.sleep(5)

            # 리뷰 크롤링
            SCROLL_PAUSE_TIME = 5  # 스크롤 대기 시간
            last_height = 0  # 스크롤 높이 초기화

            # 리뷰 리스트 컨테이너
            review_container = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]')

            while len(self.review_data) < target_count:
                # '자세히' 버튼 클릭
                more_buttons = self.driver.find_elements(By.CLASS_NAME, "w8nwRe")
                for button in more_buttons:
                    try:
                        button.click()
                        time.sleep(1)  # 클릭 후 대기
                    except Exception as e:
                        self.logger.warning(f"'자세히' 버튼 클릭 중 오류 발생: {e}")

                # 현재 페이지의 리뷰 HTML 파싱
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                reviews = soup.find_all('div', class_='jftiEf')  # 리뷰 아이템 컨테이너

                for review in reviews:
                    blank = []

                    # 별점 크롤링
                    rating_element = review.find('span', class_='kvMYJc')
                    if rating_element:
                        rating = rating_element.get('aria-label')  # 예: "별표 5개"
                        rating = re.search(r'\d+', rating).group()  # 숫자만 추출
                        blank.append(rating)
                    else:
                        blank.append("N/A")

                    # 날짜 크롤링
                    date_element = review.find('span', class_='rsqaWe')
                    if date_element:
                        date = date_element.text.strip()
                        blank.append(date)
                    else:
                        blank.append("N/A")

                    # 리뷰 내용 크롤링
                    content_element = review.find('span', class_='wiI7pd')
                    if content_element:
                        content = content_element.text.strip()
                        blank.append(content)
                    else:
                        blank.append("N/A")

                    # 데이터 저장 (중복 방지)
                    if blank not in self.review_data:
                        self.review_data.append(blank)

                    # 목표 개수 도달 시 루프 종료
                    if len(self.review_data) >= target_count:
                        break

                # 스크롤 동작
                self.driver.execute_script('arguments[0].scrollBy(0, 1500);', review_container)
                time.sleep(SCROLL_PAUSE_TIME)

                # 현재 컨테이너 높이 확인
                new_height = self.driver.execute_script("return arguments[0].scrollHeight;", review_container)

                # 스크롤 한계 체크
                if new_height == last_height:
                    self.logger.info("더 이상 스크롤할 내용이 없습니다.")
                    break
                last_height = new_height

                self.logger.info(f"현재까지 크롤링된 리뷰 개수: {len(self.review_data)}개")

            self.logger.info(f"총 {len(self.review_data)}개의 리뷰를 크롤링했습니다.")

        except Exception as e:
            self.logger.error(f"리뷰 크롤링 중 오류 발생: {e}")
            raise
    
    def save_to_database(self):
        try:
            if not self.review_data:
                self.logger.warning("저장할 데이터가 없습니다. 먼저 scrape_reviews를 실행하세요.")
                raise ValueError("저장할 데이터가 없습니다.")
            
            # 데이터 저장 경로 설정
            database_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'database')
            os.makedirs(database_dir, exist_ok=True)  # database 디렉토리가 없으면 생성
            
            # 저장할 파일 경로
            file_path = os.path.join(database_dir, 'reviews_googlemaps.csv')

            # 크롤링한 데이터를 DataFrame으로 변환
            df = pd.DataFrame(self.review_data, columns=["rating", "date", "content"])

            # CSV 파일로 저장
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            self.logger.info(f"크롤링 데이터를 {file_path}에 저장했습니다.")
        except Exception as e:
            self.logger.error(f"데이터 저장 중 오류 발생: {e}")
