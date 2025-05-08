import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Setup WebDriver
def setup_driver():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36",
    ]
    chosen_agent = random.choice(user_agents)

    options = Options()
    options.add_argument(f"user-agent={chosen_agent}")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# Scrape Trending Videos
def scrape_videos(driver, url):
    print("Opening YouTube Trending page...")
    driver.get(url)
    videos = driver.find_elements(By.ID, 'dismissible')
    print(f"Found {len(videos)} videos.")

    data = []
    for idx, video in enumerate(videos):
        try:
            meta = video.find_element(By.ID, 'meta')
            title = meta.find_element(By.ID, 'video-title').text
            channel = meta.find_element(By.ID, 'metadata').find_element(By.ID, 'channel-name').text

            meta_data = meta.find_elements(By.CSS_SELECTOR, '.inline-metadata-item.style-scope.ytd-video-meta-block')
            views = meta_data[0].text if len(meta_data) > 0 else 'N/A'
            uploaded = meta_data[1].text if len(meta_data) > 1 else 'N/A'

            description_elem = video.find_elements(By.ID, 'description-text')
            description = description_elem[0].text if description_elem else 'N/A'

            link = video.find_element(By.ID, 'thumbnail').get_attribute('href')

            data.append({
                "Title": title,
                "Channel": channel,
                "Views": views,
                "Uploaded": uploaded,
                "Description": description,
                "Link": link
            })

            print(f"[{idx + 1}/{len(videos)}] Collected: {title}")

        except Exception as e:
            print(f"⚠️ Skipping video {idx + 1} due to error: {e}")
            continue

    return data


# Save DataFrame to CSV
def save_to_csv(data, filename):
    df = pd.DataFrame(data).drop_duplicates()
    df.index = range(len(df))
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(df)} unique videos to '{filename}'.")


# Main Runner
def main():
    driver = setup_driver()
    try:
        trending_data = scrape_videos(driver, 'https://www.youtube.com/feed/trending?bp=6gQJRkVleHBsb3Jl')
        save_to_csv(trending_data, 'trending_on_youtube.csv')
    finally:
        time.sleep(2)
        driver.close()
        print("Browser closed.")


# Entry Point
if __name__ == "__main__":
    main()
