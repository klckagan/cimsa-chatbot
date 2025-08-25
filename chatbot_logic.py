
import json
import random
import re
from datetime import datetime
from pathlib import Path

from fuzzywuzzy import process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


FAQ_FILE = Path("faq.json")
LOG_FILE = Path("talep_log.txt")


CONFIDENT_THRESHOLD = 0.60         
LOW_PRIORITY_TAGS = {              
    "cimsa_ceo", "cimsa_misyon_vizyon", "cimsa_tarihce",
    "cimsa_surdurulebilirlik", "sabanci_gecmisi", "cimsa_web"
}


SUGGEST_MIN = 50                   
SUGGEST_MAX = 85                   
HARD_MATCH  = 85                   


awaiting_request = False           
ask_request = ""                   


_TR_MAP = str.maketrans({
    "İ": "I", "I": "I", "ı": "i", "Ş": "S", "ş": "s",
    "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O",
    "ö": "o", "Ç": "C", "ç": "c"
})
def _normalize(s: str) -> str:
    s = (s or "").strip()
    s = s.translate(_TR_MAP).lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _log(event: str, text: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event}: {text}\n")
    except Exception:
        pass  


with open(FAQ_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

intents = data.get("intents", [])


all_patterns  = []  
norm_patterns = []  
for intent in intents:
    for p in intent.get("patterns", []):
        all_patterns.append((p, intent["tag"]))
        norm_patterns.append((_normalize(p), intent["tag"]))


ROUTE_RULES = [
    (re.compile(r"\b(sap(\s+gui|\s+login)?|sapgui)\b", re.I), "sap"),

    (re.compile(r"\b(outlook|e[- ]?posta|mail|parola|s(i|ı)fre)\b", re.I), "outlook_password"),

    (re.compile(r"\b(yaz(i|ı)c(i|ı)|printer|c(i|ı)kt(i|ı)|offline)\b", re.I), "printer"),

    (re.compile(r"\b(onedrive|senkron)\b", re.I), "onedrive"),

    (re.compile(r"\b(teams|mikrofon|kamera|toplant(i|ı))\b", re.I), "teams"),

    (re.compile(r"\b(vpn)\b", re.I), "vpn"),

    (re.compile(r"\b(ceo|genel m(ü|u)d(ü|u)r)\b", re.I), "cimsa_ceo"),
    
    (re.compile(r"(bilgi (i|ı)sl(e|e)m|bilgi teknoloji|(^|\b)bt($|\b)|(^|\b)it($|\b)).*(nerede|yeri)", re.I), "cimsa_it_department"),
]

_X, _y = [], []
for intent in intents:
    for p in intent.get("patterns", []):
        _X.append(_normalize(p))
        _y.append(intent["tag"])

_nlu_ready = False
_vectorizer = None
_clf = None

if len(set(_y)) >= 2 and len(_X) >= 5:
    _vectorizer = TfidfVectorizer(
        lowercase=False,          
        ngram_range=(1, 2),
        max_features=5000
    )
    X_vec = _vectorizer.fit_transform(_X)
    _clf = LogisticRegression(max_iter=1000)
    _clf.fit(X_vec, _y)
    _nlu_ready = True

def _predict_intent_nlu(norm_text: str):
    if not _nlu_ready:
        return None, 0.0
    vec  = _vectorizer.transform([norm_text])
    tag  = _clf.predict(vec)[0]
    conf = float(_clf.predict_proba(vec).max())
    return tag, conf

def _get_intent_by_tag(tag: str):
    for it in intents:
        if it.get("tag") == tag:
            return it
    return None

def _responses_for_tag(tag: str):
    it = _get_intent_by_tag(tag)
    if not it:
        return ["Bu konuda bilgim yok."]
    return it.get("responses", ["Bu konuda bilgim yok."])

def _fuzzy_best_match(norm_user_text: str):
    if not norm_patterns:
        return None, 0
    choices = [t for (t, _tag) in norm_patterns]
    matches = process.extract(norm_user_text, choices, limit=3)
    return matches, (matches[0][1] if matches else 0)


def get_bot_response(kullanici_sorusu: str):
    global awaiting_request, ask_request

    _log("USER", str(kullanici_sorusu))

    text_orig = (kullanici_sorusu or "").strip()
    text_norm = _normalize(text_orig)

    for rx, forced_tag in ROUTE_RULES:
        if rx.search(text_orig) or rx.search(text_norm):
            bot = random.choice(_responses_for_tag(forced_tag))
            if "talebinizi buraya yazın" in bot.lower() or "talep" in forced_tag.lower():
                awaiting_request = True
                ask_request = forced_tag
            _log("BOT", f"[RULE->{forced_tag}] {bot}")
            return bot

    if awaiting_request:
        if text_norm in ("hayir", "iptal", "vazgec", "yok"):
            awaiting_request = False
            ask_request = ""
            bot = "👍 Tamamdır, başka bir konuda yardımcı olabilir miyim?"
            _log("BOT", bot)
            return bot

        awaiting_request = False
        ask_request = ""
        bot = "✅ Teşekkürler, talebiniz kaydedildi ve ilgili ekibe iletilecek."
        _log("BOT", bot)
        return bot

    if text_orig.startswith("__ATTACH__::"):
        bot = "📎 Eki aldım. Gerekirse detayları soracağım."
        _log("BOT", bot)
        return bot

    if not text_norm:
        bot = random.choice([
            "❓ Tam anlayamadım. Sorununuzu biraz daha farklı bir şekilde yazabilir misiniz?",
            "🤔 Sanırım tam anlayamadım, lütfen sorunuzu biraz daha açık yazar mısınız?",
            "🙇 Bu konuda emin değilim. Daha net ifade edebilir misiniz?",
            "😕 Tam kavrayamadım. Biraz daha detay verebilir misiniz?",
            "📝 Rica etsem sorununuzu yeniden açıklayabilir misiniz?"
        ])
        _log("BOT", bot)
        return bot

    intent_tag, conf = _predict_intent_nlu(text_norm)
    if intent_tag:
        min_conf = 0.75 if intent_tag in LOW_PRIORITY_TAGS else CONFIDENT_THRESHOLD
        if conf >= min_conf:
            bot = random.choice(_responses_for_tag(intent_tag))
            if "talebinizi buraya yazın" in bot.lower() or "talep" in intent_tag.lower():
                awaiting_request = True
                ask_request = intent_tag
            _log("BOT", f"[NLU {conf:.2f}->{intent_tag}] {bot}")
            return bot

    matches, top_score = _fuzzy_best_match(text_norm)
    if matches and top_score > HARD_MATCH:
        best_norm = matches[0][0]
        chosen_tag = next((tag for (txt, tag) in norm_patterns if txt == best_norm), None)
        if chosen_tag:
            bot = random.choice(_responses_for_tag(chosen_tag))
            if "talebinizi buraya yazın" in bot.lower() or "talep" in chosen_tag.lower():
                awaiting_request = True
                ask_request = chosen_tag
            _log("BOT", f"[FUZZY {top_score}->{chosen_tag}] {bot}")
            return bot

    if matches and SUGGEST_MIN <= top_score <= SUGGEST_MAX:
        suggestions_norm = [m[0] for m in matches if isinstance(m, tuple)]
        seen, unique = set(), []
        for s in suggestions_norm:
            if s not in seen:
                unique.append(s); seen.add(s)
        if unique:
            bot = "SUGGEST|" + "|".join(unique[:3])
            _log("BOT", bot)
            return bot

    bot = random.choice([
        "❓ Tam anlayamadım. Sorununuzu biraz daha farklı bir şekilde yazabilir misiniz?",
        "🤔 Sanırım tam anlayamadım, lütfen sorunuzu biraz daha açık yazar mısınız?",
        "🙇 Bu konuda emin değilim. Daha net ifade edebilir misiniz?",
        "😕 Tam kavrayamadım. Biraz daha detay verebilir misiniz?",
        "📝 Rica etsem sorununuzu yeniden açıklayabilir misiniz?"
    ])
    _log("BOT", bot)
    return bot
