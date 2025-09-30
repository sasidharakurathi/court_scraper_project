from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import base64
from io import BytesIO
from PIL import Image
import time

class CourtScraper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.__init_options()
        
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
    
        self.wait = WebDriverWait(self.driver, 10)
    
    def __init_options(self):
        # self.options.add_argument("--headless")
        # self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920x1080")
        self.options.add_experimental_option("detach", True)
        
class HighCourtScraper(CourtScraper):
    def __init__(self,url="https://hcservices.ecourts.gov.in/hcservices/main.php"):
        self.url = url
        super().__init__()
    
    def navigate_to_case_status(self):
        self.driver.get(self.url)
        case_status_anchor = self.wait.until(EC.visibility_of_element_located((By.ID, 'leftPaneMenuCS')))
        self.driver.execute_script("arguments[0].click();", case_status_anchor)
        
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='OK']"))
        ).click()
    
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
        
        self.wait.until(
            EC.element_to_be_clickable((By.ID, "CScaseNumber"))
        ).click()
        
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
        refresh_btn = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "refresh-btn"))
        )

        refresh_btn.click()

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
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Go' and @class='Gobtn']"))
        )
        go_btn.click()
        time.sleep(1)
    
    
    def click_view_by_full_case_number(self, case_type_text, case_number, year):
        
        temp = ""
        for c in str(case_type_text):
            if c == "(":
                break
            temp += c
        
        case_type_text = temp

        full_case_number = str(case_type_text) + "/" + str(case_number) + "/" + str(year)
        
        
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
        
        view_link.click()


    
    def fetch_case(self, case_type_id, case_number, year, captcha, case_type_text):
        self.select_case_type(case_type_id)
        self.set_case_number(case_number)
        self.set_year(year)
        self.set_captcha(captcha)
        
        self.click_go_button()
        
        for _ in range(3):
            try:
                self.click_view_by_full_case_number(case_type_text, case_number, year)
                break
            except:
                time.sleep(1)

        
        print("Done: ")


if __name__ == "__main__":
    scraper = HighCourtScraper()
    scraper.navigate_to_case_status()
    scraper.fetch_highcourt_list()
    