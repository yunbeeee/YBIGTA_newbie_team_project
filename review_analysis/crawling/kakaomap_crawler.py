import os
import time
import csv
#from base_crawler import BaseCrawler
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from review_analysis.crawling.base_crawler import BaseCrawler
from logger import setup_logger

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class KakaomapCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = "https://place.map.kakao.com/10332413"  # 카카오맵 리뷰 페이지의 기본 URL을 설정
        self.driver = None
        self.reviews = []
        self.logger = setup_logger()
        
    def start_browser(self):
        self.logger.info("WebDriver를 초기화합니다...")
        options = Options()
        options.add_argument("headless")
        # # chromedriver 경로를 절대경로로 수정
        # chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
        
        # # chromedriver 경로가 실제 존재하는지 확인
        # if not os.path.exists(chromedriver_path):
        #     self.logger.error(f"chromedriver 경로가 잘못되었습니다: {chromedriver_path}")
        #     raise FileNotFoundError(f"chromedriver를 찾을 수 없습니다. 경로를 확인해주세요: {chromedriver_path}")
        
        # # Service 객체로 chromedriver 경로 설정
        # service = Service(chromedriver_path)

        try:
            #self.driver = webdriver.Chrome(service=service, options=options)
            self.driver = webdriver.Chrome(options=options)
            self.logger.info("WebDriver가 성공적으로 초기화되었습니다.")
        except Exception as e:
            self.logger.error(f"WebDriver 초기화 실패: {e}")
            raise       

    
    def scrape_reviews(self):
        self.start_browser()
        self.logger.info("Start scraping reviews...")
        self.driver.get(self.base_url)
        time.sleep(3)
        try:
            # '후기 더보기' 버튼을 클릭하여 리뷰를 추가로 로드
            load_more_button_xpath = '//a[@href="#none" and @class="link_more"]'
            reviews_collected = 0
            while reviews_collected < 1000:

                # 새로운 리뷰가 로드되었으므로, 다시 리뷰를 찾습니다.
                soup = BeautifulSoup(self.driver.page_source, 'html.parser', from_encoding='utf-8')
                reviews = soup.select("li:has(.comment_info .txt_comment)")
                for review in reviews:
                    # 1. 날짜 추출
                    try:
                        date = review.select_one(".time_write").get_text(strip=True)
                    except AttributeError:
                        date = "날짜 없음"
                    
                    # 2. 별점 추출 (style 속성에서 width 값 추출)
                    try:
                        star_element = review.select_one(".star_info .grade_star.size_s .ico_star.inner_star")
                        if star_element:
                            style = star_element.get("style", "")
                            width_percentage = int(style.split(":")[1].replace("%;", "").strip())
                            star_rating = width_percentage / 20  # 별점 계산
                        else:
                            star_rating = "별점 없음"
                    except AttributeError:
                        star_rating = "별점 없음"

                    
                    # 3. 리뷰 내용 추출
                    try:
                        comment = review.select_one(".txt_comment span").get_text(strip=True)
                    except AttributeError:
                        comment = "리뷰 내용 없음"
                    
                    # 리뷰 정보를 self.reviews 리스트에 저장
                    self.reviews.append({'rating': star_rating, 'date': date, 'content': comment})
                    reviews_collected += 1
                    
                    # 1000개 리뷰 수집 후 종료
                    if reviews_collected >= 1000:
                        break                
                
                # '후기 더보기' 버튼을 기다렸다가 클릭
                try:
                    load_more_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, load_more_button_xpath))
                    )
                    load_more_button.click()
                    self.logger.info(f"'후기 더보기' 버튼 클릭: {reviews_collected}개의 리뷰를 수집 중...")
                    time.sleep(3)  # 페이지 업데이트 대기
                except Exception as e:
                    self.logger.error(f"후기 더보기 버튼 클릭 중 오류 발생: {e}")
                    break  # 더 이상 '후기 더보기' 버튼이 없으면 종료

            self.logger.info(f"총 {reviews_collected}개의 리뷰를 수집했습니다.")

        except Exception as e:
            self.logger.error(f"리뷰 크롤링 중 오류 발생: {e}")
            raise
    def save_to_database(self):
        """리뷰 데이터를 CSV 파일에 저장"""
        self.logger.info("CSV 파일에 데이터 저장 중...")
        output_file = os.path.join(self.output_dir, 'reviews_kakaomap.csv')
        
        # CSV로 저장
        try:
            with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=['rating', 'date', 'content'])
                writer.writeheader()
                writer.writerows(self.reviews)
            self.logger.info(f"리뷰 {len(self.reviews)}개를 {output_file}에 저장했습니다.")
        except Exception as e:
            self.logger.error(f"CSV 저장 실패: {e}")
            raise

    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            self.logger.info("브라우저가 정상적으로 종료되었습니다.")