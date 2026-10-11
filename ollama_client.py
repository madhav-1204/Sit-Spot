import os
import random
import requests

OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("SITSPOT_MODEL", "gemma3:1b")
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")
TIMEOUT_SECONDS = 60

def get_model_name():
    return os.environ.get("SITSPOT_MODEL", DEFAULT_MODEL)

def is_ollama_available():
    try:
        res = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return res.status_code == 200
    except Exception:
        return False

def get_installed_models():
    try:
        res = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if res.status_code == 200:
            data = res.json()
            return [m.get("name") for m in data.get("models", [])]
    except Exception:
        pass
    return []

def load_prompt_file(filename):
    filepath = os.path.join(PROMPTS_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def get_fallback_prompt():
    fallback_text = load_prompt_file("fallback.txt")
    lines = [line.strip() for line in fallback_text.splitlines() if line.strip()]
    if lines:
        return random.choice(lines)
    return "Face east if you can. Count the different bird sounds before you count anything else."

def query_ollama(prompt, temperature=0.8):
    model = get_model_name()
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
    if response.status_code == 404:
        raise ValueError(f"Model '{model}' is not pulled in Ollama. Pull it with: ollama pull {model}")
    if response.status_code != 200:
        err_msg = ""
        try:
            err_msg = response.json().get("error", response.text)
        except Exception:
            err_msg = response.text
        raise RuntimeError(f"Ollama returned error ({response.status_code}): {err_msg}")

    data = response.json()
    return data.get("response", "").strip()

def generate_session_prompt(time_of_day, month, last_notes="None yet"):
    template = load_prompt_file("session_prompt.txt")
    formatted_prompt = template.format(
        time_of_day=time_of_day,
        month=month,
        last_notes=last_notes if last_notes else "First session. No previous notes."
    )
    try:
        result = query_ollama(formatted_prompt, temperature=0.8)
        if result:
            cleaned = result.strip('"').strip("'").strip()
            return cleaned, True, None
    except requests.exceptions.ConnectionError:
        return get_fallback_prompt(), False, "Ollama is not running. Using an offline fallback prompt."
    except requests.exceptions.Timeout:
        return get_fallback_prompt(), False, "Model request timed out after 60 seconds. Using an offline fallback prompt."
    except ValueError as e:
        return get_fallback_prompt(), False, f"{str(e)} Using offline fallback prompt."
    except Exception as e:
        return get_fallback_prompt(), False, f"Model call failed ({str(e)}). Using offline fallback prompt."

    return get_fallback_prompt(), False, "Model returned an empty response. Using an offline fallback prompt."

def tidy_notes(raw_notes):
    template = load_prompt_file("tidy_entry.txt")
    formatted_prompt = template.format(raw_notes=raw_notes)
    try:
        result = query_ollama(formatted_prompt, temperature=0.3)
        if result:
            lines = result.splitlines()
            body_lines = []
            follow_up = None
            for line in lines:
                if line.strip().lower().startswith("next time:"):
                    follow_up = line.strip()[10:].strip()
                elif line.strip():
                    body_lines.append(line.strip())
            tidy_text = " ".join(body_lines)
            return tidy_text, follow_up, True, None
    except requests.exceptions.ConnectionError:
        return None, None, False, "Ollama is not running. Showing raw notes only."
    except requests.exceptions.Timeout:
        return None, None, False, "Model timed out after 60 seconds. Showing raw notes only."
    except ValueError as e:
        return None, None, False, f"{str(e)}. Showing raw notes only."
    except Exception as e:
        return None, None, False, f"Model call failed ({str(e)}). Showing raw notes only."

    return None, None, False, "Model returned an empty response."

def summarize_patterns(entries):
    template = load_prompt_file("look_back.txt")
    formatted_entries = []
    for e in entries:
        date_str = e["created_at"][:10] if e.get("created_at") else "Unknown date"
        text = e.get("tidy_entry") or e.get("raw_notes") or ""
        formatted_entries.append(f"[{date_str}]: {text}")
    
    entries_block = "\n".join(formatted_entries)
    prompt = template.format(entries_text=entries_block)
    try:
        result = query_ollama(prompt, temperature=0.3)
        if result:
            return result, True, None
    except requests.exceptions.ConnectionError:
        return None, False, "Ollama is not running. Cannot summarize patterns offline."
    except requests.exceptions.Timeout:
        return None, False, "Summary timed out after 60 seconds."
    except ValueError as e:
        return None, False, f"{str(e)}."
    except Exception as e:
        return None, False, f"Summary call failed ({str(e)})."

    return None, False, "Empty response from model."
