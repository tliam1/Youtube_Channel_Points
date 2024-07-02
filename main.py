import json
import time
import random
import threading
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import db
from auth import Authorize

authResponse = Authorize('client_secret.json')
credentials = authResponse.credentials

# Building the youtube object:
youtube = build('youtube', 'v3', credentials=credentials)

# Settings
_delay = 1


def getLiveChatId(LIVE_STREAM_ID):
    """
    It takes a live stream ID as input, and returns the live chat ID associated with that live stream

    LIVE_STREAM_ID: The ID of the live stream
    return: The live chat ID of the live stream.
    """
    try:
        stream = youtube.videos().list(
            part="liveStreamingDetails",
            id=LIVE_STREAM_ID,  # Live stream ID
        )
        response = stream.execute()
        if 'items' in response and response['items']:
            liveChatId = response['items'][0]['liveStreamingDetails']['activeLiveChatId']
            print("\nLive Chat ID: ", liveChatId)
            return liveChatId
        else:
            print("No live stream details found for the given ID.")
            return None
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None


# Access user's channel Name:
def getUserName(userId):
    """
    It takes a userId and returns the userName.

    userId: The user's YouTube channel ID
    return: User's Channel Name
    """
    channelDetails = youtube.channels().list(
        part="snippet",
        id=userId,
    )
    response = channelDetails.execute()
    # print(json.dumps(response, indent=2))
    userName = response['items'][0]['snippet']['title']
    return userName


# print(getUserName("UC0YXSy_J8uTDEr7YX_-d-sg"))


def sendReplyToLiveChat(liveChatId, message):
    """
    It takes a liveChatId and a message, and sends the message to the live chat.

    liveChatId: The ID of the live chat to which the message should be sent
    message: The message you want to send to the chat
    """
    reply = youtube.liveChatMessages().insert(
        part="snippet",
        body={
            "snippet": {
                "liveChatId": liveChatId,
                "type": "textMessageEvent",
                "textMessageDetails": {
                    "messageText": message,
                }
            }
        }
    )
    response = reply.execute()
    print("Message sent!")


def getAllChatters(userIds):
    """
    It takes a set of user IDs and returns the usernames.

    userIds: A set of unique user IDs
    return: A list of usernames
    """
    usernames = [getUserName(userId) for userId in userIds]
    return usernames


def timer_function(flag, lock):
    while True:
        time.sleep(300)  # Wait for 5 minutes
        with lock:
            flag[0] = True


def main():
    # db.connectDB() remember we need to close this too
    LIVE_STREAM_ID = input("Enter the live stream ID: ")
    liveChatId = getLiveChatId(LIVE_STREAM_ID)
    if not liveChatId:
        print("Invalid live stream ID or no active live chat found.")
        return

    messagesList = []  # List of messages
    userIds = set()  # Set of unique user IDs
    lock = threading.Lock()
    flag = [False]  # A list containing a single boolean element

    # Start the timer function in a separate thread
    timer_thread = threading.Thread(target=timer_function, args=(flag, lock))
    timer_thread.daemon = True  # Set as a daemon thread to run in the background
    timer_thread.start()

    while True:
        # bot replies to every message within past 1 second (can be changed to add delay):
        time.sleep(1)

        notReadMessages = []  # List of messages not yet read by bot
        # Fetching the messages from the live chat:
        liveChat = youtube.liveChatMessages().list(
            liveChatId=liveChatId,
            part="snippet"
        )
        response = liveChat.execute()
        # print("\nMessages Fetched:  ", json.dumps(response, indent=2))
        allMessages = response['items']

        # Check if there are any new messages and add them messagesList/notReadMessages list:
        # if len(messagesList) >= 0:
        #     for messages in allMessages:
        #         userId = messages['snippet']['authorChannelId']
        #         message = messages['snippet']['textMessageDetails']['messageText']
        #         messagesList.append((userId, message))
        #         userIds.add(userId)
        # else:
        for messages in allMessages:
            userId = messages['snippet']['authorChannelId']
            message = messages['snippet']['textMessageDetails']['messageText']
            if (userId, message) not in messagesList:
                notReadMessages.append((userId, message))
            if (userId, message) not in messagesList:
                messagesList.append((userId, message))

        for message in notReadMessages:
            userId = message[0]
            userIds.add(userId)
            message = message[1]
            # print(userId)
            userName = getUserName(userId)
            # print(f'\nUsername: {userName}')

            # if (message == "Hello" or message == "hello" or message == "Hi" or message == "hi"):
            #     sendReplyToLiveChat(
            #         liveChatId,
            #         "Hey " + userName + "! Welcome to the stream!")
            #
            # if (message == "!discord" or message == "!disc"):
            #     discord_link = "https://discord.gg/"
            #     sendReplyToLiveChat(
            #         liveChatId,
            #         f'Join our discord! {discord_link}')
            #
            # if (message == "!random" or message == "!rand"):
            #     dad_jokes = [
            #         "Why do fathers take an extra pair of socks when they go golfing? In case they get a hole in one!",
            #         "Dear Math, grow up and solve your own problems.",
            #         "What has more letters than the alphabet? The post office!",
            #         "Why are elevator jokes so classic and good? They work on so many levels!",
            #         "What do you call a fake noodle? An impasta!",
            #         "What do you call a belt made out of watches? A waist of time!",
            #         "Why did the scarecrow win an award? Because he was outstanding in his field!",
            #         "Why don't skeletons ever go trick or treating? Because they have no body to go with!",
            #         "What's brown and sticky? A stick!"]
            #     joke = random.choice(dad_jokes)
            #     sendReplyToLiveChat(liveChatId, joke)
        # Check the flag to see if the 5 minutes have elapsed
        with lock:
            if flag[0]:
                # 5 minutes have elapsed, process the chatters, reward points
                print("ADDED 5 min grub points TO: ")
                db.addGrubPoints(userIds)
                flag[0] = False
                # for userId in userIds:
                #     print(getUserName(userId))
                userIds = set()


if __name__ == "__main__":
    main()
