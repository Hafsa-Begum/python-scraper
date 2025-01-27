from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json



def scrape_youtube_videos(search_query):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--mute-audio")  # Mute audio

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open YouTube and search for the query
        driver.get("https://www.youtube.com")
        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys(search_query)
        search_box.submit()

        # Wait for results to load
        time.sleep(3)

        # Get video links
        videos = driver.find_elements(By.XPATH, '//*[@id="video-title"]')
        video_links = [video.get_attribute("href") for video in videos if video.get_attribute("href")]

        print(f"Found {len(video_links)} video links.")

        # Prepare to scrape video details
        video_data = []
        for index, link in enumerate(video_links, start=1):
            print(f"Processing video {index}/{len(video_links)}: {link}")
            driver.get(link)
            time.sleep(3)  # Wait for the video page to load

            if "/shorts/" in link:  # Handle Shorts videos
                try:
                    title = get_shorts_title(link, driver)
                except Exception as e:
                    title = "N/A"
                    print(f"Could not find title for {link}: {e}")

                try:
                    channel = driver.find_element(By.CLASS_NAME, "yt-core-attributed-string--white-space-pre-wrap").text
                except Exception as e:
                    channel = "N/A"
                    print(f"Could not find likes for Shorts video {link}: {e}")

                video_data.append({
                    "no": index,
                    "type": "Shorts",
                    "channel": channel,
                    "title": title,
                    "link": link
                })

            else:  # Handle regular videos
                try:
                    title = driver.find_element(By.CSS_SELECTOR, "h1.style-scope.ytd-watch-metadata").text
                except Exception as e:
                    title = "N/A"
                    print(f"Could not find title for {link}: {e}")

                try:
                    views = driver.find_element(By.CSS_SELECTOR, "span.bold.style-scope.yt-formatted-string").text
                except Exception as e:
                    views = "N/A"
                    print(f"Could not find views for {link}: {e}")

                try:
                    channel = driver.find_element(By.CSS_SELECTOR, "yt-formatted-string#text.style-scope.ytd-channel-name.complex-string").text
                except Exception as e:
                    channel = "N/A"
                    print(f"Could not find channel for {link}: {e}")

                video_data.append({
                    "no": index,
                    "type": "Regular",
                    "title": title,
                    "views": views,
                    "channel": channel,
                    "link": link
                })

        # Save the data to a JSON file
        output_file = f"youtube_video_data_{search_query.replace(' ', '_')}.json"
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(video_data, file, ensure_ascii=False, indent=4)

        print(f"Video data saved to {output_file}")

    finally:
        # Close the driver
        driver.quit()

def get_shorts_title(shorts_url, driver):
    try:
        driver.get(shorts_url)

        # Scroll to ensure dynamic content loads
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the title element to be visible
        title_element = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "h2 span.yt-core-attributed-string")
            )
        )
        return title_element.text
    except Exception as e:
        print(f"Could not find title for {shorts_url}: {e}")
        return None

if __name__ == "__main__":
    search_query = input("Enter the search query: ")
    scrape_youtube_videos(search_query)
