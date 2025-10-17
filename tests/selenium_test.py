# tests/selenium_test.py
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

class TestNYC311WebApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run without GUI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_positive_search(self):
        self.driver.get(f"{BASE_URL}/")
        self.driver.find_element(By.NAME, "borough").send_keys("BROOKLYN")
        self.driver.find_element(By.NAME, "complaint_type").send_keys("DOOR/WINDOW")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertGreater(len(rows), 1)

    def test_negative_search(self):
        self.driver.get(f"{BASE_URL}/")
        self.driver.find_element(By.NAME, "borough").send_keys("STATEN ISLAND")
        self.driver.find_element(By.NAME, "complaint_type").send_keys("INVALIDTYPE")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertEqual(len(rows), 1)

    def test_aggregate_page(self):
        self.driver.get(f"{BASE_URL}/aggregate")
        table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertGreater(len(rows), 1)

if __name__ == "__main__":
    unittest.main()
