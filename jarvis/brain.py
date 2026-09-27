"""Jarvis's brain: a conversation with Claude that can search the web."""

import os
from datetime import datetime

import anthropic

MODEL = os.environ.get("JARVIS_MODEL", "claude-opus-5")

SYSTEM_PROMPT = """You are JARVIS, a witty, loyal and highly capable personal AI assistant, \
in the spirit of Tony Stark's assistant. Address the user as "sir" (or by their name if \
they tell you it). Your replies are spoken aloud by a text-to-speech engine, so:
- Keep answers short and conversational: one to three sentences unless asked for detail.
- Never use markdown, bullet points, tables, code blocks, emojis or URLs.
- Write numbers and units the way they should be spoken.
Use web search whenever the question depends on current information such as news, \
weather, sports scores or prices."""


class Brain:
    def __init__(self):
        # Reads ANTHROPIC_API_KEY (or an `ant auth login` profile) from the environment.
        self.client = anthropic.Anthropic()
        self.history = []

    def reset(self):
        self.history = []

    def think(self, user_text: str) -> str:
        now = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
        self.history.append(
            {"role": "user", "content": f"[Local time: {now}]\n{user_text}"}
        )

        try:
            # Server tools like web search may pause a long turn; resume until done.
            for _ in range(5):
                response = self.client.beta.messages.create(
                    model=MODEL,
                    max_tokens=16000,
                    system=SYSTEM_PROMPT,
                    messages=self.history,
                    tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}],
                    output_config={"effort": "low"},  # fast replies suit a voice assistant
                    betas=["server-side-fallback-2026-07-01"],
                    fallbacks="default",
                )
                self.history.append({"role": "assistant", "content": response.content})
                if response.stop_reason != "pause_turn":
                    break
        except (anthropic.AuthenticationError, TypeError):  # TypeError: no key configured
            self.history.pop()
            return "I can't reach my brain, sir. Please check your Anthropic API key."
        except anthropic.RateLimitError:
            self.history.pop()
            return "I'm being rate limited, sir. Give me a moment and try again."
        except anthropic.APIConnectionError:
            self.history.pop()
            return "I can't connect to the internet right now, sir."
        except anthropic.APIStatusError as e:
            self.history.pop()
            return f"Something went wrong on the server, sir. Error {e.status_code}."

        if response.stop_reason == "refusal":
            return "I'm afraid I can't help with that one, sir."

        text = " ".join(b.text for b in response.content if b.type == "text").strip()
        return text or "I'm not sure what to say to that, sir."
