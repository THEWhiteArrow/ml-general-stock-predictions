import os
import requests
import datetime
from playwright.sync_api import sync_playwright

DATA_DIR = os.path.join(os.getcwd(), "data")


def check_playwright_installation():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://example.com")
            print("Playwright is installed correctly and can open a browser.")
            browser.close()
    except Exception as e:
        print(f"An error occurred while checking Playwright installation: {e}")


def download_from_website_using_js(url: str, js: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto(url)
        page.wait_for_load_state("domcontentloaded")

        with page.expect_download() as download_info:
            page.evaluate(js)

        download = download_info.value

        print(f"Downloaded file name: {download.suggested_filename}")

        download.save_as(
            os.path.join(
                DATA_DIR,
                download.suggested_filename,
            )
        )
        page.close()
        browser.close()


def download_from_yahoo_api(stock_name: str, file_name: str):
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_name}"

    response = requests.get(
        url=url,
        params={
            "period1": "0",
            "period2": int(datetime.datetime.now().timestamp()),
        },
        headers={
            "Accept": "text/csv",
            "User-Agent": "Mozilla/5.0",
        },
        timeout=5,
    )

    if response.status_code == 200:
        data = response.text

        with open(
            os.path.join(DATA_DIR, file_name),
            "w",
        ) as f:
            f.write(data)

        print(f"Downloaded yahoo finance history: {file_name}")

    else:
        raise Exception(
            f"An error occurred while downloading NVIDIA stocks history. Status code: {response.status_code}"
        )
