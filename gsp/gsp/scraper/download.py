import os
import requests
import datetime


def download_from_yahoo_api(stock_id: str, save_dir: str):
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_id}"
    file_name = f"{stock_id}.csv"

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
            os.path.join(save_dir, file_name),
            "w",
        ) as f:
            f.write(data)

        print(f"Downloaded yahoo finance history: {file_name}")

    else:
        raise Exception(
            f"An error occurred while downloading NVIDIA stocks history. Status code: {response.status_code}"
        )
