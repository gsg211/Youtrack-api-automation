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
    issue = command.get("text", "")
    print(issue)
    respond("created new issue")

if __name__ == "__main__":
    # watcher_thread = threading.Thread(
    #     target=watch_youtrack,
    #     args=(YOUTRACK_URL, YOUTRACK_TOKEN, SLACK_BOT_TOKEN, SLACK_USER_ID),
    #     daemon=True
    # )
    #
    # watcher_thread.start()
    # handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    # handler.start()
    print("temp")
    post_issue(YOUTRACK_URL,YOUTRACK_TOKEN,"Hello world 4 ", "custom description")