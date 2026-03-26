# SmartResponder

An app that responds to phone calls using AI.

## Recommended call-handling tool for France

Use **Twilio Programmable Voice** for this use case.

Why this is a good fit:
- You can buy a French number when inventory is available.
- You can often port your existing number to Twilio in supported scenarios.
- You get webhook + API control for call flows.
- It works well with AI backends for speech understanding and generated replies.

## What this starter does

The Python app implements your 3 requested test steps:
1. Says: **"Hello, this is Artem"**
2. Listens to the caller's spoken response
3. Sends the transcript to an LLM and speaks back the generated answer

## Project files

- `app.py` — Flask server + Twilio voice webhooks + LLM integration
- `requirements.txt` — Python dependencies
- `.env.example` — environment variable template

## Quick start

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment

```bash
cp .env.example .env
# then edit .env with your real keys
```

### 3) Run the server

```bash
python app.py
```

### 4) Expose local server to Twilio (for development)

Use ngrok (or Cloudflare Tunnel):

```bash
ngrok http 8000
```

Copy your HTTPS URL (example: `https://abc123.ngrok-free.app`).

### 5) Configure your Twilio number webhook

In Twilio Console for your phone number:
- **A CALL COMES IN** → Webhook URL: `https://<your-url>/voice`
- Method: `POST`

Now call your Twilio number and test.

## Endpoints

- `POST /voice` — greeting + speech capture
- `POST /process` — transcript -> LLM answer -> spoken reply
- `POST /test-pipeline` — quick non-telephony test of the 3-step logic
- `GET /health` — health check

## About "using your own voice"

This starter uses Twilio built-in TTS voice (`alice`).
If you want your own cloned voice, you typically add a dedicated voice-cloning/TTS provider and stream generated audio to the call.
For production low-latency "interruptible" conversations, consider Twilio Media Streams + a realtime AI stack.

## Is Twilio only a customer-service tool?

No. Twilio is a **communications API platform (CPaaS)**.

Twilio can do all of these:
- Receive and place **phone calls** (Programmable Voice)
- Receive and send **SMS** (Programmable Messaging)
- Route interactions to humans, bots, CRMs, or support tools

So you can use Twilio as the telephony layer for your personal AI phone assistant, not only for customer support centers.

## Secrets and security

- Put real credentials only in local `.env` (already gitignored in this repo).
- Keep `.env.example` with placeholders only.
- If a secret was ever shared in chat/email/screenshots, rotate it in Twilio Console immediately.
