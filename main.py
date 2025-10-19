import gzip
import time

import requests
import base64
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class Notification:
    def __init__(self, id, content):
        self.id = id
        self.content = content

def send_slack_message(bot_token, user_id, message):
    slack_client=WebClient(token=bot_token)
    try:
        # Call the chat.postMessage method using the WebClient
        response = slack_client.chat_postMessage(
            channel=user_id,
            text=message
        )
        print(f"Message sent to {user_id}: {response['message']['text']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")


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
        id_list = [line.strip() for line in file.readlines()]
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

def handle_response(response,notifications_list, slack_bot_token, slack_user_id):
    if response.status_code == 200:
        response_content = response.json()

        for notificationItem in response_content:
            notification = Notification(notificationItem.get("id"), "/*******\\\n" + decode_notification(notificationItem.get("content")) + "\\*******/")

            if notification.id not in notifications_list:
                notifications_list.append(notification.id)
                write_sent_notification(notification.id)
                send_slack_message(slack_bot_token, slack_user_id, notification.content)
    else:
        print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":

    load_dotenv()


    YOUTRACK_URL = os.getenv("YOUTRACK_URL")
    YOUTRACK_TOKEN = os.getenv("YOUTRACK_TOKEN")
    SLACK_BOT_TOKEN=os.getenv("SLACK_BOT_TOKEN")
    SLACK_USER_ID = os.getenv("SLACK_USER_ID")

    while True:
        notifications_list = load_sent_notifications()
        response = get_notifications(YOUTRACK_URL, YOUTRACK_TOKEN)
        handle_response(response,notifications_list,SLACK_BOT_TOKEN,SLACK_USER_ID)
        time.sleep(1)
