from django.conf import settings

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

import base64
import time

from bs4 import BeautifulSoup
import requests
import os

class CourtScraper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.__init_options()
        
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
    
        self.wait = WebDriverWait(self.driver, 10)
    
    def __init_options(self):
        self.options.add_argument("--start-fullscreen")
        self.options.add_argument("--headless")
        # self.options.add_argument("--headless=new")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920x1080")
        self.options.add_experimental_option("detach", True)
        # self.options.add_argument("--force-device-scale-factor=1")
        
    
    def safe_click(self, element):
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)
            
    def download_pdf(self, url, pdf_filename, pdf_path, static_path):
        cookies = self.driver.get_cookies()
        cookies_dict = {c['name']: c['value'] for c in cookies}
        if not os.path.exists(pdf_path):
            response = requests.get(url, cookies=cookies_dict, headers={'User-Agent': 'Mozilla/5.0'})
        
            with open(pdf_path, "wb") as f:
                f.write(response.content)
        
        return f"/{static_path}/{pdf_filename}"
    
        
class HighCourtScraper(CourtScraper):
    def __init__(self,url="https://hcservices.ecourts.gov.in/hcservices/main.php"):
        self.url = url
        super().__init__()
    
    def navigate_to_case_status(self):
        self.driver.get(self.url)
        case_status_anchor = self.wait.until(EC.visibility_of_element_located((By.ID, 'leftPaneMenuCS')))
        self.driver.execute_script("arguments[0].click();", case_status_anchor)
        
        modal_ok_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='OK']"))
        )
        
        self.safe_click(modal_ok_button)
    
    def fetch_highcourt_list(self):
        highcourt_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "sess_state_code"))
        )

        options = highcourt_select.find_elements(By.TAG_NAME, "option")

        high_courts = []
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if value != "0":
                high_courts.append({"id": value, "name": text})

        return high_courts

    def fetch_bench_list(self):
        bench_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "court_complex_code"))
        )
        
        options = bench_select.find_elements(By.TAG_NAME, "option")
        
        benches = []
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if value != "0":
                benches.append({"id": value, "name": text})
        # print(f"{benches = }")
        return benches

    def fetch_case_types(self):
        case_type_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "case_type"))
        )
        
        options = case_type_select.find_elements(By.TAG_NAME, "option")
        
        case_types = []
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if value != "0":
                case_types.append({"id": value, "name": text})
        # print(f"{case_types = }")
        return case_types
    
    def select_highcourt_by_id(self, highcourt_id):
        self.navigate_back()
        highcourt_select_elem = self.wait.until(
            EC.presence_of_element_located((By.ID, "sess_state_code"))
        )
        
        select = Select(highcourt_select_elem)
        select.select_by_value(str(highcourt_id))
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", highcourt_select_elem)

    def select_bench_by_id(self, bench_id):
        self.navigate_back()
        bench_select_elem = self.wait.until(
            EC.presence_of_element_located((By.ID, "court_complex_code"))
        )
        
        select = Select(bench_select_elem)
        select.select_by_value(str(bench_id))
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", bench_select_elem)
        
        case_number_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "CScaseNumber"))
        )
        self.safe_click(case_number_button)
        
    def select_case_type(self, case_type_id):
        # case_type
        
        case_type_select_elem = self.wait.until(
            EC.presence_of_element_located((By.ID, "case_type"))
        )
        
        select = Select(case_type_select_elem)
        select.select_by_value(str(case_type_id))
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", case_type_select_elem)
        time.sleep(1)
        
    def set_case_number(self, case_number):
        # search_case_no
        case_number_input_elem = self.wait.until(
            EC.visibility_of_element_located((By.ID, "search_case_no"))
        )
        case_number_input_elem.clear()
        case_number_input_elem.send_keys(str(case_number))
        time.sleep(1)
        
    def set_year(self, year):
        # rgyear
        year_input_elem = self.wait.until(
            EC.visibility_of_element_located((By.ID, "rgyear"))
        )
        year_input_elem.clear()
        year_input_elem.send_keys(str(year))
        time.sleep(1)
        
    def set_captcha(self, captcha):
        # captcha
        captcha_input_elem = self.wait.until(
            EC.visibility_of_element_located((By.ID, "captcha"))
        )
        captcha_input_elem.clear()
        captcha_input_elem.send_keys(str(captcha))
        time.sleep(1)
        
    def refresh_captcha(self):
        self.navigate_back()
        refresh_btn = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "refresh-btn"))
        )
        
        # self.driver.execute_script("arguments[0].scrollIntoView(true);", refresh_btn)

        # refresh_btn.click()
        
        # Direct JS click
        # self.driver.execute_script("arguments[0].click();", refresh_btn)
        self.safe_click(refresh_btn)

        time.sleep(1)  
    
    def get_captcha_image(self):
        # captcha_image
        self.refresh_captcha()
        
        captcha_elem = self.wait.until(
            EC.visibility_of_element_located((By.ID, "captcha_image"))
        )
        time.sleep(1)
        png = captcha_elem.screenshot_as_png

        b64_png = base64.b64encode(png).decode("utf-8")

        return b64_png

    def click_go_button(self):
        # Gobtn
        go_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Go' and @class='Gobtn']"))
        )
        # go_btn.click()
        self.safe_click(go_btn)
        time.sleep(1)
    
    
    def click_view_by_full_case_number(self, full_case_number):
        
        
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//tbody/tr"))
        )

        row = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//td[contains(text(), '{full_case_number}')]/..")
            )
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", row)
        
        view_link = row.find_element(By.XPATH, ".//a[text()='View']")
            
        self.wait.until(EC.element_to_be_clickable((By.XPATH, ".//a[text()='View']")))
        
        # view_link.click()
        self.safe_click(view_link)

    def navigate_back(self):
        try:
            back_button = WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='backTopDiv']//input[@id='bckbtn']"))
            )
            back_button.click()
            print("Back button clicked.")
        except TimeoutException:
            print("Back button not found, skipping click.")
    
    def fetch_case(self, case_type_id, case_number, year, captcha, case_type_text):
        self.navigate_back()
        self.select_case_type(case_type_id)
        self.set_case_number(case_number)
        self.set_year(year)
        self.set_captcha(captcha)
        
        self.click_go_button()
        
        try:
            error_p = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, "//div[@id='errSpan']/p"))
            )
            print("error_p.text: " , error_p.text)
            if error_p.text == "Invalid Captcha" or error_p.text == "Record Not Found":
                return error_p.text
        except TimeoutException:
            print("TimeoutException: ")
        
        temp = ""
        for c in str(case_type_text):
            if c == "(":
                break
            temp += c
        
        case_type_text = temp

        full_case_number = str(case_type_text) + "/" + str(case_number) + "/" + str(year)
        
        for _ in range(3):
            try:
                self.click_view_by_full_case_number(full_case_number)
                break
            except:
                time.sleep(1)
                
        case_results = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@align='center'][.//div[@id='caseBusinessDiv4']]")))
        html_content = case_results.get_attribute("innerHTML")
        json_result = self.parse_full_case_with_pdf(html_content, full_case_number)

        # print(f"{json_result = }")
        
        print("Done: ")
        
        return json_result 
        
    def parse_full_case_with_pdf(self, html, full_case_number):
        soup = BeautifulSoup(html, "html.parser")
        result = {}

        # --- Case Details ---
        case_table = soup.find("table", class_="case_details_table")
        case_details = {}
        if case_table:
            rows = case_table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                for i in range(0, len(cols), 2):
                    key = cols[i].get_text(strip=True)
                    value = cols[i+1].get_text(strip=True)
                    case_details[key] = value
        result["case_details"] = case_details

        # --- Case Status ---
        status_table = soup.find("table", class_="table_r")
        case_status = {}
        if status_table:
            for row in status_table.find_all("tr"):
                cols = row.find_all("td")
                key = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                case_status[key] = value
        result["case_status"] = case_status

        # --- Petitioner and Respondent ---
        petitioner = soup.find("span", class_="Petitioner_Advocate_table")
        respondent = soup.find("span", class_="Respondent_Advocate_table")
        result["petitioner"] = petitioner.get_text(strip=True) if petitioner else ""
        result["respondent"] = respondent.get_text(strip=True) if respondent else ""

        # --- Category Details ---
        category_table = soup.find("table", id="subject_table")
        category_details = {}
        if category_table:
            for row in category_table.find_all("tr"):
                cols = row.find_all("td")
                key = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                category_details[key] = value
        result["category_details"] = category_details

        # --- IA Details ---
        ia_table = soup.find("table", class_="IAheading")
        ia_list = []
        if ia_table:
            rows = ia_table.find_all("tr")[1:]  # skip header
            for row in rows:
                cols = [col.get_text(strip=True) for col in row.find_all("td")]
                if cols:
                    ia_list.append({
                        "IA Number": cols[0],
                        "Party": cols[1],
                        "Date of Filing": cols[2],
                        "Next Date": cols[3],
                        "IA Status": cols[4]
                    })
        result["ia_details"] = ia_list

        # --- Case History ---
        history_table = soup.find("table", class_="history_table")
        history_list = []
        if history_table:
            rows = history_table.find_all("tr")[1:]  # skip header
            for row in rows:
                cols = [col.get_text(strip=True) for col in row.find_all("td")]
                if cols:
                    history_list.append({
                        "Cause List Type": cols[0],
                        "Judge": cols[1],
                        "Business On Date": cols[2],
                        "Hearing Date": cols[3],
                        "Purpose of hearing": cols[4]
                    })
        result["case_history"] = history_list

        # --- Orders ---
        orders_table = soup.find("table", class_="order_table")
        orders_list = []
        if orders_table:
            rows = orders_table.find_all("tr")[1:]  # skip header
            for row in rows:
                cols = row.find_all("td")
                if cols:
                    # extract the PDF link if available
                    link_tag = cols[4].find("a")
                    pdf_url =  None
                    
                    if link_tag:
                        # link_tag["href"]
                        url = "https://hcservices.ecourts.gov.in/hcservices/" + link_tag["href"]
                        
                        order_date = cols[3].get_text(strip=True)
                        
                        full_case_number = full_case_number.replace('/', '_')
                        order_date = order_date.replace('-', '')
                        pdf_filename = f"{full_case_number}_{order_date}.pdf"
                        
                        save_dir = settings.HIGHCOURT_ORDERS_PDF_DIR
                        os.makedirs(save_dir, exist_ok=True)  # ensure folder exists
                        pdf_path = os.path.join(save_dir, pdf_filename)
                        
                        static_path = settings.STATIC_HIGHCOURT_ORDERS_PDF_DIR
                        pdf_url = self.download_pdf(url,pdf_filename, pdf_path, static_path)
                        # pdf_url = self.download_pdf(url,full_case_number, cols[3].get_text(strip=True))

                    orders_list.append({
                        "Order Number": cols[0].get_text(strip=True),
                        "Order on": cols[1].get_text(strip=True),
                        "Judge": cols[2].get_text(strip=True),
                        "Order Date": cols[3].get_text(strip=True),
                        "Order Details": cols[4].get_text(strip=True),
                        "PDF URL": str(pdf_url)
                    })
        result["orders"] = orders_list

        return result

class HighCourtCauseListScraper(CourtScraper):
    def __init__(self,url="https://hcservices.ecourts.gov.in/hcservices/main.php"):
        self.url = url
        super().__init__()
    
    def navigate_to_cause_list(self):
        self.driver.get(self.url)
        case_status_anchor = self.wait.until(EC.visibility_of_element_located((By.ID, 'leftPaneMenuCL')))
        self.driver.execute_script("arguments[0].click();", case_status_anchor)
        
        modal_ok_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='OK']"))
        )
        
        self.safe_click(modal_ok_button)
    
    def fetch_highcourt_list(self):
        highcourt_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "sess_state_code"))
        )

        options = highcourt_select.find_elements(By.TAG_NAME, "option")

        high_courts = []
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if value != "0":
                high_courts.append({"id": value, "name": text})

        return high_courts
    
    def fetch_bench_list(self):
        
        bench_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "court_complex_code"))
        )
        
        options = bench_select.find_elements(By.TAG_NAME, "option")
        
        benches = []
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if value != "0":
                benches.append({"id": value, "name": text})
        # print(f"{benches = }")
        return benches
    
    
    
    
    def select_highcourt_by_id(self, highcourt_id):
        highcourt_select_elem = self.wait.until(
            EC.presence_of_element_located((By.ID, "sess_state_code"))
        )
        
        select = Select(highcourt_select_elem)
        select.select_by_value(str(highcourt_id))
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", highcourt_select_elem)

    def select_bench_by_id(self, bench_id):
        bench_select_elem = self.wait.until(
            EC.presence_of_element_located((By.ID, "court_complex_code"))
        )
        
        select = Select(bench_select_elem)
        select.select_by_value(str(bench_id))
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", bench_select_elem)
        
    def set_captcha(self, captcha):
        # captcha
        
        captcha_input_elem = self.wait.until(
            EC.visibility_of_element_located((By.ID, "captcha"))
        )
        captcha_input_elem.clear()
        captcha_input_elem.send_keys(str(captcha))
        time.sleep(1)
    
    
    def refresh_captcha(self):
        refresh_btn = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "refresh-btn"))
        )
        
        self.safe_click(refresh_btn)

        time.sleep(1) 
        
    def get_captcha_image(self):
        # captcha_image
        
        self.refresh_captcha()
        
        captcha_elem = self.wait.until(
            EC.visibility_of_element_located((By.ID, "captcha_image"))
        )


        png = captcha_elem.screenshot_as_png

        b64_png = base64.b64encode(png).decode("utf-8")

        return b64_png
    
    def click_go_button(self):
        # Gobtn
        go_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "butCivil"))
        )
        # go_btn.click()
        self.safe_click(go_btn)
        time.sleep(1)
    
    def fetch_cause_lists(self, high_court, cause_bench, cause_date, cause_captcha):
        
        date_input = self.wait.until(
            EC.visibility_of_element_located((By.ID, "causelist_date"))
        )
        
        self.driver.execute_script("arguments[0].value = arguments[1];", date_input, cause_date)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", date_input)
        
        self.set_captcha(cause_captcha)
        
        self.click_go_button()
        
        case_results = self.wait.until(EC.presence_of_element_located((By.ID, "div_Causelist")))
        html_content = case_results.get_attribute("innerHTML")
        
        if html_content == "Invalid Captcha" or html_content in "Invalid Captcha" or "Invalid Captcha" in html_content:
            return "Invalid Captcha"
        elif html_content == '{"Error":"ERROR_VAL"}':
            return "Invalid Data"
        elif "No cause List Available" in html_content:
            return "No cause List Available for this date...!!"
            
            

        
        json_result = self.parse_cause_lists(html_content, cause_date)
        
        return json_result
        
    def parse_cause_lists(self, html_content, cause_date):
        
        high_court_host_url = "https://hcservices.ecourts.gov.in/hcservices/"
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        table = soup.find("table", class_="causelistTbl")
        
        # Extract headers
        headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

        # Extract rows
        rows = []
        for row_id, tr in enumerate(table.find("tbody").find_all("tr")):
            cells = tr.find_all("td")
            row_data = {}
            for i, cell in enumerate(cells):
                # Check if it has a link
                a_tag = cell.find("a")
                if a_tag:
                    url = high_court_host_url + str(a_tag.get("href"))
                    
                    cause_date = cause_date.replace('-', '')
                    pdf_filename = f"{cause_date}_{row_id+1}.pdf"
                    
                    save_dir = os.path.join(settings.HIGHCOURT_CASELIST_PDF_DIR , cause_date)
                    os.makedirs(save_dir, exist_ok=True)  # ensure folder exists
                    pdf_path = os.path.join(save_dir, pdf_filename)
                    
                    static_path = os.path.join(settings.STATIC_HIGHCOURT_CASELIST_PDF_DIR, cause_date)
                    pdf_url = self.download_pdf(url, pdf_filename, pdf_path, static_path)
                    row_data[headers[i]] = {
                        "text": a_tag.get_text(strip=True),
                        "href": pdf_url
                    }
                else:
                    row_data[headers[i]] = cell.get_text(strip=True)
            rows.append(row_data)
            
        return rows
        


if __name__ == "__main__":
    scraper = HighCourtScraper()
    scraper.navigate_to_case_status()
    scraper.fetch_highcourt_list()
    