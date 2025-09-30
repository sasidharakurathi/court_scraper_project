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
        # self.options.add_argument("--headless")  # You can uncomment this to run without a UI
        # self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920x1080")
        self.options.add_experimental_option("detach", True)  # <-- keeps browser open
        
class HighCourtScraper(CourtScraper):
    def __init__(self,url="https://hcservices.ecourts.gov.in/hcservices/main.php"):
        self.url = url
        super().__init__()
    
    def navigate_to_case_status(self):
        self.driver.get(self.url)
        case_status_anchor = self.wait.until(EC.visibility_of_element_located((By.ID, 'leftPaneMenuCS')))
        # case_status_anchor.click()
        self.driver.execute_script("arguments[0].click();", case_status_anchor)
        
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='OK']"))
        ).click()
    
    def fetch_highcourt_list(self):
        # Locate the High Court <select> element
        highcourt_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "sess_state_code"))
        )

        # Get all options
        options = highcourt_select.find_elements(By.TAG_NAME, "option")

        # Prepare a list of dictionaries
        high_courts = []
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if value != "0":  # skip the default
                high_courts.append({"id": value, "name": text})

        return high_courts

    def fetch_bench_list(self):
        # court_complex_code
        
        bench_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "court_complex_code"))
        )
        
        # Get all options
        options = bench_select.find_elements(By.TAG_NAME, "option")
        
        # Prepare a list of dictionaries
        benches = []
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if value != "0":  # skip the default
                benches.append({"id": value, "name": text})
        # print(f"{benches = }")
        return benches

    def fetch_case_types(self):
        # case_type
        
        case_type_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "case_type"))
        )
        
        # Get all options
        options = case_type_select.find_elements(By.TAG_NAME, "option")
        
        # Prepare a list of dictionaries
        case_types = []
        for opt in options:
            value = opt.get_attribute("value")
            text = opt.text.strip()
            if value != "0":  # skip the default
                case_types.append({"id": value, "name": text})
        print(f"{case_types = }")
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
        
    def refresh_captcha(self):
        # Wait until the refresh button is clickable
        refresh_btn = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "refresh-btn"))
        )

        # Click it
        refresh_btn.click()

        time.sleep(1)  
    
    def get_captcha_image(self):
        # captcha_image
        
        self.refresh_captcha()
        
        # Wait for captcha image element
        captcha_elem = self.wait.until(
            EC.visibility_of_element_located((By.ID, "captcha_image"))
        )

        # Take screenshot of the element
        png = captcha_elem.screenshot_as_png  # raw PNG bytes

        # Convert to base64 string to send via JSON
        b64_png = base64.b64encode(png).decode("utf-8")

        return b64_png



# def get_states():
#     """
#     Uses Selenium to scrape the list of states from the eCourts website.
#     Returns a list of dictionaries, each containing the state's name and value.
#     """
#     # Setup Selenium WebDriver
#     options = webdriver.ChromeOptions()
#     # options.add_argument("--headless")  # You can uncomment this to run without a UI
#     # options.add_argument("--disable-gpu")
#     options.add_argument("--window-size=1920x1080")

#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

#     states = []
#     try:
#         # Navigate to the website
#         url = 'https://services.ecourts.gov.in/ecourtindia_v6/'
#         driver.get(url)
#         wait = WebDriverWait(driver, 10)
        
#         # Navigate to the Case Status page
#         case_status_anchor = wait.until(EC.visibility_of_element_located((By.ID, 'leftPaneMenuCS')))
#         case_status_url = case_status_anchor.get_attribute('href')
        
#         if not case_status_url:
#             print("Could not find the Case Status URL.")
#             return [] # Return empty list if URL not found
            
#         driver.get(case_status_url)
#         print(f"Successfully navigated to: {driver.current_url}")

#         # --- NEW CODE STARTS HERE ---

#         # 1. Wait for the state dropdown to be visible
#         state_dropdown = wait.until(
#             EC.visibility_of_element_located((By.ID, "sess_state_code"))
#         )
        
#         # 2. Find all the <option> elements within the dropdown
#         options_list = state_dropdown.find_elements(By.TAG_NAME, "option")
        
#         print(f"Found {len(options_list)} options in the dropdown.")

#         # 3. Loop through each option to scrape its details
#         for option in options_list:
#             # Get the value attribute (e.g., '1', '2', etc.)
#             state_value = option.get_attribute('value')
            
#             # Get the visible text (e.g., 'Andaman and Nicobar Portblair')
#             state_name = option.text
            
#             # 4. Skip the first disabled option ("Select State") and add the rest
#             if state_value: # This check skips options with an empty value
#                 states.append({
#                     "name": state_name.strip(),
#                     "value": state_value
#                 })

#     except Exception as e:
#         print(f"An error occurred: {e}")

#     finally:
#         driver.quit() # Always close the browser

#     return states


if __name__ == "__main__":
    scraper = HighCourtScraper()
    scraper.navigate_to_case_status()
    scraper.fetch_highcourt_list()
    