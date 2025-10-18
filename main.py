import gzip

import requests
import base64
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv


def decode_notification(notification):
    decoded_data = gzip.decompress(base64.b64decode(notification))
    soup = BeautifulSoup(decoded_data, "html.parser")
    decoded_notification = ""
    for paragraph in soup.find_all("p"):
        line = paragraph.get_text(strip=True)
        decoded_notification += line + "\n"
    return decoded_notification


if __name__=="__main__":
    load_dotenv()

    YOUTRACK_URL = os.getenv("YOUTRACK_URL")
    TOKEN = os.getenv("TOKEN")

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    }

    params = {
        "filter": "read==false",
        "fields": "content"
    }

    response = requests.get(YOUTRACK_URL, headers=headers, params=params)
    notifications_list=list()
    if response.status_code == 200:
        response_content=response.json()
        content=response_content[1].get("content")


        for notification in response_content:
            print(decode_notification(notification.get("content")))

    else:
        print(f"Error: {response.status_code} - {response.text}")