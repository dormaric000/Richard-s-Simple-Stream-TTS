import requests
import soundfile as sf
import time
import Chat_Connection
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import io
import wave
import pyaudio

print("Starting...")


try:
    TTS_COMMAND = "*" # LOWERCASE ONLY! * = Every Message Will Be TTS'd
    TWITCH_CHANNEL = 'twitch_channel_username_here' # LOWERCASE ONLY! If streaming on youtube leave it as is.
    STREAMING_ON_TWITCH = False # True = Twitch, False = YouTube
    YOUTUBE_CHANNEL_ID = "channel_id" # Find this under Settings -> Advanced Settings -> Channel ID (NOT USER ID)
    YOUTUBE_STREAM_URL = "yt_url" # If your stream is unlisted put the stream URL here, otherwise leave it as is.
    MESSAGE_RATE = 0 # How fast the program processes incoming Chat messages. Lower = Faster, Higher = Slower, 0 = As fast as possible
    MAX_QUEUE_LENGTH = 1 # ~1-10 is HIGHLY RECOMENDED because if you have a high message rate the program won't crash.
    MAX_WORKERS = 100 # 100 Recomended
    AnounceUser = True # If true will anounce who sent the message.

    if STREAMING_ON_TWITCH:
        t = Chat_Connection.Twitch()
        t.twitch_connect(TWITCH_CHANNEL)
    else:
        t = Chat_Connection.YouTube()
        t.youtube_connect(YOUTUBE_CHANNEL_ID, YOUTUBE_STREAM_URL)

    def handle_message(message: dict) -> None:
        try:
            msg = message['message'].lower()
            username = message['username'].lower()

            print(f"{username} said '{msg}'")
            if TTS_COMMAND == "*":
                if AnounceUser:
                    to_speak = f"{username} said '{msg}'"
                else:
                    to_speak = msg
            else:
                if msg.startswith(TTS_COMMAND):
                    if AnounceUser:
                        to_speak = f"{username} said '{msg[len(TTS_COMMAND):]}'"
                    else:
                        to_speak = msg[len(TTS_COMMAND):]
                else:
                    return
            print(f"Received input: {to_speak}")

            def split_text(text: str, limit: int = 200) -> list:
                words = text.split()
                chunks = []
                current_chunk = []
                current_length = 0
                for word in words:
                    if len(word) > limit:
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                            current_chunk = []
                            current_length = 0
                        for i in range(0, len(word), limit):
                            word_chunk = word[i:i + limit]
                            chunks.append(word_chunk)
                        continue

                    if current_length + len(word) + 1 <= limit:
                        current_chunk.append(word)
                        current_length += len(word) + 1
                    else:
                        chunks.append(' '.join(current_chunk))
                        current_chunk = [word]
                        current_length = len(word)
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                return chunks

            if len(to_speak) > 200:
                print("WARNING: Character count is over 200 characters, splitting into multiple requests.")
                parts = split_text(to_speak)
                with open("output.wav", "wb") as outfile:
                    for i, part in enumerate(parts):
                        url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en-TR&client=tw-ob&q={part}"
                        response = requests.get(url)
                        if response.status_code == 200:
                            print(f"Successfully generated audio part {i+1}/{len(parts)}")
                            audio_data, samplerate = sf.read(io.BytesIO(response.content))
                            sf.write(outfile, audio_data, samplerate, format="WAV")
                        else:
                            print(f"Error: {response.status_code}")
                print("Combined audio saved as output.wav")
            else:
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en-TR&client=tw-ob&q={to_speak}"
                print("Character count is under 200 characters, no need to split into multiple requests.")
                response = requests.get(url)
                if response.status_code == 200:
                    print("Successfully generated the audio with Google Translate, now saving it as output.wav")
                    audio_data, samplerate = sf.read(io.BytesIO(response.content))
                    sf.write("output.wav", audio_data, samplerate)
                    print("Audio saved as output.wav")
                else:
                    print(f"Error: {response.status_code}")

            print("Playing audio...")
            wf = wave.open("output.wav", 'rb')
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(1024)
            while len(data) > 0:
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
            p.terminate()

        except Exception as e:
            print("Encountered exception: " + str(e))

    message_queue = []
    last_time = time.time()
    active_tasks = []

    while True:

        active_tasks = [t for t in active_tasks if not t.done()]

        new_messages = t.twitch_receive_messages();
        if new_messages:
            message_queue += new_messages;
            message_queue = message_queue[-MAX_QUEUE_LENGTH:]

        messages_to_handle = []
        if not message_queue:
            last_time = time.time()
        else:
            r = 1 if MESSAGE_RATE == 0 else (time.time() - last_time) / MESSAGE_RATE
            n = int(r * len(message_queue))
            if n > 0:
                messages_to_handle = message_queue[0:n]
                del message_queue[0:n]
                last_time = time.time()

        if not messages_to_handle:
            continue
        else:
            for message in messages_to_handle:
                if len(active_tasks) <= MAX_WORKERS:
                    thread_pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
                    active_tasks.append(thread_pool.submit(handle_message, message))
                else:
                    print(f'WARNING: active tasks ({len(active_tasks)}) exceeds number of workers ({MAX_WORKERS}). ({len(message_queue)} messages in the queue)')
except Exception as e:
    print("Encountered exception: " + str(e))
    input("Press enter to exit...")

