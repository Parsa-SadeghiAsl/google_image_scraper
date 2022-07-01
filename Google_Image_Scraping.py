import os
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
from PIL import Image
import time


# Locate your chromedriver executable path here
PATH = "/usr/bin/chromedriver"


# Get the url of the image
def fetch_image_urls(item_name, max_links, wd, delay):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)
    
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    wd.get(search_url.format(q=item_name))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links:
        scroll_to_end(wd)

        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
        number_results = len(thumbnail_results)
        print(f'Found: {number_results} search results. Extracting links from {results_start}:{number_results}')

        for img in thumbnail_results[results_start:number_results]:
            try:
                img.click()
                time.sleep(delay)
            except Exception:
                continue

            actual_images = wd.find_elements(By.CSS_SELECTOR, 'img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))
            
            image_count = len(image_urls)
            if len(image_urls) >= max_links:
                print(f'Found: {len(image_urls)} image links, done!')
                wd.quit()
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            # load_more_button = wd.find_element(By.CSS_SELECTOR, ".mye4qd")
            # if load_more_button:
            #     wd.execute_script("arguments[0].click();", load_more_button)

        results_start = len(thumbnail_results)

    return image_urls


# Download the images
def download_image(download_path, url):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f'Erorr - cannot download {url} - {e}')

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(download_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f'SUCCESS - saved {url} - as {file_path}')
    except Exception as e:
        print(f'Error - cannot save {url} - {e}')


# Combine the two functions
def search_and_download(item_name, PATH, download_path, number_images):
    target_folder = os.path.join(download_path, '_'.join(item_name.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=PATH) as wd:
        res = fetch_image_urls(item_name, number_images, wd, 2)

    for url in res:
        download_image(target_folder, url)



item_name = 'kendrick lamar'
search_and_download(item_name, PATH, 'images', 80)