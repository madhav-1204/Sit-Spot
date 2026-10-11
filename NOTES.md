# Dev Log: Sit Spot

## 2026-10-11
- Initialized new Git repository for Hacktoberfest 2026 Week 1 Challenge ("Touch Grass").
- Checked system environment for Ollama: local Ollama HTTP daemon detected at http://localhost:11434 with empty model list (`{"models":[]}`).
- Encountered 404 from `/api/generate` when model `gemma3:1b` is not yet downloaded. Handled explicitly in `ollama_client.py` to notify the user with exact pull instructions while gracefully falling back to `prompts/fallback.txt` for prompts and preserving authentic raw notes.
- Tech stack: Python 3.11 + standard library `sqlite3` + Flask 3.1 + `requests`. Minimal 2-package dependency footprint.
- Frontend architecture: Server-rendered Jinja2 templates, zero external CDNs, zero JS framework, system font stack, single centered column (max-width 40rem), readable down to 375px mobile width.
- Core workflows implemented:
  - Home: session counter, last visit date, duration selection (5, 10, 20m), "Go outside" button.
  - Out: "phone away" screen, prompt display, start timestamp, "I'm back" button.
  - Back: rough notes textarea, outside minutes calculation.
  - Tidy: side-by-side editable raw and tidy notes, follow-up reflection question, screen vs outside time metrics, save / discard options.
  - Look Back: past entries list, "What keeps showing up" pattern summary citing exact entry dates.
- Automated testing: built test suites in `tests/` covering database persistence, graceful fallback, and all user flow routes. 10/10 tests passed.
