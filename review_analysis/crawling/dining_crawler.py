from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import csv
from review_analysis.crawling.base_crawler import BaseCrawler


class DiningCodeCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = "https://www.diningcode.com/profile.php?rid=L4miF0diqkcW"
        self.reviews_data: list[dict[str, str]] = []

    def start_browser(self):
        # Selenium WebDriver 설정
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 디버깅 시 비활성화
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        """
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.83 Safari/537.36"
        )
        """
        service = Service("chromedriver")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def scrape_reviews(self):
        # 브라우저 열기
        self.start_browser()
        self.driver.get(self.base_url)
        time.sleep(5)  # 페이지 로드 대기

        existing_reviews = set()

        while True:
            time.sleep(3)  # 페이지 로드 대기
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # 리뷰, 별점, 날짜 추출
            review_texts = soup.select("p.review_contents.btxt")
            scores = soup.select("span.total_score")
            dates = soup.select("div.date")

            for review, score, date in zip(review_texts, scores, dates):
                review_data = {
                    "rating": score.text.strip(),
                    "date": date.text.strip(),
                    "review": review.text.strip()
                }
                # 중복 데이터 확인
                review_identifier = f"{review_data['review']}-{review_data['date']}"  # 고유 키 생성
                if review_identifier not in existing_reviews:
                    existing_reviews.add(review_identifier)
                    self.reviews_data.append(review_data)

            # "평가 더보기" 버튼 클릭
            try:
                more_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "More__Review__Button"))
                )
                self.driver.execute_script("arguments[0].click();", more_button)
                time.sleep(3)
            except Exception:
                # 더보기 버튼이 없으면 종료
                break

        self.driver.quit()

    def save_to_database(self):
        # 데이터 저장
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        file_path = os.path.join(self.output_dir, "reviews_diningcode.csv")
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["rating", "date", "review"])
            writer.writeheader()
            writer.writerows(self.reviews_data)
