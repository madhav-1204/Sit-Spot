import sys
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

import db
import ollama_client

app = Flask(__name__)
app.secret_key = "sit-spot-local-dev-key"

@app.context_processor
def inject_model_name():
    return {"sitspot_model": ollama_client.get_model_name()}

def get_time_of_day():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 20:
        return "evening"
    else:
        return "night"

def get_current_month():
    return datetime.now().strftime("%B")

@app.route("/")
def home():
    count = db.get_entry_count()
    last_entry = db.get_last_entry()
    return render_template("home.html", count=count, last_entry=last_entry)

@app.route("/start", methods=["POST"])
def start_session():
    screen_t0 = time.time()
    custom_duration = request.form.get("custom_duration", "").strip()
    if custom_duration:
        try:
            target_minutes = int(custom_duration)
        except ValueError:
            target_minutes = 10
    else:
        try:
            target_minutes = int(request.form.get("duration", 10))
        except ValueError:
            target_minutes = 10

    if target_minutes <= 0:
        target_minutes = 10

    time_of_day = get_time_of_day()
    month = get_current_month()
    
    recent = db.get_recent_entries(3)
    recent_notes = " ; ".join([r.get("raw_notes", "") for r in recent if r.get("raw_notes")])

    prompt, used_ai, error_message = ollama_client.generate_session_prompt(
        time_of_day=time_of_day,
        month=month,
        last_notes=recent_notes
    )

    prompt_screen_seconds = int(time.time() - screen_t0)
    start_timestamp = time.time()
    start_time_display = datetime.now().strftime("%I:%M %p").lstrip("0")

    return render_template(
        "out.html",
        prompt=prompt,
        target_minutes=target_minutes,
        start_timestamp=start_timestamp,
        start_time_display=start_time_display,
        prompt_screen_seconds=prompt_screen_seconds,
        error_message=error_message
    )

@app.route("/back", methods=["POST"])
def back_session():
    start_timestamp = float(request.form.get("start_timestamp", time.time()))
    prompt = request.form.get("prompt", "")
    target_minutes = int(request.form.get("target_minutes", 10))
    prompt_screen_seconds = int(request.form.get("prompt_screen_seconds", 0))

    outside_seconds = max(1, int(time.time() - start_timestamp))
    outside_minutes = max(1, outside_seconds // 60)
    notes_start_timestamp = time.time()

    return render_template(
        "notes.html",
        target_minutes=target_minutes,
        prompt=prompt,
        outside_seconds=outside_seconds,
        outside_minutes=outside_minutes,
        prompt_screen_seconds=prompt_screen_seconds,
        notes_start_timestamp=notes_start_timestamp
    )

@app.route("/tidy", methods=["POST"])
def tidy_view():
    raw_notes = request.form.get("raw_notes", "").strip()
    action = request.form.get("action", "tidy")
    target_minutes = int(request.form.get("target_minutes", 10))
    prompt = request.form.get("prompt", "")
    outside_seconds = int(request.form.get("outside_seconds", 0))
    prompt_screen_seconds = int(request.form.get("prompt_screen_seconds", 0))
    notes_start = float(request.form.get("notes_start_timestamp", time.time()))

    notes_screen_seconds = int(time.time() - notes_start)
    screen_seconds = prompt_screen_seconds + notes_screen_seconds

    if action == "save_raw":
        db.save_entry(
            target_minutes=target_minutes,
            outside_seconds=outside_seconds,
            screen_seconds=screen_seconds,
            prompt=prompt,
            raw_notes=raw_notes,
            is_raw_only=1
        )
        flash("Entry saved.")
        return redirect(url_for("entries"))

    # Action is tidy
    tidy_entry, follow_up, used_ai, error_message = ollama_client.tidy_notes(raw_notes)

    return render_template(
        "tidy.html",
        target_minutes=target_minutes,
        prompt=prompt,
        outside_seconds=outside_seconds,
        screen_seconds=screen_seconds,
        raw_notes=raw_notes,
        tidy_entry=tidy_entry or raw_notes,
        follow_up=follow_up,
        error_message=error_message
    )

@app.route("/save", methods=["POST"])
def save_final_entry():
    action = request.form.get("action", "save_both")
    target_minutes = int(request.form.get("target_minutes", 10))
    outside_seconds = int(request.form.get("outside_seconds", 0))
    screen_seconds = int(request.form.get("screen_seconds", 0))
    prompt = request.form.get("prompt", "")
    raw_notes = request.form.get("raw_notes", "").strip()
    tidy_entry = request.form.get("tidy_entry", "").strip()
    follow_up = request.form.get("follow_up", "").strip()

    is_raw_only = 1 if action == "save_raw_only" else 0

    db.save_entry(
        target_minutes=target_minutes,
        outside_seconds=outside_seconds,
        screen_seconds=screen_seconds,
        prompt=prompt,
        raw_notes=raw_notes,
        tidy_entry=tidy_entry if not is_raw_only else None,
        follow_up=follow_up if not is_raw_only else None,
        is_raw_only=is_raw_only
    )

    flash("Entry saved.")
    return redirect(url_for("entries"))

@app.route("/entries")
def entries():
    all_entries = db.get_all_entries()
    return render_template("entries.html", entries=all_entries)

@app.route("/look-back", methods=["POST"])
def look_back():
    recent = db.get_recent_entries(10)
    summary, used_ai, error_message = ollama_client.summarize_patterns(recent)
    all_entries = db.get_all_entries()
    
    if error_message:
        flash(error_message)

    return render_template("entries.html", entries=all_entries, summary=summary)

def load_demo_data():
    if db.get_entry_count() == 0:
        db.save_entry(
            target_minutes=10,
            outside_seconds=640,
            screen_seconds=75,
            prompt="Find the nearest shadow. Notice how far it moves before you stand up.",
            raw_notes="Shadow of the birch moved about two inches across the wooden railing. Breeze from east. Two crows flew overhead making low clicks.",
            tidy_entry="I watched the shadow of the birch tree move roughly two inches across the wooden deck railing. A cool breeze came from the east while two crows flew overhead making low clicking sounds.",
            follow_up="Did the crows return to the same tree?",
            is_raw_only=0
        )
        db.save_entry(
            target_minutes=5,
            outside_seconds=320,
            screen_seconds=45,
            prompt="Count the different bird sounds before you count anything else.",
            raw_notes="Damp morning. Heard a chickadee whistled call, then high chirps in the hedge. Wet cedar smell.",
            tidy_entry="I sat in the damp morning air and listened to a chickadee whistle, followed by high chirps coming from the hedge. The cedar nearby smelled strongly of rain.",
            follow_up="Could you see where the chickadee was perched?",
            is_raw_only=0
        )

if __name__ == "__main__":
    db.init_db()
    if "--demo" in sys.argv:
        load_demo_data()
    print(f"Sit Spot running at http://127.0.0.1:5000 (Model: {ollama_client.get_model_name()})")
    app.run(host="127.0.0.1", port=5000, debug=False)
