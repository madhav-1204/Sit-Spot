# Sit Spot

A local-first journal for short sit-outside sessions. An open-weight Gemma model running locally through Ollama gives you one brief prompt before you step outside, and tidies your rough notes when you return.

Built during **Hacktoberfest Week 1 (Oct 5–11, 2026)** for the *"Touch Grass"* challenge. The screen is designed to be the shortest part of the experience.

---

## Setup in 4 Commands

```bash
git clone https://github.com/madhav-1204/Sit-Spot.git
cd sit-spot
pip install -r requirements.txt
python app.py
```

Then open your browser to [http://127.0.0.1:5000](http://127.0.0.1:5000).

*(To populate sample entries for demonstration, run: `python app.py --demo`)*

---

## Local AI Model Configuration

Sit Spot uses an open-weight model running entirely on your local machine via [Ollama](https://ollama.ai). No cloud APIs, no tracking, and no internet access required at runtime.

1. Install Ollama from [ollama.ai](https://ollama.ai).
2. Pull the default Gemma model:
   ```bash
   ollama pull gemma3:1b
   ```
   *(Or use `gemma3:4b` / `gemma2:2b` by setting the environment variable `SITSPOT_MODEL`)*.
3. If Ollama is offline or not installed, Sit Spot functions completely offline using curated fallback prompts and preserves your raw notes without interruption.

---

## How It Works

1. **Home**: Choose 5, 10, or 20 minutes. See past session count and the date of your last visit.
2. **Out Screen**: Displays ONE calm instruction (maximum 25 words) grounded in the time of day, month, and prior notes. Reminds you: *phone away*. Displays the start time and a single button: *I'm back*. No animated timers, rings, or notifications.
3. **Notes**: A plain textarea for rough thoughts (2 to 5 lines). Typos and incomplete sentences are welcome.
4. **Tidy**: The local Gemma model rewrites the rough notes into a 3–4 sentence first-person journal entry using **only** facts present in your notes (no hallucinated birds, weather, or floral filler words), plus one follow-up question for your next visit. You can edit either side, save both, or keep raw notes only.
5. **Entries**: Inspect past sessions. Shows exact minutes spent outside versus approximate minutes spent looking at the screen. Use the *"What keeps showing up"* button to ask the model to analyze recurring patterns across recent visits, citing specific dates for every observation.

---

## Honest Limitations

- **Small Model Nuance**: Running a compact 1B/4B parameter model locally means prompt adherence relies on strict prompt formatting. On rare occasions with very short notes (e.g. 1-2 words), the model may output minimal rewrites.
- **Offline Fallback**: When Ollama is stopped or unavailable, the AI tidying step is gracefully bypassed, saving your authentic raw notes directly to SQLite without data loss.
- **Hardware Requirement**: First-time token generation depends on your laptop's CPU/GPU capabilities. If a local model call exceeds 60 seconds, it safely times out.

---

## Credits & Dependencies

- **Framework**: Flask (Jinja2) for clean, server-rendered HTML.
- **Storage**: Python standard library `sqlite3` (no ORM or heavy database engines).
- **HTTP**: `requests` for talking to localhost:11434.
- **Model**: Gemma open-weights by Google DeepMind running via Ollama.
- **Design**: Hand-crafted CSS using system font stacks, zero external CDNs, zero JavaScript frameworks, and zero web fonts.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
