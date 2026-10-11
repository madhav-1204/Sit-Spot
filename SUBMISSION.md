# Dev.to Submission Draft

> Copy and paste this directly into Dev.to for the **Hacktoberfest 2026 Week 1 Challenge ("Touch Grass")**.

---

```markdown
---
title: "Sit Spot: A local-first journal where the screen is the shortest part of the experience"
published: true
tags: hacktoberfest, opensource, ai, python
canonical_url: false
cover_image: 
---

*This project is a submission for the Hacktoberfest 2026 Week 1 Dev Challenge: Touch Grass.*

## What I Built

Most nature apps try to keep you looking at your screen: identification cameras, gamified streaks, achievement badges, and animated timers. 

For the "Touch Grass" challenge, I wanted the exact opposite: **Sit Spot** is a local-first, offline journal designed for short (5, 10, or 20 minute) sit-outside sessions. The screen is deliberately the shortest part of the whole experience.

Here is how the session works:
1. **Before you go out**: A small open-weight model (`gemma3:1b` running locally via Ollama) gives you **one** short prompt (under 25 words) grounded in the current time of day and season.
2. **Outside**: The screen displays your prompt and a calm notice: *"phone away"*. There is no animated countdown ring and no notifications. Just one button: *"I'm back"*.
3. **When you return**: A plain textarea for rough notes. 2 to 5 lines is plenty. Typos don't matter.
4. **Tidying up**: The local model rewrites your rough notes into a concise, 3-to-4 sentence first-person journal entry using **only** facts present in your notes (no hallucinated weather or floral adjectives), plus one follow-up question for your next visit. You can edit either side, save both, or keep your raw notes only.
5. **Looking back**: The journal tracks your approximate time outside versus screen time, and lets you ask the model: *"What keeps showing up?"* to summarize recurring patterns while citing exact entry dates.

Everything runs on your laptop. No cloud LLM APIs, no API keys, and no telemetry. If Ollama is turned off, the app still works completely offline with curated fallback prompts and standard SQLite persistence.

---

## The Tech Stack

- **Python 3.11** + **Flask**: Server-rendered Jinja2 templates, no JavaScript framework, no build steps.
- **SQLite** (`sqlite3` stdlib): Local file storage for entries, durations, and screen-time tracking.
- **Local AI**: `gemma3:1b` (806 MB, Q4_K_M) running through Ollama at `http://localhost:11434`.
- **CSS**: A single, hand-crafted stylesheet using system fonts, a calm forest-green accent, and zero external CDNs or icon sets. Readable down to 375px mobile viewports.

---

## What Happened During Development

Building with a compact 1B parameter model locally is an honest exercise in constraint design:

1. **Initial Hallucinations**:
   During our initial test run, when given raw notes like `"Spider web between two lilac twigs with water drops on it. A wasp walked on the dry wood rail"`, the 1B model added unmentioned sensory details: *"The dry wood surface felt cool beneath my fingertips"* and asked *"What color were the lilac flowers?"* (the notes only mentioned twigs!).
   
   *The fix:* We added a few-shot example and strict negative constraints in `prompts/tidy_entry.txt` explicitly instructing the model to never invent unmentioned feelings or objects.

2. **The "I stopped the rain" bug**:
   In another test note (`"Rain stopped about 10 minutes ago. Earth smells damp"`), the model took the first-person instruction too literally and wrote: *"I stopped the rain about ten minutes ago."* We had to add a rule: *"NEVER attribute natural events to the observer."*

3. **Graceful Offline Degradation**:
   If Ollama is stopped, the application catches the connection error cleanly, shows an offline notice, and lets you save your raw notes directly to SQLite without losing your session.

---

## How to Run It

```bash
# 1. Clone repo
git clone https://github.com/<your-username>/sit-spot.git
cd sit-spot

# 2. Install dependencies (only Flask and requests)
pip install -r requirements.txt

# 3. Pull the local Gemma model
ollama pull gemma3:1b

# 4. Run the app
python app.py
```

Then visit `http://127.0.0.1:5000`.

---

## Source Code

- GitHub Repository: [https://github.com/<your-username>/sit-spot](https://github.com/<your-username>/sit-spot)
- License: MIT
```
