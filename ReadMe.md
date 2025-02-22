# What is This?
This is a program that gets messages from YouTube or Twitch and reads them outloud... For FREE!
# How is this free?
I make a Request to Google Translate to speak the messages in english. (It gets a bit weird when talking in other languages so I recomend keeping it in english)
# How can I set it up?
1. Install Python [here](https://www.python.org/downloads/)
2. Open the CMD and navigate to the folder where the requirments.txt is.
3. Run this command
````python
pip install -r requirements.txt
````
4. Open the Main.py file in a text editor (Like notepad) and edit the variables to your liking.
5. Save the file.
6. Run it while streaming and enjoy!
# What do the variables do?
TTS_COMMAND - What should the user include at the begining of their message to use TTS
Example:
````python
TTS_COMMAND = "TTS: " # Users will have to put "TTS: " at the start of there message for TTS
````
TWITCH_CHANNEL - Twitch Channel to Read Messages from.
STREAMING_ON_TWITCH - If true read messages from twitch instead of youtube.
YOUTUBE_CHANNEL_ID - Your YouTube Channel ID (Find this by clicking your Youtube profile pic -> Settings -> Advanced Settings)
YOUTUBE_STREAM_URL - If your stream is unlisted put the stream URL here.
MESSAGE_RATE - How fast the program processes incoming Chat messages
MAX_QUEUE_LENGTH - ~1-10 is HIGHLY RECOMENDED
AnounceUser - Include usernames in TTS

# Credits
Some code was made by [dougdoug](https://github.com/DougDougGithub/TwitchPlays). I just added stuff too it.


# Support
Need help? Contact me at Richdorman2+support@gmail.com
