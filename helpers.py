import gzip

import time

import requests
import base64
from bs4 import BeautifulSoup

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ----------------------------------------------------
# This file contains all functions used to run the app
# ----------------------------------------------------

class Notification:
    def __init__(self, notification_id, content):
        self.id = notification_id
        self.content = content

# used to send the notification to the user
def send_slack_message(bot_token, user_id, message):
    slack_client=WebClient(token=bot_token)
    try:
        response = slack_client.chat_postMessage(
            channel=user_id,
            text=message
        )
        print(f"Message sent to {user_id}: {response['message']['text']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# decodes notification using gzip and removes the paragraph tags
def decode_notification(notification_text):
    #decode
    decoded_data = gzip.decompress(base64.b64decode(notification_text))
    soup = BeautifulSoup(decoded_data, "html.parser")
    decoded_notification = ""
    #remove paragraphs
    for paragraph in soup.find_all("p"):
        line = paragraph.get_text(strip=True)
        decoded_notification += line + "\n"
    return decoded_notification

# SentNotifications.text contains all previously sent notifications
def load_sent_notifications():
    with open('SentNotifications.text', 'r') as file:
        id_list = [line.strip() for line in file.readlines()]
    return id_list

# appends a new id if a new notifications is sent
def write_sent_notification(notification_id):
    with open('SentNotifications.text', 'a') as file:
        file.writelines(notification_id + '\n')

# get request to the youtrack rest api
def get_notifications(url, token):
    endpoint = f"{url}/api/users/me/notifications"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    params = {
        "fields": "content,id",
        "$top": "200"
    }

    return requests.get(endpoint, headers=headers, params=params)

# checks to see if a new notification appeared then sends it
def handle_response(response,notifications_list, slack_bot_token, slack_user_id):
    if response.status_code == 200:
        response_content = response.json()

        # the response contains all notifications
        for notificationItem in response_content:

            notification = Notification(
                notificationItem.get("id"),
                "/*******\\\n" + decode_notification(notificationItem.get("content")) + "\\*******/"
            )
            if notification.id not in notifications_list:
                notifications_list.append(notification.id)
                write_sent_notification(notification.id)

                send_slack_message(slack_bot_token, slack_user_id, notification.content)
    else:
        print(f"Error: {response.status_code} - {response.text}")

# the loop
def check_notifications(youtrack_url, youtrack_token, slack_bot_token, slack_user_id, delay):
    print(f"\nStarted checking notifications with delay of {delay}\n")
    while True:
        try:
            notifications_list = load_sent_notifications()
            response = get_notifications(youtrack_url, youtrack_token)
            handle_response(response, notifications_list, slack_bot_token, slack_user_id)
            time.sleep(delay)
        except Exception as e:
            print(e)

# post reques to create a new issue. The description and project id are optional
# used by the /issue slack command
def post_issue(youtrack_url, youtrack_token, issue_summary,issue_description="automated issue created by slack", project_id="0-0"):
    endpoint=f"{youtrack_url}/api/issues"

    if not issue_description :
        print(issue_description)
        issue_description = "automated issue created by slack"

    if not project_id:
        project_id="0-0"

    headers={
        "Authorization" : f"Bearer {youtrack_token}",
        "Accept" : "application/json",
        "Content-Type" : "application/json"
    }

    body = {
        "project": {"id": project_id},
        "summary": issue_summary,
        "description" : issue_description
    }
    response= requests.post(endpoint,headers=headers, json=body)
    print(response.json())

# get request to get all projects from youtrack. Used by the /projects slack command
def get_all_project_ids(youtrack_url, youtrack_token):
    endpoint=f"{youtrack_url}/api/admin/projects?"
    headers={
        "Authorization" : f"Bearer {youtrack_token}",
        "Accept" : "application/json",
    }

    params = {
        "fields" : "id,name,shortName"
    }
    response= requests.get(endpoint,headers=headers, params=params)
    return response.json()

def set_delay():
    delay = input("\nInput the time delay between requests\n{press ENTER for the default value 500}\nDelay : ")
    if not delay:
        print("default value selected => 500")
        return 500
    else:
        try:
            delay = int(delay)
            print(f"delay value => {delay}")
            return delay
        except ValueError:
            print("Delay must be a number, using default value => 500")
            return 500
    return 500
