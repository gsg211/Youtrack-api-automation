import requests

from helpers import *
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import threading

load_dotenv()

YOUTRACK_URL = os.getenv("YOUTRACK_URL")
YOUTRACK_TOKEN = os.getenv("YOUTRACK_TOKEN")
SLACK_BOT_TOKEN=os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN= os.getenv("SLACK_APP_TOKEN")
SLACK_USER_ID = os.getenv("SLACK_USER_ID")

app = App(token=SLACK_BOT_TOKEN)


@app.command("/issue")
def create_new_issue(ack, respond, command):
    ack()
    command_text= command.get("text", "").split(' ; ')
    print(command_text)
    issue_summary=command_text[0].strip()
    if not issue_summary:
        respond("New Issue must have a summary")

    issue_description = command_text[1].strip() if len(command_text) > 1 else None
    project_id = command_text[2].strip() if len(command_text) > 2 else None

    post_issue(YOUTRACK_URL,YOUTRACK_TOKEN,issue_summary,issue_description,project_id)
    respond("created new issue")


@app.command("/projects")
def create_new_issue(ack, respond, command):
    ack()
    response=get_all_project_ids(YOUTRACK_URL, YOUTRACK_TOKEN)
    respond(response.__repr__())

if __name__ == "__main__":
    # The app runs 2 threads
    #watcher_thread checks the notifications and sends them to the Slack user
    watcher_thread = threading.Thread(
        target=watch_youtrack,
        args=(YOUTRACK_URL, YOUTRACK_TOKEN, SLACK_BOT_TOKEN, SLACK_USER_ID),
        daemon=True
    )
    watcher_thread.start()

    # main thread runs the Slack app that creates new issues
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()