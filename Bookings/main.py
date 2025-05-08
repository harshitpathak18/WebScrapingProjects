import time
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_hotels_selenium(url, filename):
    # Set up Selenium driver
    service = Service('chromedriver.exe')  # Ensure correct path
    options = Options()
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    
    driver.get(url)
    
    # Infinite scroll
    height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if height == new_height:
            break
        height = new_height
    
    # Extract hotel cards
    hotel_cards = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'div[data-testid="property-card"]')
    ))
    
    rows = []
    for hotel in hotel_cards:
        try:
            hotel_name = hotel.find_element(By.CSS_SELECTOR, 'div[data-testid="title"]').text
        except:
            hotel_name = np.nan
        
        try:
            location = hotel.find_element(By.CSS_SELECTOR, 'span[data-testid="address"]').text
        except:
            location = np.nan
        
        try:
            link = hotel.find_element(By.CSS_SELECTOR, 'a[data-testid="title-link"]').get_attribute('href')
        except:
            link = np.nan
        
        try:
            distance_from_downtown = hotel.find_element(By.CSS_SELECTOR, 'span[data-testid="distance"]').text.replace(' km from center', '').strip()
            distance_from_downtown = float(distance_from_downtown)
        except:
            distance_from_downtown = np.nan
        
        try:
            price_text = hotel.find_element(By.CSS_SELECTOR, 'span[data-testid="price-and-discounted-price"]').text
            price = int(price_text.replace(',', '').replace('₹', '').strip())
        except:
            price = np.nan
        
        try:
            review_block = hotel.find_element(By.CSS_SELECTOR, 'div[data-testid="review-score"]')
            rating = float(review_block.find_element(By.CSS_SELECTOR, 'div[aria-hidden="true"]').text)
            
            score_text = review_block.find_element(By.CSS_SELECTOR, 'span.becbee2f63').text
            total_reviews = review_block.find_element(By.CSS_SELECTOR, 'span.eaa8455879').text
        except:
            rating = np.nan
            score_text = np.nan
            total_reviews = np.nan
        
        rows.append({
            'Hotel': hotel_name,
            'Locality': location,
            'Downtown(km)': distance_from_downtown,
            'Rating': rating,
            'Score Text': score_text,
            'Total Reviews': total_reviews,
            'Price(₹)': price,
            'Link': link
        })
    
    driver.quit()
    
    df = pd.DataFrame(rows)
    df.to_csv(f"{filename}.csv", index=False)
    print(f"✅ Data saved to {filename}.csv")
    print(df.head())

if __name__ == "__main__":
    url = input("Enter the Booking.com URL to scrape: ").strip()
    filename = input("Enter the filename to save (without extension): ").strip()
    
    scrape_hotels_selenium(url, filename)
