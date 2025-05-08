import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException


def init_driver():
    service = Service('chromedriver.exe')
    options = Options()
    options.add_argument('--headless=new')
    return webdriver.Chrome(service=service, options=options)


def safe_find_text(element, by, value):
    try:
        return element.find_element(by, value).text
    except NoSuchElementException:
        return ''  # Return empty if not found


def scrape_indian_express(driver):
    driver.get('https://indianexpress.com/latest-news/?ref=latestnews')
    articles = driver.find_elements(By.CLASS_NAME, 'articles')
    data = []
    for article in articles:
        headline = safe_find_text(article, By.CLASS_NAME, 'title')
        summary = safe_find_text(article, By.TAG_NAME, 'p')
        data.append({'Source': 'The Indian Express', 'Headline': headline, 'Summary': summary})
    return pd.DataFrame(data)


def scrape_nbc(driver):
    driver.get('https://www.nbcnews.com/')
    headlines = driver.find_elements(By.CLASS_NAME, 'headline-large')
    summaries = driver.find_elements(By.CSS_SELECTOR, '.multi-story__dek.publico-txt.f3.lh-copy.fw4')
    data = []
    for headline, summary in zip(headlines, summaries):
        data.append({'Source': 'NBC', 'Headline': headline.text, 'Summary': summary.text})
    return pd.DataFrame(data)


def scrape_times_of_india(driver):
    driver.get('https://timesofindia.indiatimes.com/briefs')
    articles = driver.find_elements(By.CLASS_NAME, 'brief_box')
    data = []
    for article in articles:
        headline = safe_find_text(article, By.TAG_NAME, 'h2')
        summary = safe_find_text(article, By.TAG_NAME, 'p')
        data.append({'Source': 'Times of India', 'Headline': headline, 'Summary': summary})
    return pd.DataFrame(data)


def main():
    driver = init_driver()
    
    try:
        indian_express_df = scrape_indian_express(driver)
        nbc_df = scrape_nbc(driver)
        times_of_india_df = scrape_times_of_india(driver)

        aggregated_news = pd.concat([indian_express_df, nbc_df, times_of_india_df], ignore_index=True)
        aggregated_news.to_csv('aggregated_news.csv', index=False)
        print(aggregated_news.head())
        
    finally:
        driver.quit()  

if __name__ == '__main__':
    main()