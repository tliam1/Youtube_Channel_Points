import time
from datetime import datetime, timezone
import random
import threading
# from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import db
import utils
# from auth import Authorize
from utils import youtube
import rewards

# Settings
_delay = 5


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
    reply.execute()
    print("Message sent!")


def getAllChatters(userIds):
    """
    It takes a set of user IDs and returns the usernames.

    userIds: A set of unique user IDs
    return: A list of usernames
    """
    usernames = [utils.getUserName(userId) for userId in userIds]
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

    # bot_start_time = datetime.now(timezone.utc)
    skipFirstBatch = True  # just to ignore the first flow of messages if you started bot mid stream

    if not liveChatId:
        print("Invalid live stream ID or no active live chat found.")
        return

    messagesList = []  # List of messages
    userIds = set()  # Set of unique user IDs
    processedMessageIds = set()  # Set of unique message IDs to track processed messages
    lock = threading.Lock()
    flag = [False]  # A list containing a single boolean element

    # Start the timer function in a separate thread
    timer_thread = threading.Thread(target=timer_function, args=(flag, lock))
    timer_thread.daemon = True  # Set as a daemon thread to run in the background
    timer_thread.start()
    while True:
        # bot replies to every message within past 1 second (can be changed to add delay):
        time.sleep(_delay)

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
            messageId = messages['id']
            userId = messages['snippet']['authorChannelId']
            message = messages['snippet']['textMessageDetails']['messageText']
            # message_time = datetime.strptime(messages['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            if messageId not in processedMessageIds: # and message_time > bot_start_time
                notReadMessages.append((userId, message, messageId))

        for message in notReadMessages:
            userId = message[0]
            userIds.add(userId)
            messageId = message[2]
            processedMessageIds.add(messageId)
            message = message[1]
            splitMsg = str(message).split()

            if skipFirstBatch:
                continue

            if str(message).lower() == "!p":
                print("REQUESTED TO CHECK POINTS")
                db.CheckPermissions(userId)
                userName = utils.getUserName(userId)
                points = db.checkGrubPoints(userId)
                sendReplyToLiveChat(
                    liveChatId,
                    userName + ", you have " + str(points) + " points.")

            if len(splitMsg) > 1 and splitMsg[0] == "!g":
                db.CheckPermissions(userId)
                userName = utils.getUserName(userId)
                if splitMsg[1].isdigit() or splitMsg[1].lower() == "all":
                    amount = int(splitMsg[1]) if splitMsg[1].isdigit() else db.checkGrubPoints(userId)
                    if db.checkGrubPoints(userId) < amount:
                        response = f"{userName} Does not have enough points to gamble {amount}!"
                        pass
                    else:
                        roll = random.randrange(1, 100)
                        if 75 <= roll < 99:
                            reward = amount
                            db.addGambleResults(userId, reward)
                            response = f"{userName} rolled {roll} and won " + str(amount * 2)
                            # print("user attempted to gamble value: " + str(amount) + " and won " + str(reward))
                        elif roll >= 99:
                            reward = amount * 9
                            db.addGambleResults(userId, reward)
                            response = f"{userName} rolled {roll} and won " + str(amount * 10)
                            # print("user attempted to gamble value: " + str(amount) + " and won " + str(reward))
                        else:
                            reward = -amount
                            db.addGambleResults(userId, reward)
                            response = f"{userName} rolled {roll} and lost " + str(reward * -1)
                            # print("user attempted to gamble value: " + str(amount) + " and lost " + str(reward))
                    sendReplyToLiveChat(
                        liveChatId,
                        response)
                else:
                    print("user failed to gamble due to errors")

            if len(splitMsg) > 2 and splitMsg[0] == "!d":
                db.CheckPermissions(userId)
                userName = utils.getUserName(userId)
                # donorUserName = utils.getUserName(userId)
                # print(db.CheckIfHandleExists(splitMsg[1]))
                # print(splitMsg[2].isdigit())
                # print(splitMsg[2])
                # print(splitMsg[1])
                # print(userId)
                # print(db.CheckHandle(userId))
                if db.CheckIfHandleExists(splitMsg[1]) and splitMsg[2].isdigit():
                    amount = int(splitMsg[2])
                    if db.checkGrubPoints(userId) < amount:
                        response = f"{userName} Does not have enough points to donate {splitMsg[2]}!"
                        sendReplyToLiveChat(
                            liveChatId,
                            f"{response}")
                        pass
                    elif db.CheckHandle(userId) == splitMsg[1].strip():
                        response = f"{userName} cannot donate points to themselves!"
                        sendReplyToLiveChat(
                            liveChatId,
                            f"{response}")
                        pass
                    else:
                        db.donatePoints(userId, splitMsg[1], amount)
                        sendReplyToLiveChat(
                            liveChatId,
                            f"@{userName} donated {splitMsg[2]} points to {splitMsg[1]}!")
                        pass
                else:
                    sendReplyToLiveChat(
                        liveChatId,
                        "Invalid acceptor handle or given value is not a digit. Go to the channel and check their @name (you need the @ sign) and try again")

            if splitMsg[0] == "!r":
                userName = utils.getUserName(userId)
                if len(splitMsg) == 1:
                    response = rewards.rewards_to_string()
                    sendReplyToLiveChat(
                        liveChatId,
                        f'\"{response}\"')
                elif rewards.is_valid_reward(splitMsg[1]) and db.checkGrubPoints(userId) >= int(rewards.rewards[splitMsg[1]]["price"]):
                    description = rewards.rewards[splitMsg[1]]["description"]
                    cost = int(rewards.rewards[splitMsg[1]]["price"])
                    db.RedeemReward(userId=userId, cost=cost)
                    response = f"{userName} has redeemed {splitMsg[1]}: {description}"
                    sendReplyToLiveChat(
                        liveChatId,
                        f"{response}")
                elif rewards.is_valid_reward(splitMsg[1]) and db.checkGrubPoints(userId) < int(rewards.rewards[splitMsg[1]]["price"]):
                    response = f"{userName} doesn't have enough grub points to redeem {splitMsg[1]}!"
                    sendReplyToLiveChat(
                        liveChatId,
                        f"{response}")
                else:
                    sendReplyToLiveChat(
                        liveChatId,
                        f"{userName}: Error retrieving reward {splitMsg[1]}. Make sure this reward exists by typing the command \"!r\"")
                    # print a description of all redeems
                    pass

            # if (message == "!discord" or message == "!disc"):
            #     discord_link = "https://discord.gg/"
            #     sendReplyToLiveChat(
            #         liveChatId,
            #         f'Join our discord! {discord_link}')

        # Check the flag to see if the 5 minutes have elapsed
        with lock:
            if flag[0]:
                # 5 minutes have elapsed, process the chatters, reward points
                # print("ADDED 5 min grub points TO: ")
                db.addGrubPoints(userIds)
                flag[0] = False
                # for userId in userIds:
                #     print(getUserName(userId))
                userIds = set()

        skipFirstBatch = False # back to processing all messages


if __name__ == "__main__":
    main()
