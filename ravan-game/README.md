# Shoot Ravan's Ten Heads

A tap-to-shoot archery game for a Dandiya or Navratri night stall. Ravan's paper
effigy sways on the festival ground. Players tap where they want the arrow to land,
knock off all ten heads, then hit the glowing navel to burn Ravan with fireworks.

Everything is in one file, `index.html`. It needs no internet, no install and no
server, so it keeps working when the venue Wi-Fi does not.

## How to play

| Step | What happens |
|---|---|
| Tap or click where the arrow should land | The arrow flies from the bow to that spot |
| Hit a head | The head flies off and Ravan sways faster |
| Knock off all ten heads | Ravan's navel starts to glow |
| Hit the navel | Ravan burns, fireworks go off, big bonus points |

Each game has 15 arrows and 60 seconds by default. Ravan slows down at each end of
his sway, which is the best moment to shoot.

**Scoring.** A head is worth 100 points, plus 25 more for each hit in a row (up to
+100). The navel is worth 500. A player who burns Ravan also gets 75 points for each
arrow fewer than 15 used and 10 points for each second under 60. These bonuses use
the same baseline whatever the stall settings, so changing settings mid-evening does
not inflate scores. The top 10 scores stay on the leaderboard, tagged with the
difficulty when it is not Normal.

## Ravan talks to each player in their language

After **Play**, each player types their name and picks their state. Ravan then
speaks to them by name in that state's language. Where a state has several
languages, the player taps one. For example, Uttar Pradesh offers Hindi, Bhojpuri
and Awadhi, and Bihar offers Bhojpuri, Maithili, Magahi and Hindi. English is
always offered too.

| Moment | What Ravan does |
|---|---|
| Game starts | Dares the player by name |
| Every other miss | Mocks the shot |
| Second, fifth and eighth head | Boasts that he has more heads |
| All ten heads gone | Gloats about the nectar in his navel |
| Player loses | Taunts them by name, then laughs |
| Player wins | Admits defeat |
| Start screen | Shouts a dare in a different language every minute or so |

His words show as a large subtitle in the player's script, with a short English line
underneath so the crowd can follow. Scores are saved under the player's name, and the
leaderboard shows their state, for example "Priya · BR".

**Languages:** Hindi, Bhojpuri, Awadhi, Maithili, Magahi, Haryanvi, Rajasthani
(Marwari), Chhattisgarhi, Punjabi, Urdu, Bengali, Odia, Assamese, Nepali, Marathi,
Gujarati, Konkani, Tamil, Telugu, Kannada, Malayalam and English.

Each language was written by one translator and then checked and corrected by a
separate native-language reviewer. Before the event, ask a student from each state
to read their language's lines. Magahi needs this most. Bhojpuri, Awadhi, Maithili,
Haryanvi, Rajasthani, Chhattisgarhi, Odia, Assamese, Nepali, Konkani, Telugu, Kannada
and Malayalam should get a quick look too. To fix a line, open **Settings**, press
**Edit Ravan's lines**, pick the language, change the text and press **Save**. Put
each line on its own row and write `{name}` where the player's name goes.

**Giving Ravan a real voice.** The best Ravan is a real person. Open **Settings**,
press **Edit Ravan's lines** and pick a language. Next to each line, press **Record**,
say the line in a big Ramlila voice without the player's name (the name still shows
on screen), and press **Stop**. You can also record on a phone and press **Upload**.
The game trims the silence, evens out the volume, makes the voice deeper and adds
Ravan's loudspeaker echo (untick the box to switch the effect off). Recordings are
saved on that device and are used in place of the computer voice. A student who can
do a good Ravan voice can record the main lines of a language in a few minutes.

**The computer voice.** Lines that are not recorded are read with the device's own
text-to-speech voice. The game picks a man's voice where the device has one, and the
same screen lets you choose the voice for each language and hear it, or choose
**No voice** so Ravan only shows subtitles and laughs. Bhojpuri and the other
Hindi-belt dialects use the Hindi voice. Settings lists which languages the device
can speak.

- **Windows:** open Settings, then Time & language, then Speech, then Add voices.
  The Hindi pack includes Microsoft Hemant, a man's voice that works offline.
- **Android:** the voice is chosen in the tablet's own settings, under Accessibility,
  Text-to-speech output, the engine's settings, Install voice data, then the language.
  The game cannot choose it, so recording the lines is the surest way to a man's voice.

Turn **Ask each player's name and state** off in Settings to skip the form and use
one language for everyone.

## Running it at the stall

**Touch laptop or Windows tablet**

1. Copy `index.html` to the device.
2. Open it in Chrome or Edge.
3. Press **Full screen** on the start screen, or press `F`.

**Android tablet or iPad**

1. Copy `index.html` to the tablet, or open the published link once while online.
2. Open it in Chrome (Android) or Safari (iPad).
3. Use **Add to Home Screen** so it opens full screen like an app.

**Big TV or projector**

1. Connect the PC or laptop to the TV with an HDMI cable.
2. Open `index.html`, then press **Full screen**.
3. Players click with a mouse. A touch laptop also works, since the TV shows the same screen.
4. The game scales to any size, including 4K, and the text is sized to read from a distance.

A tablet can also be mirrored to a TV with Chromecast, Miracast or AirPlay. Players
tap on the tablet while the crowd watches on the TV.

## Stall settings

Press **Settings** on the start screen to change:

- **Stall name** shown above the title.
- **Prize line**, for example "Top score tonight wins a chocolate box".
- **Arrows per game**: 12, 15, 18, 20 or 25. There are 11 targets, so 12 is the minimum.
- **Time limit**: 30 to 120 seconds.
- **Difficulty**: Easy for children, Normal, or Hard for repeat players.
- **Sound effects** on or off. The `M` key also toggles sound.
- **Ravan's laugh**: keep the game's own laugh, or choose **Recorded laugh** to use a recording.
  Record the laugh on a phone (a few seconds, under 1 MB), press **Choose a recording**
  and pick the file. The game levels its volume, saves it on the device and plays it for
  every laugh. **Play Ravan's laugh** tests the speakers before the crowd arrives.
- **Players and languages**: ask for each player's name and state, pick the language
  used when not asking, switch Ravan's speaking voice on or off, and edit his lines.
- **Clear leaderboard** at the start of each night. Tap it twice to confirm.

Settings and scores are saved in the browser on that device only.

## Keys for the stall owner

| Key | Action |
|---|---|
| `F` | Full screen on or off |
| `M` | Sound on or off |
| `Esc` | Pause or resume a game, or go back from the name screen or Settings |
| `Enter` | Start a game from the start screen or result screen |

The game pauses by itself if the browser tab is hidden. The result screen returns to
the start screen after 45 seconds, so the next player always sees the leaderboard.

## Stall tips

- Charge 20 to 30 rupees per game and give a prize for the top score each hour.
- Keep the leaderboard visible between games. A score to beat brings people back.
- Use Easy for small children and Normal or Hard once the crowd gets competitive.
- Turn the volume up. Ravan laughs when a game starts, when a player misses and when
  a player loses. Between games he laughs every half minute or so to pull in passers-by.
  The sound starts after the first tap on the screen, because browsers block sound until then.
- Keep the device plugged in. The game asks the screen to stay awake while it runs.
