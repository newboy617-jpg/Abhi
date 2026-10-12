"""The voice cloning web app:  python -m voiceclone ui"""

from datetime import datetime
from pathlib import Path

import gradio as gr

from . import audio
from .engine import LANGUAGES, VoiceCloner, watermark_score
from .library import VoiceLibrary, slugify

OUTPUT_DIR = Path("output")
LANGUAGE_CHOICES = [(f"{name} ({code})", code) for code, name in LANGUAGES.items()]


def build(device=None) -> gr.Blocks:
    library = VoiceLibrary()
    cloner = VoiceCloner(device=device)  # models load on first use

    def voice_picker(selected=None):
        names = library.names()
        return gr.Dropdown(choices=names, value=selected or (names[0] if names else None))

    def add_voice(upload, recording, start, end, isolate, name, language, whose, agreed):
        sample = upload or recording
        if not sample:
            raise gr.Error("Upload a video or audio file, or record a sample, first.")
        if not agreed:
            raise gr.Error("Tick the box to confirm the owner of this voice agreed to it being cloned.")
        try:
            wav = audio.extract_voice(sample, start=start, end=end, isolate=isolate)
            voice = library.add(
                name or "",
                wav,
                consent=f"{whose.strip() or 'not specified'} (confirmed in web app)",
                language=language,
                source=Path(sample).name if upload else "microphone",
            )
        except (ValueError, RuntimeError, FileNotFoundError) as e:
            raise gr.Error(str(e))
        note = f"Saved **{voice.name}** ({voice.seconds:g} s of speech). Go to the *Speak* tab to use it."
        if voice.seconds < audio.GOOD_SECONDS:
            note += f"\n\nTip: {audio.GOOD_SECONDS}-30 s of clear speech gives a closer match."
        return note, voice_picker(voice.name)

    def speak(name, text, language, emotion, cfg_weight, temperature, fast):
        if not name:
            raise gr.Error("Pick a voice first (clone one in the first tab).")
        try:
            voice = library.get(name)
            wav, sr = cloner.speak(voice, text, language=language or None, emotion=emotion,
                                   cfg_weight=cfg_weight, temperature=temperature, fast=fast)
        except (KeyError, ValueError) as e:
            raise gr.Error(e.args[0])
        out = OUTPUT_DIR / f"{slugify(voice.name)}-{datetime.now():%Y%m%d-%H%M%S}.wav"
        audio.save(out, wav, sr)
        return str(out)

    def check(clip):
        if not clip:
            raise gr.Error("Upload a clip to check.")
        score = watermark_score(clip)
        if score > 0.5:
            return f"**Watermark found** (confidence {score:.2f}): this clip was made with an AI voice model."
        return f"**No watermark found** (confidence {score:.2f}). That doesn't prove it's a real recording."

    with gr.Blocks(title="Voice Clone") as demo:
        gr.Markdown("# Voice Clone\nClone a voice from a short recording, then make it say anything.")

        with gr.Tab("1. Clone a voice"):
            gr.Markdown(
                "Give a video or audio file where the person talks for at least 10 seconds, "
                "or record yourself reading this:\n\n"
                f"> {audio.READING_PASSAGE}"
            )
            with gr.Row():
                with gr.Column():
                    upload = gr.File(label="Video or audio file (mp4, mkv, mp3, wav, m4a...)",
                                     file_types=["video", "audio"], type="filepath")
                    recording = gr.Audio(sources=["microphone"], type="filepath", label="...or record yourself")
                    with gr.Row():
                        start = gr.Textbox(label="Start at (optional)", placeholder="e.g. 1:05")
                        end = gr.Textbox(label="End at (optional)", placeholder="e.g. 1:35")
                    isolate = gr.Checkbox(value=True, label="Remove background music and noise")
                    gr.Markdown("Pick a part where only this person is talking. "
                                "Without times, the first 3 minutes are used.")
                with gr.Column():
                    name = gr.Textbox(label="Name for this voice", placeholder="e.g. Abhi")
                    language = gr.Dropdown(LANGUAGE_CHOICES, value="en", label="Language they usually speak")
                    whose = gr.Textbox(label="Whose voice is this?",
                                       placeholder="e.g. my own voice / my friend Rahul")
                    agreed = gr.Checkbox(label="This is my voice, or its owner has agreed to it being cloned")
                    add_btn = gr.Button("Clone voice", variant="primary")
                    add_note = gr.Markdown()

        with gr.Tab("2. Speak"):
            with gr.Row():
                with gr.Column():
                    voice = gr.Dropdown(label="Voice", choices=library.names())
                    text = gr.Textbox(label="Text", lines=6, placeholder="Type anything, any length...")
                    speak_lang = gr.Dropdown([("Same as the voice", "")] + LANGUAGE_CHOICES, value="",
                                             label="Speak in")
                    with gr.Accordion("Style", open=False):
                        emotion = gr.Slider(0.25, 2.0, value=0.5, step=0.05,
                                            label="Emotion (0.5 natural, higher is more dramatic)")
                        cfg_weight = gr.Slider(0.0, 1.0, value=0.5, step=0.05,
                                               label="Pace / accent (lower is slower; 0 drops the accent in other languages)")
                        temperature = gr.Slider(0.05, 2.0, value=0.8, step=0.05,
                                                label="Variation (higher is more expressive, lower more steady)")
                        fast = gr.Checkbox(label="Fast mode (English only, ignores emotion)")
                    speak_btn = gr.Button("Generate speech", variant="primary")
                with gr.Column():
                    result = gr.Audio(label="Cloned speech", type="filepath")
                    gr.Markdown(
                        "Every clip carries an inaudible watermark marking it as AI-generated. "
                        "The first run downloads the voice model (a few GB)."
                    )

        with gr.Tab("Check a clip"):
            gr.Markdown("Find out whether a clip was generated by this kind of model.")
            clip = gr.Audio(sources=["upload"], type="filepath", label="Clip")
            check_btn = gr.Button("Check")
            check_note = gr.Markdown()

        add_btn.click(add_voice, [upload, recording, start, end, isolate, name, language, whose, agreed],
                      [add_note, voice])
        speak_btn.click(speak, [voice, text, speak_lang, emotion, cfg_weight, temperature, fast], result)
        check_btn.click(check, clip, check_note)
        demo.load(voice_picker, None, voice)

    return demo
