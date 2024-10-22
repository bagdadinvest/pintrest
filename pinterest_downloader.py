from playwright.sync_api import sync_playwright
import os
import time
import json

# Phase 1: Gather all the pin links from the main Pinterest page
def gather_pinterest_pin_links(link, cookies_path):
    print("Initializing Playwright for Phase 1...")
    pin_urls = []
    with sync_playwright() as p:
        # Launching browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # Loading cookies for authentication
        print("Loading cookies from JSON file...")
        try:
            with open(cookies_path, 'r') as cookies_file:
                cookies = json.load(cookies_file)
                # Ensure all cookies have valid sameSite attribute
                for cookie in cookies:
                    if 'sameSite' not in cookie or cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                        cookie['sameSite'] = 'None'
                context.add_cookies(cookies)
        except FileNotFoundError:
            print("Error: Cookies file not found. Ensure you have exported your session cookies to a JSON file.")
            return

        page = context.new_page()

        print("Navigating to Pinterest link...")
        # Navigate to the Pinterest page
        page.goto(link)
        time.sleep(5)  # Adding a delay to ensure all content is loaded

        print("Scrolling to load all pins...")
        # Scroll to load more pins, assuming Pinterest uses infinite scrolling
        previous_height = page.evaluate("document.body.scrollHeight")
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)  # Wait for more content to load
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height

        print("Scraping pins links...")
        # Collecting all the pins links using the correct data attribute selector
        pin_elements = page.query_selector_all("[data-test-pin-id]")
        if not pin_elements:
            print("No pins found on the page. Check the selector or the page structure.")
        else:
            print(f"Found {len(pin_elements)} pins on the page.")

        # Extracting URLs from pin IDs
        for pin in pin_elements:
            pin_id = pin.get_attribute("data-test-pin-id")
            if pin_id:
                pin_url = f"https://tr.pinterest.com/pin/{pin_id}/"
                pin_urls.append(pin_url)

        # Closing browser
        print("Phase 1 complete, closing browser...")
        browser.close()

    # Save the pin URLs for Phase 2
    if pin_urls:
        with open("pin_links.txt", "w") as file:
            for url in pin_urls:
                file.write(f"{url}\n")
        print("Pin URLs saved to pin_links.txt")
    else:
        print("No URLs found to save.")

# Phase 2: Visit each pin link and download the high-quality image
def download_high_quality_pinterest_media(cookies_path):
    print("Initializing Playwright for Phase 2...")
    with sync_playwright() as p:
        # Launching browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # Loading cookies for authentication
        print("Loading cookies from JSON file...")
        try:
            with open(cookies_path, 'r') as cookies_file:
                cookies = json.load(cookies_file)
                # Ensure all cookies have valid sameSite attribute
                for cookie in cookies:
                    if 'sameSite' not in cookie or cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                        cookie['sameSite'] = 'None'
                context.add_cookies(cookies)
        except FileNotFoundError:
            print("Error: Cookies file not found. Ensure you have exported your session cookies to a JSON file.")
            return

        page = context.new_page()

        # Ensuring directories for download
        download_directory = 'pinterest_downloads'
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)

        # Reading pin URLs from the saved file
        try:
            with open("pin_links.txt", "r") as file:
                pin_urls = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print("Error: pin_links.txt not found. Ensure Phase 1 ran successfully.")
            return

        # Iterating over all pin links and downloading highest quality images
        print("Starting download process...")
        for index, pin_url in enumerate(pin_urls):
            try:
                print(f"Accessing pin {index + 1}: {pin_url}")
                page.goto(pin_url)
                time.sleep(5)  # Adding delay to load the pin page

                # Locate and click the element to show the larger version of the image
                view_larger_button = page.query_selector('[data-test-id="media-viewer-button"]')
                if view_larger_button:
                    view_larger_button.click()
                    time.sleep(3)  # Wait for the larger image to load

                # Locate the best quality image using its class
                large_image_element = page.query_selector('[data-test-id="closeup-image-main"] img')
                if not large_image_element:
                    print(f"No high-quality image found for pin {index + 1}.")
                    continue

                media_url = large_image_element.get_attribute("src")
                print(f"Found high-quality media {index + 1}: {media_url}")

                if not media_url:
                    print(f"Skipping pin {index + 1}, no media URL found...")
                    continue

                # Downloading file
                file_type = "jpg" if "jpg" in media_url else "mp4"
                file_path = os.path.join(download_directory, f"media_{index + 1}.{file_type}")
                with open(file_path, "wb") as file:
                    response = page.request.get(media_url)
                    file.write(response.body())
                print(f"Downloaded {media_url} to {file_path}")
            except Exception as e:
                print(f"Error occurred during download for pin {index + 1}: {e}")

        # Closing browser
        print("Download complete, closing browser...")
        browser.close()

if __name__ == "__main__":
    pinterest_link = "https://tr.pinterest.com/doctorgorlanov/pins/"
    cookies_path = "pinterest_cookies.json"  # Path to the cookies JSON file
    print(f"Starting Phase 1: Gathering pin links from: {pinterest_link}")
    gather_pinterest_pin_links(pinterest_link, cookies_path)
    print("Starting Phase 2: Downloading high-quality media from gathered links")
    download_high_quality_pinterest_media(cookies_path)
    print("Script completed.")
