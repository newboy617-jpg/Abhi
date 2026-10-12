# JARVIS - your personal AI assistant

> This repo also includes **[Voice Clone](#voice-cloning)**: clone a voice from a short recording
> and make it say anything, in 23 languages, and have Jarvis talk in it.

A voice assistant inspired by Iron Man's JARVIS. It **wakes up and says hello when you
walk into your room** by detecting your phone over Bluetooth (about 10 m range), then
listens to your voice, runs quick commands on your computer and answers anything else
with Claude (with live web search for news, weather, scores and so on).

## What it can do

| Say... | Jarvis... |
|---|---|
| *(walk into your room with your phone)* | "Hello sir, welcome back. Good evening. How can I help you?" |
| "What time is it?" / "What's the date?" | tells you instantly |
| "Open YouTube" / "Open GitHub" / "Open calculator" | opens the website or app |
| "Play Believer by Imagine Dragons" | plays it on YouTube |
| "Search for best laptops 2026" | opens Google results |
| "What's the weather in Mumbai?" / "Who won the match yesterday?" | searches the web and answers |
| "Explain black holes" / "Tell me a joke" / anything else | answers with Claude, remembering the conversation |
| "Forget everything" | clears its memory |
| "Go to sleep" / "Goodbye" | goes on standby (say "Jarvis" to wake it) |
| "Shut down" | quits |

When you leave the room with your phone, Jarvis notices and goes back on standby, ready to greet you next time.

## Setup

You need Python 3.10+ on a computer with Bluetooth and a microphone (a laptop is perfect).

```bash
git clone https://github.com/newboy617-jpg/Abhi.git
cd Abhi
pip install -r requirements.txt
cp .env.example .env        # on Windows: copy .env.example .env
```

Open `.env` and paste your Anthropic API key (get one at https://console.anthropic.com).

> **PyAudio trouble?** Windows: `pip install pipwin && pipwin install pyaudio`.
> macOS: `brew install portaudio` first. Linux: `sudo apt install portaudio19-dev python3-pyaudio espeak`.

## Make it detect your phone

1. Turn on Bluetooth on your phone and keep the Bluetooth settings screen open
   (that makes it visible).
2. Hold the phone next to your computer and run:
   ```bash
   python -m jarvis.presence --scan
   ```
3. Your phone is usually the one at the top with the strongest signal (e.g. `-45 dBm`)
   and a name like `Abhi's Galaxy`. Walk to the far side of the room and scan again to
   see what the signal looks like at the edge of your room.
4. Put its name (or address) in `.env`:
   ```
   JARVIS_PHONE_NAME=Abhi's Galaxy
   JARVIS_RSSI_THRESHOLD=-80
   ```
   `-80` is roughly 10 metres indoors. Use `-70` if Jarvis greets you from outside the room.

**If your phone doesn't show up or its address keeps changing** (iPhones and many newer
Androids hide or randomise their Bluetooth identity for privacy), install the free
**nRF Connect** app, go to *Advertiser*, and create an advertisement with a device name
such as `JarvisKey`. Then set `JARVIS_PHONE_NAME=JarvisKey`. A smartwatch or Bluetooth
earbuds that you always carry also work well.

**Wi-Fi alternative:** give your phone a fixed IP in your router and set
`JARVIS_PHONE_IP=192.168.1.25`. This detects you anywhere in the house rather than just
in your room.

## Run it

```bash
python -m jarvis            # full voice mode, waits for your phone
python -m jarvis --text     # type instead of talking
python -m jarvis --mute     # print replies instead of speaking
python -m jarvis --no-presence   # start talking right away, no phone detection
```

Leave it running on your laptop and it will greet you every time you come into your room.

**Start automatically when the computer turns on**
- Windows: press `Win+R`, type `shell:startup`, and put a shortcut there to a `.bat` file containing
  `cd C:\path\to\Abhi && python -m jarvis`.
- macOS / Linux: add `cd /path/to/Abhi && python3 -m jarvis` to your login items or crontab (`@reboot`).

## Voice cloning

`voiceclone` copies a voice from a video or audio file (or your microphone) and then says any
text you type in that voice, in English, Hindi or 21 other languages. It can pull the voice out
of a video and strip away background music and noise first. It runs on your own computer
using Resemble AI's open-source [Chatterbox](https://github.com/resemble-ai/chatterbox) models
(MIT licence), so recordings never leave your machine.

### Install

The voice models need PyTorch, which is large, so it has its own requirements file. A separate
virtual environment is a good idea:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-voiceclone.txt
pip install -r requirements.txt    # only if you also want Jarvis in this environment
```

- Python 3.10 to 3.13 works best.
- **NVIDIA GPU on Windows:** first run
  `pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124`
  (the default Windows build only uses the CPU). On Linux the GPU build is the default, and on
  Apple Silicon Macs the GPU is used automatically.
- It also runs on a normal CPU, just more slowly.
- To read videos and formats like m4a, install **ffmpeg**: Windows `winget install ffmpeg`,
  macOS `brew install ffmpeg`, Linux `sudo apt install ffmpeg`.
- The first time you generate speech, the model (a few GB) downloads from Hugging Face.

### Clone a voice and use it

```bash
# 1. Clone: from a video, taking the voice out of the music and background noise...
python -m voiceclone add "Abhi" --video interview.mp4 --isolate
#    ...only using the part where they talk (here from 1:05 to 1:35)...
python -m voiceclone add "Abhi" --video interview.mp4 --start 1:05 --end 1:35 --isolate
#    ...from an audio file (mp3, wav, m4a, ogg...)...
python -m voiceclone add "Abhi" --audio voice_note.m4a
#    ...or record yourself reading a short passage (20 seconds)
python -m voiceclone add "Abhi" --record
#    When it's done it offers to let you type text and hear it straight away.

# 2. Speak in that voice. The audio plays and is saved in output/
python -m voiceclone say "Abhi" "Hello! This is my cloned voice speaking."
python -m voiceclone say "Abhi" "नमस्ते, आप कैसे हैं?" --lang hi
python -m voiceclone say "Abhi" --file speech.txt -o speech.wav   # any length of text

# 3. Or give it dialogue line by line: type a line, press Enter, hear it in that voice
python -m voiceclone talk "Abhi"

python -m voiceclone list            # your saved voices
python -m voiceclone remove "Abhi"
```

Prefer clicking to typing? `python -m voiceclone ui` opens a web app in your browser where you can
upload a video or audio file (or record yourself), type text, tweak the style and download
the result.

**Tips for a close match**
- Use 10-30 seconds of one person talking naturally. With a video, use `--start`/`--end` to pick
  a part where only that person is talking (without them, the first 3 minutes are used).
- Add `--isolate` when there's music or background noise. It uses Meta's open-source Demucs
  model to keep just the voice (it downloads about 80 MB the first time).
- A phone voice note recorded in a quiet room is fine. Silences are trimmed automatically.
- The clone copies the sample's mood too, so a calm sample gives calm speech.

**Style controls for `say` and `talk`**

| Option | What it does |
|---|---|
| `--emotion 0.5` | `0.25` calm, `0.5` natural, `1.0` and up dramatic |
| `--cfg 0.5` | `0.3` slows fast talkers down; `0` drops the accent when the voice speaks another language |
| `--temperature 0.8` | higher is more expressive, lower is steadier |
| `--lang hi` | speak another language: ar da de el en es fi fr he hi it ja ko ms nl no pl pt ru sv sw tr zh |
| `--fast` | much faster English model (ignores `--emotion`) |

### Make Jarvis talk in a cloned voice

Clone a voice as above, then put its name in `.env`:

```
JARVIS_VOICE=Abhi
```

Jarvis uses the fast English model. A GPU keeps replies snappy; on a CPU each reply takes a few
extra seconds. If anything goes wrong, Jarvis falls back to its normal voice.

### Use it responsibly

Only clone your own voice or the voice of someone who has agreed to it. Using someone's voice
without permission to deceive people, commit fraud or harass someone is illegal in many places.
To help with this:
- `add` asks whose voice it is and stores that note with the voice.
- Every generated clip carries Resemble AI's inaudible **Perth watermark**. Check any clip with
  `python -m voiceclone check clip.wav`.

## How it works

```
jarvis/
  __main__.py   standby -> phone arrives -> greet -> conversation -> standby
  presence.py   Bluetooth (signal strength) / Wi-Fi phone detection in the background
  voice.py      microphone speech recognition + text-to-speech
  skills.py     instant local commands (time, open apps/sites, YouTube, Google)
  brain.py      Claude with web search for everything else
voiceclone/
  __main__.py   command line: add / say / talk / list / remove / ui / check
  library.py    saved voices (voices/<name>/reference.wav + profile.json)
  audio.py      reading audio/video, removing background sound, recording, playback
  engine.py     Chatterbox voice models: picks the right one, splits long text
  app.py        the web app
```

Change the model with `JARVIS_MODEL` in `.env` (default `claude-opus-5`). Edit `SYSTEM_PROMPT`
in `brain.py` to change Jarvis's personality, or add your own commands in `skills.py`.
