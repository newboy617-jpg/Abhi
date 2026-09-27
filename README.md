# JARVIS - your personal AI assistant

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

## How it works

```
jarvis/
  __main__.py   standby -> phone arrives -> greet -> conversation -> standby
  presence.py   Bluetooth (signal strength) / Wi-Fi phone detection in the background
  voice.py      microphone speech recognition + text-to-speech
  skills.py     instant local commands (time, open apps/sites, YouTube, Google)
  brain.py      Claude with web search for everything else
```

Change the model with `JARVIS_MODEL` in `.env` (default `claude-opus-5`). Edit `SYSTEM_PROMPT`
in `brain.py` to change Jarvis's personality, or add your own commands in `skills.py`.
