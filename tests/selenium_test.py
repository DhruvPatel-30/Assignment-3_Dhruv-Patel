# tests/selenium_test.py
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:5000"  # CI-friendly localhost

class TestNYC311WebApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Use webdriver-manager to automatically handle ChromeDriver
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_positive_search(self):
        """Positive test: valid filters return results"""
        self.driver.get(f"{BASE_URL}/")
        self.driver.find_element(By.NAME, "borough").send_keys("BROOKLYN")
        self.driver.find_element(By.NAME, "complaint_type").send_keys("DOOR/WINDOW")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertGreater(len(rows), 1, "Expected at least one row in search results")

    def test_negative_search(self):
        """Negative test: invalid filters return 0 results"""
        self.driver.get(f"{BASE_URL}/")
        self.driver.find_element(By.NAME, "borough").send_keys("STATEN ISLAND")
        self.driver.find_element(By.NAME, "complaint_type").send_keys("INVALIDTYPE")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertEqual(len(rows), 1, "Expected 0 results (only header row)")

    def test_aggregate_page(self):
        """Test aggregate page loads correctly"""
        self.driver.get(f"{BASE_URL}/aggregate")
        table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertGreater(len(rows), 1, "Expected aggregate table with at least one borough")

if __name__ == "__main__":
    unittest.main()
