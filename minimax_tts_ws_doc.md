Text to Speech（T2A）
Introduction
This API supports synchronous text-to-speech audio generation, with a maximum of 5000 characters of input. As this API is a stateless interface, the model will not receive any information other than what is directly passed through as input. This would not include information such as domain logic, nor will the model store any incoming data.
The interface supports the following features:
1.
100+ existing voices to choose
2.
Adjustable volume, tone, speed, and output format for every voice
3.
Weighted voice mixing: create a unique new voice from existing voices
4.
Detailed manual control of pauses and lulls in speech
5.
Multiple audio specifications and formats
6.
Real-time streaming
This API could be potentially used for phrase generation, voice chat, online social networking sites, etc.
MiniMax MCP
github: https://github.com/MiniMax-AI/MiniMax-MCP
HTTP API
API: https://api.minimax.io/v1/t2a_v2
Models
The following models support 24 languages as follows:
English (US, UK, Australia, India)
Chinese (Mandarin and Cantonese)
Japanese, Korean, French, German, Spanish, Portuguese (Brazilian), Italian, Arabic, Russian, Turkish, Dutch, Ukrainian, Vietnamese, and Indonesian, Thai, Polish, Romanian, Greek, Czech, Finnish, Hindi.
Model
Description
speech-02-hd
The brand new HD model boasts superior rhythm and stability, with outstanding performance in replication similarity and sound quality.
speech-02-turbo
The brand new Turbo model boasts superior rhythm and stability, with enhanced multilingual capabilities and excellent performance.
speech-01-hd
Rich Voices, Expressive Emotions, Authentic Languages
speech-01-turbo
Excellent performance and low latency
Interface Parameters
Request
AuthorizationstringRequired
API key
Content-Typeapplication/jsonRequired
Content-Type
GroupidRequired
The group to which the user belongs. Use the pre-generated value. The value should be spliced at the end of the url that calls the API.
modelstringRequired
Desired model. Includes:speech-02-hd, speech-01-turbo, speech-01-hd, speech-01-turbo
textstringRequired
Text to be synthesized. Character limit < 5000 chars. Paragraph markers will be replaced by line breaks. (To manually add a pause, insert the phrase <#x#> where x refers to the number of seconds to pause. Supports 0.01-99.99, with an accuracy of at most 2 decimal places).
voice_setting
Hide Properties
speedrange: [0.5,2] default: 1.0
The speed of the generated speech. Larger values indicate faster speech.
volrange: (0,10] default: 1.0
The volume of the generated speech. Larger values indicate larger volumes.
pitchrange: [-12,12] default: 0
The pitch of the generated speech. A value of 0 corresponds to default voice output.
voice_idstring
Desired voice. Both system voice ids and cloned voice ids are supported. System voice ids are listed below:
Wise_Woman
Friendly_Person
Inspirational_girl
Deep_Voice_Man
Calm_Woman
Casual_Guy
Lively_Girl
Patient_Man
Young_Knight
Determined_Man
Lovely_Girl
Decent_Boy
Imposing_Manner
Elegant_Man
Abbess
Sweet_Girl_2
Exuberant_Girl

Use the
get voice API to retrieve more system voices.
emotionstring
The emotion of the generated speech;
Currently supports seven emotions；
range:["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"]
english_normalizationbool
This parameter supports English text normalization, which improves performance in number-reading scenarios, but this comes at the cost of a slight increase in latency. If not provided, the default value is false.
audio_setting
Hide Properties
sample_raterange: [8000,16000,22050,24000,32000,44100] default: 32000
Sample rate of generated sound. Optional.
bitraterange: [32000,64000,128000,256000] default: 128000
Bitrate of generated sound. Optional

formatstring range: [mp3,pcm,flac] default: mp3
Format of generated sound. Optional

channelrange: [1, 2] default: 1
The number of channels of the generated audio.
1: mono
2: stereo
pronunciation_dict
Show Properties
timber_weightsrequired: either voice_id or timber_weightsRequired
Show Properties
streamboolean
Boolean value indicating whether the generated audio will be a stream. Defaults to non-streaming output.
language_booststring
Enhance the ability to recognize specified languages and dialects.
Supported values include:
'Chinese', 'Chinese,Yue', 'English', 'Arabic', 'Russian', 'Spanish', 'French', 'Portuguese', 'German', 'Turkish', 'Dutch', 'Ukrainian', 'Vietnamese', 'Indonesian', 'Japanese', 'Italian', 'Korean', 'Thai', 'Polish', 'Romanian', 'Greek', 'Czech', 'Finnish', 'Hindi', 'auto'
subtitle_enablebool
The parameter controls whether the subtitle service is enabled. If this parameter is not provided, the default value is false. This parameter only takes effect when the output is non-streaming.
output_formatstring
This parameter controls the format of the output content. The optional values are urlandhex. The default value is hex. This parameter is only effective in non-streaming scenarios. In streaming scenarios, only the "hex" format is supported for return.
Response
dataobject
Data may be returned as null. When referring to sample code, please refer primarily to non-null responses
Show Properties
trace_idstring
The id of the current conversation. Will be used in order to locate issues during inquiries and feedback
subtitle_filestring
The download link for the synthesized subtitles. Subtitles corresponding to the audio file, accurate to the sentence, in milliseconds, and in JSON format.
extra_infoobject
extra info
Show Properties
base_respobject
Error codes, status messages, and corresponding details, should the request run into any problems.
Show Properties
Request Success (Non-streaming)
Request Success (stream)
T2A v2
Copy
curl --location 'https://api.minimax.io/v1/t2a_v2?GroupId=${group_id}' \
--header 'Authorization: Bearer ${api_key}' \
--header 'Content-Type: application/json' \
--data '{
    "model":"speech-02-hd",
    "text":"The real danger is not that computers start thinking like people, but that people start thinking like computers. Computers can only help us with simple tasks.",
    "stream":false,
    "voice_setting":{
        "voice_id":"Grinch",
        "speed":1,
        "vol":1,
        "pitch":0
    },
    "audio_setting":{
        "sample_rate":32000,
        "bitrate":128000,
        "format":"mp3",
        "channel":1
    }
  }'
Request Success (Non-streaming)
Request Success (stream)
Response
Copy
{
    "data":{
        "audio":"hex audio",
        "status":2,
        "subtitle_file":"https://minimax-algeng-chat-tts.oss-cn-wulanchabu.aliyuncs.com/XXXX",
    },     
     "extra_info":{
        "audio_length":5746,
        "audio_sample_rate":32000,
        "audio_size":100845,
        "audio_bitrate":128000,
        "word_count":300,
        "invisible_character_ratio":0,
        "audio_format":"mp3",
        "usage_characters":630
    },
    "trace_id":"01b8bf9bb7433cc75c18eee6cfa8fe21",
    "base_resp":{
        "status_code":0,
        "status_msg":""
    }
}
Complete Streaming Sample
This is an example of an API call that creates an audio stream. The full audio file will be saved at the end of the call.
complete example
Copy
# This Python file uses the following encoding: utf-8

import json
import subprocess
import time
from typing import Iterator

import requests

group_id = ''    #your_group_id
api_key = ''    #your_api_key

file_format = 'mp3'  # support mp3/pcm/flac

url = "https://api.minimax.io/v1/t2a_v2?GroupId=" + group_id
headers = {"Content-Type":"application/json", "Authorization":"Bearer " + api_key}


def build_tts_stream_headers() -> dict:
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'authorization': "Bearer " + api_key,
    }
    return headers


def build_tts_stream_body(text: str) -> dict:
    body = json.dumps({
        "model":"speech-02-turbo",
        "text":"The real danger is not that computers start thinking like people, but that people start thinking like computers. Computers can only help us with simple tasks.",
        "stream":True,
        "voice_setting":{
            "voice_id":"male-qn-qingse",
            "speed":1.0,
            "vol":1.0,
            "pitch":0
        },
        "audio_setting":{
            "sample_rate":32000,
            "bitrate":128000,
            "format":"mp3",
            "channel":1
        }
    })
    return body


mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
mpv_process = subprocess.Popen(
    mpv_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)


def call_tts_stream(text: str) -> Iterator[bytes]:
    tts_url = url
    tts_headers = build_tts_stream_headers()
    tts_body = build_tts_stream_body(text)

    response = requests.request("POST", tts_url, stream=True, headers=tts_headers, data=tts_body)
    for chunk in (response.raw):
        if chunk:
            if chunk[:5] == b'data:':
                data = json.loads(chunk[5:])
                if "data" in data and "extra_info" not in data:
                    if "audio" in data["data"]:
                        audio = data["data"]['audio']
                        yield audio


def audio_play(audio_stream: Iterator[bytes]) -> bytes:
    audio = b""
    for chunk in audio_stream:
        if chunk is not None and chunk != '\n':
            decoded_hex = bytes.fromhex(chunk)
            mpv_process.stdin.write(decoded_hex)  # type: ignore
            mpv_process.stdin.flush()
            audio += decoded_hex

    return audio


audio_chunk_iterator = call_tts_stream('')
audio = audio_play(audio_chunk_iterator)

# save results to file
timestamp = int(time.time())
file_name = f'output_total_{timestamp}.{file_format}'
with open(file_name, 'wb') as file:
    file.write(audio)
WebSocket API
API: wss://api.minimax.io/ws/v1/t2a_v2
Create a WebSocket Connection
Call WebSocket library functions (the specific implementation may vary depending on the programming language or library used), passing the request headers and URL to establish a WebSocket connection.
Request
AuthorizationstringRequired
API key
Response
session_idstring
The session ID uniquely identifies the entire session.
eventstring
The event indicates the session type, and 'connected_success' is returned when the connection is successfully established.
trace_idstring
The id of the current conversation. Will be used in order to locate issues during inquiries and feedback
base_resp
Error codes, status messages, and corresponding details, should the request run into any problems.
Show Properties
Create a WebSocket Connection
Request
Copy
{
    "Authorization":"Bearer your_api_key", // api key
}
Response(success)
Response
Copy
{
    "session_id":"xxxx",
    "event":"connected_success"
    "trace_id":"0303a2882bf18235ae7a809ae0f3cca7",
    "base_resp":{
        "status_code":0,
        "status_msg":"success"
    }
}
Send “task_start” event
Sending the task_start event initiates the synthesis task. When the server returns the task_started event, it signifies that the task has successfully begun. Only after receiving this event can you send task_continue or task_finish events to the server.
Request
eventstringRequired
Specifies the command to send. The allowed value for the current step is "task_start"
modelstringRequired
Support the following models: speech-02-hdspeech-02-turbospeech-01-hdspeech-01-turbo
voice_setting
Hide Properties
speedrange: [0.5,2] default: 1.0
The speed of the generated speech. Larger values indicate faster speech.
volrange: (0,10] default: 1.0
The volume of the generated speech. Larger values indicate larger volumes.
pitchrange: [-12,12] default: 0
The pitch of the generated speech. A value of 0 corresponds to default voice output.
voice_idstring
Desired voice. Both system voice ids and cloned voice ids are supported. System voice ids are listed below:
Wise_Woman
Friendly_Person
Inspirational_girl
Deep_Voice_Man
Calm_Woman
Casual_Guy
Lively_Girl
Patient_Man
Young_Knight
Determined_Man
Lovely_Girl
Decent_Boy
Imposing_Manner
Elegant_Man
Abbess
Sweet_Girl_2
Exuberant_Girl
emotionstring
The emotion of the generated speech;
Currently supports seven emotions；
range:["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"]
english_normalizationbool
This parameter supports English text normalization, which improves performance in number-reading scenarios, but this comes at the cost of a slight increase in latency. If not provided, the default value is false
audio_setting
Hide Properties
sample_raterange: [8000,16000,22050,24000,32000,44100] default: 32000
Sample rate of generated sound. Optional.
bitraterange: [32000,64000,128000,256000] default: 128000
Bitrate of generated sound. Optional
formatstring range: [mp3,pcm,flac] default: mp3
Format of generated sound. Optional
channelrange: [1, 2] default: 1
The number of channels of the generated audio.
1: mono
2: stereo
pronunciation_dict
Hide Properties
tonelist
Replacement of text, symbols and corresponding pronunciations that require manual handling.
Replace the pronunciation (adjust the tone/replace the pronunciation of other characters) using the following format:

[“燕少飞/(yan4)(shao3)(fei1)”, “达菲/(da2)(fei1)”, “omg/oh my god”]

For Chinese texts, tones are replaced by numbers, with 1 for the first tone (high), 2 for the second tone (rising), 3 for the third tone (low/dipping), 4 for the fourth tone (falling), and 5 for the fifth tone (neutral).
timber_weightsrequired: either voice_id or timber_weights
Hide Properties
voice_idstring
Desired voice id. Must be given in conjunction with weight param. Only system voice ids are supported (see voice_id above for more information on existing system voices).
weightinteger range: [1, 100]
Must be given in conjunction with voice_id param. Supports up to voice mixing of up to 4 voices. Higher weighted voices will be sampled more heavily than lower weighted ones.
language_booststring
Enhance the ability to recognize specified languages and dialects.
Supported values include:
'Chinese', 'Chinese,Yue', 'English', 'Arabic', 'Russian', 'Spanish', 'French', 'Portuguese', 'German', 'Turkish', 'Dutch', 'Ukrainian', 'Vietnamese', 'Indonesian', 'Japanese', 'Italian', 'Korean', 'Thai', 'Polish', 'Romanian', 'Greek', 'Czech', 'Finnish', 'Hindi', 'auto'
Response
session_idstring
The session ID uniquely identifies the entire session.
eventstring
The event indicates the session type. The "task_started" event is returned upon successful completion of the current step
trace_idstring
The id of the current conversation. Will be used in order to locate issues during inquiries and feedback
base_respobject
Error codes, status messages, and corresponding details, should the request run into any problems.
Show Properties
send "task-start"
Request
Copy
{
    "event":"task_start",
    "model":"speech-02-turbo",
    "language_boost":"English",
    "voice_setting":{
        "voice_id":"Wise_Woman",
        "speed":1,
        "vol":1,
        "pitch":0,
        "emotion":"happy"
    },
    "pronunciation_dict":{},
    "audio_setting":{
        "sample_rate":32000,
        "bitrate":128000,
        "format":"mp3",
        "channel":1
    }    
}
Response Sample(task_started)
Response
Copy
{
    "session_id":"xxxx",
    "event":"task_started",
    "trace_id":"0303a2882bf18235ae7a809ae0f3cca7",
    "base_resp":{
        "status_code":0,
        "status_msg":"success"
    }
}
Send "task_continue" event
Upon receiving the task_started event from the server, the task is officially initiated. You can then send text to be synthesized via the task_continue event. Multiple task_continue events may be sent sequentially. If no events are transmitted within 120 seconds after the last server response, the WebSocket connection will be automatically terminated.
Request
eventstring
Specifies the command to send. The allowed value for the current step is "task_continue"
textstringRequired
Text to be synthesized. Character limit < 5000 chars. Paragraph markers will be replaced by line breaks. (To manually add a pause, insert the phrase <#x#> where x refers to the number of seconds to pause. Supports 0.01-99.99, with an accuracy of at most 2 decimal places).
Response
dataobject
Data may be returned as null. When referring to sample code, please refer primarily to non-null responses
Show Properties
trace_idstring
The id of the current conversation. Will be used in order to locate issues during inquiries and feedback
session_idstring
The session ID uniquely identifies the entire session.
eventstring
The event indicates the session type. The "task_continued" event is returned upon successful completion of the current step
is_finalbool
Indicates whether the request has been completed
extra_infoobject
extra info
Show Properties
base_respobject
Error codes, status messages, and corresponding details, should the request run into any problems.
Show Properties
Send "task_continue"
Copy
{
       "event":"task_continue",
       "text":"Hello, this is the text message for test"
}
Response
Copy
{
    "data":{
        "audio":"xxx",
    },
    "extra_info":{
        "audio_length":935,
        "audio_sample_rate":32000,
        "audio_size":15597,
        "bitrate":128000,
        "word_count":1,
        "invisible_character_ratio":0,
        "usage_characters":4,
        "audio_format":"mp3",
        "audio_channel":1
    },
    "session_id":"xxxx",
    "event":"task_continued",
    "is_final":false,
    "trace_id":"0303a2882bf18235ae7a809ae0f3cca7",
    "base_resp":{
        "status_code":0,
        "status_msg":"success"
    }
}
Send "task_finish" event
When the task_finish event is sent, the server will wait for all synthesis tasks in the current queue to complete upon receiving this event, then close the WebSocket connection and terminate the task.
Request
eventstring
Specifies the command to send. The allowed value for the current step is "task_finish"
Response
trace_idstring
The id of the current conversation. Will be used in order to locate issues during inquiries and feedback
session_idstring
The session ID uniquely identifies the entire session.
eventstring
The event indicates the session type. The "task_finished" event is returned upon successful completion of the current step
base_respobject
Error codes, status messages, and corresponding details, should the request run into any problems.
Show Properties
send "task_finish" event
Copy
{
    "event":"task_finish"
 }
Response
Copy
{
    "session_id":"xxxx",
    "event":"task_finished",
    "trace_id":"0303a2882bf18235ae7a809ae0f3cca7",
    "base_resp":{
        "status_code":0,
        "status_msg":"success"
    }
}
“task_failed” event
If a "task_failed" event is received, it indicates that the task has failed. You must close the WebSocket connection and handle the error.
Response
trace_idstring
The id of the current conversation. Will be used in order to locate issues during inquiries and feedback
session_idstring
The session ID uniquely identifies the entire session.
eventstring
The event indicates the session type. The "task_failed" event is returned when the task is failed
base_respobject
Error codes, status messages, and corresponding details, should the request run into any problems.
Show Properties
"task_failed" response sample
Copy
{
    "session_id":"xxxx",
    "event":"task_failed",
    "trace_id":"0303a2882bf18235ae7a809ae0f3cca7",
    "base_resp":{
        "status_code":1004,
        "status_msg":"XXXXXXX"
    }
}
API Call Sample（Websocket）
Websocket API Call Sample
Copy
import asyncio
import websockets
import json
import ssl
from pydub import AudioSegment  # Import audio processing library
from pydub.playback import play
from io import BytesIO

MODULE = "speech-02-hd"
EMOTION = "happy"


async def establish_connection(api_key):
    """Establish WebSocket connection"""
    url = "wss://api.minimax.io/ws/v1/t2a_v2"
    headers = {"Authorization": f"Bearer {api_key}"}

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        ws = await websockets.connect(url, additional_headers=headers, ssl=ssl_context)
        connected = json.loads(await ws.recv())
        if connected.get("event") == "connected_success":
            print("Connection successful")
            return ws
        return None
    except Exception as e:
        print(f"Connection failed: {e}")
        return None


async def start_task(websocket, text):
    """Send task start request"""
    start_msg = {
        "event": "task_start",
        "model": MODULE,
        "voice_setting": {
            "voice_id": "Wise_Woman",
            "speed": 1,
            "vol": 1,
            "pitch": 0,
            "emotion": EMOTION
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    await websocket.send(json.dumps(start_msg))
    response = json.loads(await websocket.recv())
    return response.get("event") == "task_started"


async def continue_task(websocket, text):
    """Send continue request and collect audio data"""
    await websocket.send(json.dumps({
        "event": "task_continue",
        "text": text
    }))

    audio_chunks = []
    chunk_counter = 1  # Add chunk counter
    while True:
        response = json.loads(await websocket.recv())
        if "data" in response and "audio" in response["data"]:
            audio = response["data"]["audio"]
            # Print encoding information (first 20 chars + total length)
            print(f"Audio chunk #{chunk_counter}")
            print(f"Encoded length: {len(audio)} bytes")
            print(f"First 20 chars: {audio[:20]}...")
            print("-" * 40)

            audio_chunks.append(audio)
            chunk_counter += 1
        if response.get("is_final"):
            break
    return "".join(audio_chunks)


async def close_connection(websocket):
    """Close connection"""
    if websocket:
        await websocket.send(json.dumps({"event": "task_finish"}))
        await websocket.close()
        print("Connection closed")


async def main():
    API_KEY = "your_api_key_here"
    TEXT = "Hello, this is a text message for test"

    ws = await establish_connection(API_KEY)
    if not ws:
        return

    try:
        if not await start_task(ws, TEXT[:10]):
            print("Failed to start task")
            return

        hex_audio = await continue_task(ws, TEXT)

        # Decode hex audio data
        audio_bytes = bytes.fromhex(hex_audio)

        # Save as MP3 file
        with open("output.mp3", "wb") as f:
            f.write(audio_bytes)
        print("Audio saved as output.mp3")

        # Directly play audio (requires pydub and simpleaudio)
        audio = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")
        print("Playing audio...")
        play(audio)

    finally:
        await close_connection(ws)


if __name__ == "__main__":
    asyncio.run(main())