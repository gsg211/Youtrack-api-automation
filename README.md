### Description

This is the test task for the Jetbrains `YouTrack Integration with Microsoft Teams` internship project

The program has 2 functionalities:
1. Periodically retrieve a list of notifications and send them as messages in a messaging app
2. Create a command in that messaging app that creates new issues using the Youtrack api

---

### How to setup the project

1. Download the source code 
2. Install the required python packages
    ``pip install -r requirements.txt``
3. Create a slack app based on a slack workspace
   1. generate an app token with the `connections:write` permission
   2. generate a bot with the following scopes
      ```
      -chat:write
      -chat:write.public
      -commands
      -groups.read
      ```
   3. activate socket mode
   4. create the commands `/issues` and `/projects`
4. Create a .env file that contains:
```
YOUTRACK_URL = "<--- the youtrack url --->"
YOUTRACK_TOKEN = "<--- the youtrack permanent token --->"
SLACK_BOT_TOKEN = "<--- the token used by your slack bot --->"
SLACK_USER_ID = "<--- slack id where the program send notifications --->"
SLACK_APP_TOKEN = "<--- the token used by your slack app --->"
```
5. Run the program `python main.py`


### How to use
The program sends a get request to the youtrack url periodically. It checks SentNotifications.txt to determine if a new notification appeared. If there is a new notification it is sent to the user_id

The bot command "/projects" is used to see all projects

The bot command `"/issue {Summary} ; {Description} ; {Project id}"` creates a new issue 