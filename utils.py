from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import Authorize

authResponse = Authorize('client_secret.json')
credentials = authResponse.credentials

# Building the youtube object:
youtube = build('youtube', 'v3', credentials=credentials)

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


def getChannelHandle(userId):
    """
    It takes a userId and returns the user's channel handle (unique identifier from the custom URL).

    userId: The user's YouTube channel ID
    return: User's Channel Handle or 'No custom URL'
    """
    try:
        channelDetails = youtube.channels().list(
            part="snippet",
            id=userId,
        )
        response = channelDetails.execute()
        customUrl = response['items'][0]['snippet'].get('customUrl', None)
        if customUrl:
            # Extract the unique identifier from the custom URL
            handle = customUrl.split('/')[-1]
        else:
            handle = 'No custom URL'
        return handle
    except HttpError as e:
        return f"An error occurred: {e}"
    except KeyError:
        return "No custom URL or channel does not exist"

