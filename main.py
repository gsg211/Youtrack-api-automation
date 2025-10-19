import gzip

import requests
import base64
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv


class Notification:
    def __init__(self, id, content):
        self.id = id
        self.content = content


def decode_notification(notification_text):
    decoded_data = gzip.decompress(base64.b64decode(notification_text))
    soup = BeautifulSoup(decoded_data, "html.parser")
    decoded_notification = ""
    for paragraph in soup.find_all("p"):
        line = paragraph.get_text(strip=True)
        decoded_notification += line + "\n"
    return decoded_notification


def load_sent_notifications():
    with open('SentNotifications.text', 'r') as file:
        id_list = file.readlines()
    return id_list


def write_sent_notification(notificationID):
    with open('SentNotifications.text', 'a') as file:
        file.writelines(notificationID + '\n')


def get_notifications(url, token):
    endpoint = f"{url}/api/users/me/notifications"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    params = {
        "fields": "content,id",
    }

    return requests.get(endpoint, headers=headers, params=params)

def handle_response(response):
    if response.status_code == 200:
        response_content = response.json()

        for notificationItem in response_content:
            notification_id = notificationItem.get("id")
            notification_content = decode_notification(notificationItem.get("content"))
            notification = Notification(notification_id, notification_content)

            if notification.id + "\n" not in notifications_list:
                notifications_list.append(notification.id)
                write_sent_notification(notification.id)
    else:
        print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":

    load_dotenv()
    YOUTRACK_URL = os.getenv("YOUTRACK_URL")
    TOKEN = os.getenv("TOKEN")
    notifications_list = load_sent_notifications()

    response = get_notifications(YOUTRACK_URL, TOKEN)
    handle_response(response)

    print(notifications_list)
