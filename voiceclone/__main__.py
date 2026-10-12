"""Voice cloning from the command line.

  python -m voiceclone add "Abhi" --audio my_voice.mp3     clone a voice from a recording
  python -m voiceclone add "Abhi" --video clip.mp4 --isolate   ...or from a video, minus music/noise
  python -m voiceclone add "Abhi" --record 20              ...or record it with your mic
  python -m voiceclone say "Abhi" "Hello, how are you?"    speak in that voice
  python -m voiceclone talk "Abhi"                         type lines, hear each one in that voice
  python -m voiceclone list                                show saved voices
  python -m voiceclone ui                                  open the web app
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

from . import audio
from .library import VoiceLibrary, slugify

OUTPUT_DIR = Path("output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m voiceclone", description="Clone a voice and make it say anything.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="clone a new voice from a recording or your microphone")
    p.add_argument("name", help="a name for the voice, e.g. Abhi")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--audio", "--video", dest="audio", metavar="FILE",
                     help="audio or video with the voice in it (mp3, wav, m4a, mp4, mkv, ...)")
    src.add_argument("--record", metavar="SECONDS", type=float, nargs="?", const=20,
                     help="record from your microphone (default 20 seconds)")
    p.add_argument("--start", metavar="TIME", help="where the person starts talking, e.g. 1:05")
    p.add_argument("--end", metavar="TIME", help="where to stop, e.g. 1:35")
    p.add_argument("--isolate", action="store_true",
                   help="remove background music and noise first (recommended for videos)")
    p.add_argument("--lang", default="en", help="language the voice usually speaks (default en)")
    p.add_argument("--consent", metavar="TEXT",
                   help="whose voice this is and that they agreed, e.g. 'my own voice'")

    def style_options(p):
        p.add_argument("--lang", help="language to speak, e.g. en, hi, fr (default: the voice's own)")
        p.add_argument("--emotion", type=float, default=0.5, help="0.25 calm, 0.5 natural, 1.0 dramatic")
        p.add_argument("--cfg", type=float, default=0.5,
                       help="0.3 for slower speech; 0 to drop the accent in another language")
        p.add_argument("--temperature", type=float, default=0.8, help="higher = more varied delivery")
        p.add_argument("--fast", action="store_true", help="use the faster English model")
        p.add_argument("--device", help="cuda, mps or cpu (default: best available)")

    p = sub.add_parser("say", help="make a saved voice say something")
    p.add_argument("name", help="saved voice to use")
    p.add_argument("text", nargs="*", help="what to say")
    p.add_argument("-f", "--file", help="read the text from a .txt file instead")
    p.add_argument("-o", "--out", help="where to save the .wav (default output/<voice>-<time>.wav)")
    p.add_argument("--no-play", action="store_true", help="just save the file, don't play it")
    style_options(p)

    p = sub.add_parser("talk", help="type dialogue line by line and hear each line in the voice")
    p.add_argument("name", help="saved voice to use")
    style_options(p)

    sub.add_parser("list", help="show saved voices")

    p = sub.add_parser("remove", help="delete a saved voice")
    p.add_argument("name")

    p = sub.add_parser("ui", help="open the voice cloning web app in your browser")
    p.add_argument("--port", type=int, default=7860)
    p.add_argument("--share", action="store_true", help="also create a temporary public link")
    p.add_argument("--device", help="cuda, mps or cpu (default: best available)")

    p = sub.add_parser("check", help="check whether a clip carries the AI-voice watermark")
    p.add_argument("file")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        {"add": add, "say": say, "talk": talk, "list": list_voices, "remove": remove, "ui": ui, "check": check}[args.command](args)
    except (ValueError, KeyError, FileNotFoundError, RuntimeError) as e:
        sys.exit(f"Error: {e.args[0] if e.args else e}")
    except KeyboardInterrupt:
        print()


def add(args):
    from .engine import LANGUAGES

    lang = args.lang.lower()
    if lang not in LANGUAGES:
        raise ValueError(f"Unsupported language '{args.lang}'. Choose from: {', '.join(LANGUAGES)}")
    slugify(args.name)  # fail on a bad name before recording anything

    consent = args.consent
    if not consent:
        if not sys.stdin.isatty():
            raise ValueError("Add --consent saying whose voice this is and that they agreed to it being cloned.")
        print("Only clone your own voice or a voice whose owner has agreed to it.")
        consent = input("Whose voice is this, and do they agree? (e.g. 'my own voice'): ").strip()
        if not consent:
            print("Cancelled.")
            return

    if args.audio:
        print(f"Reading the voice from {Path(args.audio).name}...")
        wav = audio.extract_voice(args.audio, start=args.start, end=args.end, isolate=args.isolate)
        source = Path(args.audio).name
    else:
        print("\nRead this aloud in your normal speaking voice:\n")
        print(f"  {audio.READING_PASSAGE}\n")
        input(f"Press Enter to start a {args.record:g}-second recording...")
        for n in (3, 2, 1):
            print(f"  {n}...")
            time.sleep(1)
        print("Recording - speak now!")
        wav = audio.record(args.record)
        print("Done.")
        if args.isolate:
            wav = audio.isolate_voice(wav)
        source = "microphone"

    voice = VoiceLibrary().add(args.name, wav, consent=consent, language=lang, source=source)
    print(f"\nSaved voice '{voice.name}' ({voice.seconds:g} s of speech) in {voice.folder}")
    if voice.seconds < audio.GOOD_SECONDS:
        print(f"Tip: {audio.GOOD_SECONDS}-30 s of clear speech gives a closer match.")
    print(f'Use it any time:  python -m voiceclone talk "{voice.name}"')

    if sys.stdin.isatty():
        answer = input("\nType some text for this voice to say now? [Y/n] ").strip().lower()
        if answer in ("", "y", "yes"):
            talk(build_parser().parse_args(["talk", voice.name]))


def say(args):
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        text = " ".join(args.text)
    if not text.strip():
        raise ValueError("Give some text to say, or use --file script.txt")

    voice = VoiceLibrary().get(args.name)

    from .engine import VoiceCloner

    speak(VoiceCloner(device=args.device), voice, text, args, out=args.out, play=not args.no_play)


def talk(args):
    voice = VoiceLibrary().get(args.name)

    from .engine import VoiceCloner

    cloner = VoiceCloner(device=args.device)
    print(f"Type a line and press Enter to hear it as '{voice.name}'. Press Enter on an empty line to quit.")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            break
        try:
            speak(cloner, voice, line, args)
        except ValueError as e:
            print(f"Error: {e}")


def speak(cloner, voice, text, args, out=None, play=True):
    """Generate `text` in `voice`, save it, and play it if there are speakers."""
    print(f"Speaking as '{voice.name}'...")
    start = time.time()
    wav, sr = cloner.speak(voice, text, language=args.lang, emotion=args.emotion,
                           cfg_weight=args.cfg, temperature=args.temperature, fast=args.fast)
    out = Path(out) if out else OUTPUT_DIR / f"{slugify(voice.name)}-{datetime.now():%Y%m%d-%H%M%S}.wav"
    audio.save(out, wav, sr)
    print(f"Saved {audio.duration(wav, sr):.1f} s of audio to {out} (took {time.time() - start:.0f} s)")

    if play and audio.can_play():
        audio.play(wav, sr)


def list_voices(args):
    voices = VoiceLibrary().all()
    if not voices:
        print('No voices yet. Add one with:  python -m voiceclone add "Name" --record')
        return
    for v in voices:
        print(f"  {v.name:<20} {v.language:<4} {v.seconds:>5g} s   consent: {v.consent}")


def remove(args):
    VoiceLibrary().remove(args.name)
    print(f"Deleted voice '{args.name}'.")


def ui(args):
    from .app import build

    build(device=args.device).launch(server_port=args.port, share=args.share, inbrowser=True)


def check(args):
    from .engine import watermark_score

    score = watermark_score(args.file)
    if score > 0.5:
        print(f"Watermark found (confidence {score:.2f}): this clip was made with an AI voice model.")
    else:
        print(f"No watermark found (confidence {score:.2f}). That doesn't prove it's a real recording.")


if __name__ == "__main__":
    main()
