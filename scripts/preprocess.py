import os
import json
import pandas as pd

# -----------------------------
# PATHS
# -----------------------------
RAW_INTENTS_PATH = "data/raw/intents.json"
RAW_FAQ_PATH = "data/raw/Ecommerce_FAQ_Chatbot_dataset.json"
PROCESSED_INTENTS_PATH = "data/intents.json"
PROCESSED_FAQ_PATH = "data/faqs.json"

os.makedirs("data", exist_ok=True)

# -----------------------------
# ✅ PART 1: INTENTS CLEANING
# -----------------------------
if os.path.exists(RAW_INTENTS_PATH):
    with open(RAW_INTENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "intents" not in data:
        if isinstance(data, dict) and "tag" in data:
            data = {"intents": [data]}
        elif isinstance(data, list):
            data = {"intents": data}
        else:
            raise ValueError("❌ Invalid format for intents file.")

    cleaned_intents = []
    for intent in data["intents"]:
        tag = intent.get("tag", "").strip().lower()
        patterns = list({p.strip() for p in intent.get("patterns", []) if p.strip()})
        responses = list({r.strip() for r in intent.get("responses", []) if r.strip()})
        context_set = intent.get("context_set", "").strip()

        if not tag or not patterns or not responses:
            print(f"⚠️ Skipping invalid intent: {intent}")
            continue

        cleaned_intents.append({
            "tag": tag,
            "patterns": patterns,
            "responses": responses,
            "context_set": context_set
        })

    with open(PROCESSED_INTENTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"intents": cleaned_intents}, f, indent=4, ensure_ascii=False)

    print(f"✅ Cleaned intents saved to {PROCESSED_INTENTS_PATH}")
    print(f"Total intents processed: {len(cleaned_intents)}")

else:
    print(f"⚠️ No intents dataset found at {RAW_INTENTS_PATH}")

# -----------------------------
# ✅ PART 2: FAQ CLEANING
# -----------------------------
if os.path.exists(RAW_FAQ_PATH):
    with open(RAW_FAQ_PATH, "r", encoding="utf-8") as f:
        faq_raw = json.load(f)

    # handle "questions" key wrapper
    if isinstance(faq_raw, dict) and "questions" in faq_raw:
        faq_data = faq_raw["questions"]
    elif isinstance(faq_raw, list):
        faq_data = faq_raw
    else:
        raise ValueError("❌ Invalid FAQ format. Must be a list or dict with 'questions' key.")

    cleaned_faqs = []
    seen = set()
    for faq in faq_data:
        q = faq.get("question", "").strip()
        a = faq.get("answer", "").strip()
        if not q or not a or q.lower() in seen:
            continue
        seen.add(q.lower())
        cleaned_faqs.append({"question": q, "answer": a})

    with open(PROCESSED_FAQ_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_faqs, f, indent=4, ensure_ascii=False)

    print(f"✅ Cleaned FAQs saved to {PROCESSED_FAQ_PATH}")
    print(f"Total FAQs processed: {len(cleaned_faqs)}")

else:
    print(f"⚠️ No FAQ dataset found at {RAW_FAQ_PATH}")
