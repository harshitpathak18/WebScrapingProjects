import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys


def get_flipkart_data(search_item, driver_path='chromedriver.exe'):
    service = Service(driver_path)
    options = Options()
    # Uncomment below for headless mode
    # options.add_argument('--headless=new')
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(f'https://www.flipkart.com/search?q={search_item}&otracker=search&otracker1=search')

    time.sleep(2)  # Let the page load

    product_list = driver.find_elements(By.CSS_SELECTOR, '.cPHDOP.col-12-12')
    data = []
    for product in product_list:
        try:
            product_name = product.find_element(By.CLASS_NAME, 'KzDlHZ').text
            product_price = product.find_element(By.CSS_SELECTOR, '.Nx9bqj._4b5DiR').text
            data.append({
                "Product": product_name, 
                "FlipkartPrice": product_price,
            })
        except:
            continue

    driver.quit()
    df = pd.DataFrame(data)
    return df


def get_amazon_data(search_item, driver_path='chromedriver.exe'):
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

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://www.amazon.in')

    time.sleep(2)

    search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
    search_box.send_keys(search_item)
    search_box.send_keys(Keys.ENTER)

    time.sleep(2)

    product_list = driver.find_elements(By.CLASS_NAME, 'sg-col-inner')
    data = []
    for product in product_list:
        try:
            title_block = product.find_element(By.TAG_NAME, 'h2')
            product_name = title_block.text
            product_price = product.find_element(By.CLASS_NAME, 'a-price-whole').text

            # Optional: Normalize naming structure
            try:
                name_part = product_name.split(":")[0]
                item_name = " ".join(name_part.split(' ')[:-2])
                ram = " ".join(name_part.split(' ')[-2:])
                color = product_name.split(":")[1].split(';')[-1].strip()

                product_name = f"{item_name} ({color}, {ram})"
            except:
                pass

            data.append({
                "Product": product_name,
                "AmazonPrice": "₹" + product_price,
            })
        except:
            continue

    driver.quit()
    df = pd.DataFrame(data)
    return df


def merge_data(amazon_df, flipkart_df):
    # Normalize product names for matching (remove brand if needed)
    flipkart_df['Product'] = flipkart_df['Product'].str.replace('Apple ', '', regex=False)

    merged_df = pd.merge(amazon_df, flipkart_df, on='Product', how='inner')
    return merged_df


if __name__ == "__main__":
    search_term = "iphone 16"
    chromedriver_path = 'chromedriver.exe'

    print("Scraping Flipkart...")
    flipkart_df = get_flipkart_data(search_term, chromedriver_path)
    print(f"Flipkart products found: {len(flipkart_df)}")
    print('Flipkart DataFrame\n')
    print(flipkart_df.head())
    print('\n')

    print("Scraping Amazon...")
    amazon_df = get_amazon_data(search_term, chromedriver_path)
    print(f"Amazon products found: {len(amazon_df)}")
    print('Amazon DataFrame\n')
    print(amazon_df.head())
    print('\n')
          
    print("Merging data...")
    merged_df = merge_data(amazon_df, flipkart_df)

    print("Final merged data:")
    print(merged_df)

    # Optional: save to CSV
    merged_df.to_csv(f"{"_".join(search_term.split(' '))}_price_comparison.csv", index=False)
    print("Merged data saved to merged_prices.csv")
