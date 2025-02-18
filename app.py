import os
import time
import urllib.parse
import pandas as pd
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from flask import Flask, request, render_template, jsonify, Response, send_file
import threading

#from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
#import os

def get_driver():
    """ Selenium WebDriver 설정 (Docker 환경에서 실행 가능) """
    options = Options()
    options.add_argument("--headless")  # GUI 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    # ✅ Docker 컨테이너 내에서 Chrome 실행 경로 자동 탐색
    chrome_path = shutil.which("google-chrome") or shutil.which("chromium") or "/usr/bin/google-chrome"
    options.binary_location = chrome_path

    # ✅ ChromeDriver 실행 파일 경로 설정
    service = Service(shutil.which("chromedriver") or "/usr/bin/chromedriver")

    return webdriver.Chrome(service=service, options=options)
    
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"xlsx"}
RESULT_FILE = "상품가격조사.xlsx"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

search_status = {"running": False, "current": "대기 중", "total": 0, "completed": 0}
log_messages = []  # 진행 상태를 저장하는 리스트

def log_message(message):
    """ 로그 메시지를 리스트에 추가 """
    log_messages.append(message)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "파일이 없습니다."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "선택된 파일이 없습니다."}), 400

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], "상품목록.xlsx")
        file.save(filepath)
        log_message("파일 업로드 완료: 상품목록.xlsx")
        return jsonify({"message": "파일 업로드 성공! 검색을 시작하세요."})

    return jsonify({"message": "잘못된 파일 형식입니다. .xlsx 파일을 업로드하세요."}), 400

@app.route("/search", methods=["POST"])
def search():
    global search_status
    print(f"🛠 /search 요청 받음, 현재 상태: {search_status}")

    if search_status["running"]:
        return jsonify({"message": "이미 검색이 진행 중입니다. 잠시만 기다려 주세요."})
    if search_status["running"]:
        return jsonify({"message": "이미 검색이 진행 중입니다. 잠시만 기다려 주세요."})

    search_status["running"] = True
    search_status["current"] = "검색 시작"
    search_status["completed"] = 0

    def run_scraper():
        print("🛠 쓰레드 실행 중... process_product_list() 호출")
        process_product_list()
        search_status["running"] = False
        search_status["current"] = "검색 완료"

    thread = threading.Thread(target=run_scraper)
    thread.start()

    return jsonify({"message": "검색이 시작되었습니다. 완료 후 결과 파일을 확인하세요."})

@app.route("/logs")
def logs():
    """ 진행 상태를 실시간 스트리밍 """
    def generate():
        last_index = 0
        while search_status["running"]:
            new_logs = log_messages[last_index:]
            if new_logs:
                last_index += len(new_logs)
                yield "\n".join(new_logs) + "\n"
            time.sleep(1)
    return Response(generate(), mimetype="text/plain")

@app.route("/download")
def download_file():
    """ 검색 완료된 엑셀 파일 다운로드 """
    if os.path.exists(RESULT_FILE):
        return send_file(RESULT_FILE, as_attachment=True, download_name="상품가격조사.xlsx")
    else:
        return jsonify({"message": "결과 파일이 없습니다."}), 404

def search_product_on_site(query, site):
    print(f"🔍 {site}에서 '{query}' 검색 시작")  # 실행 확인용

    """ 특정 쇼핑몰(다나와, 에누리, 네이버쇼핑, 쿠팡)에서 상품 검색 후 정보 가져오기 """
    search_urls = {
        "다나와": f"https://search.danawa.com/dsearch.php?k1={urllib.parse.quote(query)}",
        "에누리": f"https://www.enuri.com/search.jsp?keyword={urllib.parse.quote(query)}",
        "네이버쇼핑": f"https://search.shopping.naver.com/search/all?query={urllib.parse.quote(query)}",
        "쿠팡": f"https://www.coupang.com/np/search?component=&q={urllib.parse.quote(query)}"
    }

    url = search_urls.get(site)
    if not url:
        return {"상품명": query, "가격": "정보 없음", "이미지": "정보 없음", "출처": "정보 없음"}

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36")

#    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)
    driver = get_driver()

    try:
        driver.get(url)
        time.sleep(3)

        item, price, image, link = None, None, None, None

        if site == "다나와":
            products = driver.find_elements(By.CSS_SELECTOR, ".product_list .prod_main_info")
        elif site == "에누리":
            products = driver.find_elements(By.CSS_SELECTOR, ".goods-list .goods-bundle .prodItem:not(.ad_smart)")
        elif site == "네이버쇼핑":
            products = driver.find_elements(By.CSS_SELECTOR, ".basicList_list_basis__uNBZx .product_item__MDtDF")
        elif site == "쿠팡":
            products = driver.find_elements(By.CSS_SELECTOR, ".search-product")

        if products:
            first_product = products[0]
            try:
                if site == "다나와":
                    item = first_product.find_element(By.CSS_SELECTOR, ".prod_name a").text
                    price = first_product.find_element(By.CSS_SELECTOR, ".price_sect strong").text
                    image = first_product.find_element(By.CSS_SELECTOR, ".thumb_image img").get_attribute("src")
                    link = first_product.find_element(By.CSS_SELECTOR, ".prod_name a").get_attribute("href")
                elif site == "에누리":
                    item = first_product.find_element(By.CSS_SELECTOR, ".item__model a").text
                    price = first_product.find_element(By.CSS_SELECTOR, ".tx--price").text
                    image = first_product.find_element(By.CSS_SELECTOR, ".item__thumb img").get_attribute("src")
                    link = first_product.find_element(By.CSS_SELECTOR, ".item__thumb a").get_attribute("href")
                elif site == "네이버쇼핑":
                    item = first_product.find_element(By.CSS_SELECTOR, ".product_title__Mmw2K a").text
                    price = first_product.find_element(By.CSS_SELECTOR, ".price_num__S2p_v").text
                    image = first_product.find_element(By.CSS_SELECTOR, ".thumbnail_thumb__Bxb6Z img").get_attribute("src")
                    link = first_product.find_element(By.CSS_SELECTOR, ".product_title__Mmw2K a").get_attribute("href")
                elif site == "쿠팡":
                    item = first_product.find_element(By.CSS_SELECTOR, ".name").text
                    price = first_product.find_element(By.CSS_SELECTOR, ".price-value").text
                    image = first_product.find_element(By.CSS_SELECTOR, ".search-product img").get_attribute("src")
                    link = "https://www.coupang.com" + first_product.find_element(By.CSS_SELECTOR, ".search-product a").get_attribute("href")
            except:
                pass

        return {
            "상품명": item if item else "정보 없음",
            "가격": price if price else "정보 없음",
            "이미지": image if image else "정보 없음",
            "출처": link if link else "정보 없음"
        }
    finally:
        driver.quit()

def process_product_list():
    print("🚀 검색 시작!")
    start_time = datetime.now()
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], "상품목록.xlsx")

    if not os.path.exists(file_path):
        log_message("❌ 상품목록.xlsx 파일이 없습니다.")
        return

    df = pd.read_excel(file_path)
    search_status["total"] = len(df)
    results = []

    for index, row in df.iterrows():
        query = row["상품명"]
        log_message(f"🔎 [{index+1}/{len(df)}] '{query}' 검색 중...")
        search_status["current"] = query
        result_data = {"상품명": query}

        prices = []
        for site in ["다나와", "에누리", "네이버쇼핑", "쿠팡"]:
            log_message(f"➡️ [{site}] 검색 중...")
            result = search_product_on_site(query, site)
            result_data[f"{site}_가격"] = result["가격"]
            result_data[f"{site}_상품명"] = result["상품명명"]
            result_data[f"{site}_출처"] = result["출처"]

            # **로그 메시지에 검색된 상품명과 가격 포함**
            log_message(f"✅ [{site}] {result['상품명']} - {result['가격']}")

            try:
                prices.append(int(result["가격"].replace(",", "").replace("원", "")))
            except:
                pass

        # **가격 분석 추가 (최고/최저/평균/표준편차/변동계수)**
        if prices:
            result_data["최고가격"] = max(prices)
            result_data["최저가격"] = min(prices)
            result_data["평균가격"] = np.mean(prices)
#            result_data["표준편차"] = np.std(prices)
            result_data["변동계수"] = np.std(prices) / np.mean(prices)
        results.append(result_data)
        search_status["completed"] += 1

    end_time = datetime.now()
    df_results = pd.DataFrame(results)
    df_results.loc[len(df_results)] = {
        "상품명": "검색 시작 시각", "최고가격": start_time, "최저가격": "검색 종료 시각", "평균가격": end_time
    }
    df_results.to_excel(RESULT_FILE, index=False)
    log_message("✅ 엑셀 저장 완료: 상품가격조사.xlsx")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
