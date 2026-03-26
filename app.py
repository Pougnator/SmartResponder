"""SmartResponder phone-call assistant (France-ready telephony setup).

This app demonstrates a simple call flow:
1) Greet caller with: "Hello, this is Artem"
2) Listen to caller response (speech-to-text handled by Twilio)
3) Generate an AI answer from the transcript and speak it back.

Provider choice in this starter: Twilio Programmable Voice.
- Twilio can provision numbers in many countries (including France inventory when available)
- Twilio also supports porting existing numbers in supported regions
- You connect using webhooks + API

For production low-latency full duplex voice, use Twilio Media Streams + a realtime model.
This sample stays intentionally beginner-friendly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from flask import Flask, Response, request
from openai import OpenAI
from twilio.twiml.voice_response import Gather, VoiceResponse


load_dotenv()


@dataclass
class Settings:
    """App settings loaded from environment variables."""

    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"

    @classmethod
    def from_env(cls) -> "Settings":
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not key:
            raise ValueError(
                "OPENAI_API_KEY is missing. Add it to your .env file before starting the app."
            )

        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
        return cls(openai_api_key=key, openai_model=model)


def create_openai_client(settings: Settings) -> OpenAI:
    """Create and return an OpenAI client instance."""

    return OpenAI(api_key=settings.openai_api_key)


def generate_reply(client: OpenAI, model: str, caller_text: str) -> str:
    """Generate a short voice-friendly answer from caller text."""

    safe_text = (caller_text or "").strip()
    if not safe_text:
        return "I did not hear anything clearly. Could you repeat that, please?"

    prompt = (
        "You are a polite French-market phone assistant. "
        "Answer in the same language as the caller when possible. "
        "Keep the answer short and natural for voice (max 2 sentences)."
    )

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": safe_text},
        ],
        max_output_tokens=120,
    )

    text = (response.output_text or "").strip()
    return text or "Thank you for your message. Could you tell me a bit more?"


def create_app() -> Flask:
    """Flask application factory."""

    settings = Settings.from_env()
    client = create_openai_client(settings)

    app = Flask(__name__)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/voice")
    def voice() -> Response:
        """Step 1 + 2: greet and gather caller speech."""

        twiml = VoiceResponse()
        twiml.say("Hello, this is Artem", voice="alice", language="en-US")

        gather = Gather(
            input="speech",
            action="/process",
            method="POST",
            speech_timeout="auto",
            language="fr-FR",
        )
        gather.say(
            "Je vous écoute. Dites-moi comment je peux vous aider.",
            voice="alice",
            language="fr-FR",
        )
        twiml.append(gather)

        # Fallback if no speech detected.
        twiml.say(
            "Je n'ai rien entendu. Merci de rappeler.",
            voice="alice",
            language="fr-FR",
        )
        twiml.hangup()
        return Response(str(twiml), mimetype="application/xml")

    @app.post("/process")
    def process_speech() -> Response:
        """Step 3: read transcript, ask LLM, then speak answer."""

        transcript = request.form.get("SpeechResult", "")
        answer = generate_reply(client=client, model=settings.openai_model, caller_text=transcript)

        twiml = VoiceResponse()
        twiml.say(answer, voice="alice", language="fr-FR")
        twiml.pause(length=1)
        twiml.say("Merci pour votre appel. Au revoir.", voice="alice", language="fr-FR")
        twiml.hangup()

        return Response(str(twiml), mimetype="application/xml")

    @app.post("/test-pipeline")
    def test_pipeline() -> dict[str, str]:
        """Optional local test endpoint for quick validation without real calls."""

        sample_text = request.form.get("text", "Bonjour, pouvez-vous me rappeler demain matin ?")
        reply = generate_reply(client=client, model=settings.openai_model, caller_text=sample_text)
        return {
            "step_1": "Hello, this is Artem",
            "step_2": sample_text,
            "step_3": reply,
        }

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=8000, debug=True)
