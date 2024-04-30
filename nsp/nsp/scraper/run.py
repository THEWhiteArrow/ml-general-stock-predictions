import os
from nsp.scraper.utils import (
    check_playwright_installation,
    download_from_website_using_js,
    download_from_yahoo_api,
)


def run():

    JS_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "js",
    )

    NVIDIA_EVENTS_PRESENTATIONS_URL = (
        "https://investor.nvidia.com/events-and-presentations/events-and-presentations/default.aspx"
    )
    NVIDIA_EVENTS_CORPORATE_INVESTOR_URL = "https://www.nvidia.com/en-us/events/"

    check_playwright_installation()

    download_from_yahoo_api(
        stock_name="NVDA",
    )

    with open(
        os.path.join(
            JS_DIR,
            "events_presentation.js",
        ),
        "r",
    ) as file:
        js_code = file.read()
        download_from_website_using_js(
            url=NVIDIA_EVENTS_PRESENTATIONS_URL,
            js=js_code,
        )

    with open(
        os.path.join(
            JS_DIR,
            "events_corporate.js",
        ),
        "r",
    ) as file:
        js_code = file.read()
        download_from_website_using_js(
            url=NVIDIA_EVENTS_CORPORATE_INVESTOR_URL,
            js=js_code,
        )


run()
