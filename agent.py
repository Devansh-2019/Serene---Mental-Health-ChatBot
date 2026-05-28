# ============================================================
#  agent.py  —  AI Concept: Intelligent Agent (PEAS)
#
#  Gemini is called via plain HTTP requests — no SDK needed,
#  no version issues, works with any Python 3.x.
#
#  Flow:  Perceive → Update State → Plan (BDS) → Act (GA+API)
# ============================================================

import os
import json
import urllib.request
import urllib.error

from knowledge_base import KEYWORD_STATE_MAP, COPING_STRATEGIES, GOAL_STATE
from bidirectional_search import bidirectional_search, get_next_therapy_step
from genetic_algorithm import (evolve_prompt_strategy, build_system_prompt,
                                evolve_response)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _call_gemini(system_prompt: str, user_message: str,
                 conversation_history: list) -> str:
    """
    Call Groq API (free tier) — uses requests library.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        import requests
    except ImportError:
        print("[Serene] ❌ requests not installed — run: pip install requests")
        return None

    messages = [{"role": "system", "content": system_prompt}]
    recent = [m for m in conversation_history
              if m["role"] in ("user", "assistant") and m.get("content")][-10:]
    for m in recent[:-1]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       "llama-3.1-8b-instant",
                "messages":    messages,
                "max_tokens":  300,
                "temperature": 0.85,
            },
            timeout=15,
        )
        if not resp.ok:
            print(f"[Serene] ❌ Groq {resp.status_code}: {resp.text}")
            return None
        text = resp.json()["choices"][0]["message"]["content"]
        print("[Serene] ✅ Groq response received")
        return text.strip()
    except Exception as e:
        print(f"[Serene] ❌ Groq error: {type(e).__name__}: {e}")
        return None


VALID_STATES = {
    "suicidal","depressed","hopeless","sad","lonely","anxious",
    "stressed","tired","neutral","content","relaxed","okay",
    "calm","happy","peaceful","joyful"
}

def _classify_state(user_input: str, keyword_fallback: str) -> str | None:
    """
    Ask Groq to classify the emotional state from the message.
    Uses a tiny prompt — ~50 input tokens, ~5 output tokens.
    Returns None if API unavailable (keyword fallback is used instead).
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    # Crisis keywords always bypass AI classification for safety
    crisis_words = ["suicid","kill myself","want to die","end my life",
                    "self harm","dying","hurt myself"]
    if any(w in user_input.lower() for w in crisis_words):
        return "suicidal"

    try:
        import requests
        resp = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model":       "llama-3.1-8b-instant",
                "messages":    [
                    {"role": "system", "content":
                        "You are an emotion classifier. Given a message, reply with ONLY one word "
                        "from this exact list: suicidal, depressed, hopeless, sad, lonely, anxious, "
                        "stressed, tired, neutral, content, relaxed, okay, calm, happy, peaceful, joyful. "
                        "No explanation, no punctuation, just the single word."},
                    {"role": "user", "content": user_input},
                ],
                "max_tokens":  5,
                "temperature": 0.0,
            },
            timeout=8,
        )
        if resp.ok:
            state = resp.json()["choices"][0]["message"]["content"].strip().lower()
            if state in VALID_STATES:
                print(f"[Serene] 🧠 AI classified state: '{state}' (keyword said: '{keyword_fallback}')")
                return state
    except Exception as e:
        print(f"[Serene] ⚠ State classification failed: {e}")
    return None


# ══════════════════════════════════════════════════════════════
#  INTELLIGENT AGENT
# ══════════════════════════════════════════════════════════════

class MentalHealthAgent:
    """
    Goal-Based Intelligent Agent.

    PEAS:
      Performance : User's emotional progression toward 'calm'
      Environment : User text input + conversation history
      Actuators   : Therapeutic responses + coping tips
      Sensors     : Keyword extraction + sentiment detection
    """

    def __init__(self):
        self.conversation_history : list = []
        self.emotional_trajectory : list = []
        self.current_state        : str  = "neutral"
        self.session_goal         : str  = GOAL_STATE
        self.turn_count           : int  = 0

    # ── SENSOR ──────────────────────────────────────────────
    def perceive(self, user_input: str) -> dict:
        text = user_input.lower()

        PRIORITY = [
            "suicidal","depressed","hopeless","sad","lonely",
            "anxious","stressed","tired","neutral","content",
            "relaxed","okay","calm","happy","peaceful","joyful",
        ]

        # Keyword detection (always runs as base)
        keyword_state, found_kws, best = "neutral", [], 0
        for state in PRIORITY:
            kws     = KEYWORD_STATE_MAP.get(state, [])
            matches = [k for k in kws if k in text]
            score   = sum(len(k.split()) for k in matches)
            if score > best:
                best, keyword_state, found_kws = score, state, matches
            if state == "suicidal" and matches:
                keyword_state, found_kws = "suicidal", matches
                break

        # AI classification (runs when API key is set)
        # Overrides keyword result for better semantic understanding
        ai_state = _classify_state(user_input, keyword_state)
        detected = ai_state if ai_state else keyword_state

        pos = sum(1 for w in ["good","great","happy","better","calm","okay","fine"] if w in text)
        neg = sum(1 for w in ["bad","terrible","hate","hopeless","tired","sad","awful"] if w in text)
        sentiment = "positive" if pos > neg else ("negative" if neg > pos else "neutral")

        return {"raw_input": user_input, "detected_state": detected,
                "keywords_found": found_kws, "sentiment": sentiment,
                "used_ai_classification": ai_state is not None}

    # ── INTERNAL STATE ───────────────────────────────────────
    def update_state(self, percept: dict):
        self.current_state = percept["detected_state"]
        self.emotional_trajectory.append(self.current_state)
        self.conversation_history.append({
            "role":    "user",
            "content": percept["raw_input"],
            "state":   self.current_state,
        })
        self.turn_count += 1

    # ── PLAN (Bi-Directional Search) ─────────────────────────
    def plan(self) -> dict:
        return get_next_therapy_step(self.current_state, self.session_goal)

    # ── ACT (GA → Gemini API → fallback) ────────────────────
    def act(self, percept: dict, plan: dict) -> dict:
        bds = bidirectional_search(self.current_state, self.session_goal)

        # Step 1 — GA evolves prompt strategy (or fallback response)
        ga_strategy = evolve_prompt_strategy(self.current_state)
        system_prompt = build_system_prompt(
            state        = self.current_state,
            strategy     = ga_strategy,
            bds_path     = bds["path"],
            therapy_step = plan["action"],
            history      = self.conversation_history,
        )

        # Step 2 — Call Gemini via REST
        api_text = _call_gemini(system_prompt, percept["raw_input"],
                                self.conversation_history)

        # Step 3 — Fallback to GA pool if API unavailable
        if api_text:
            # Parse TIP line if Groq included one — otherwise coping_tip stays None
            coping_tip = None
            clean_lines = []
            for line in api_text.split("\n"):
                if line.strip().upper().startswith("TIP:"):
                    coping_tip = line.strip()[4:].strip()
                else:
                    clean_lines.append(line)
            response_text = "\n".join(clean_lines).strip()
            tone          = ga_strategy["tone"]
            ga_history    = ga_strategy["history"]
            fitness       = ga_strategy["fitness"]
            technique     = ga_strategy["technique"]
            using_api     = True
        else:
            fb            = evolve_response(self.current_state, percept["raw_input"])
            response_text = fb["response"]
            tone          = fb["tone"]
            ga_history    = fb["history"]
            fitness       = fb["fitness"]
            technique     = fb["technique"]
            using_api     = False
            coping_tip    = None  # no Groq = no tip

        self.conversation_history.append({
            "role": "assistant", "content": response_text
        })

        return {
            "text":           response_text,
            "tone":           tone,
            "fitness":        fitness,
            "ga_history":     ga_history,
            "ga_technique":   technique,
            "coping_tip":     coping_tip,
            "therapy_step":   plan["action"],
            "next_state":     plan["next_state"],
            "bds_path":       bds["path"],
            "bds_actions":    bds["actions"],
            "nodes_explored": bds["nodes_explored"],
            "current_state":  self.current_state,
            "goal_state":     self.session_goal,
            "turn":           self.turn_count,
            "using_api":      using_api,
        }

    # ── FULL CYCLE ───────────────────────────────────────────
    def process(self, user_input: str) -> dict:
        percept = self.perceive(user_input)
        self.update_state(percept)
        return self.act(percept, self.plan())

    # ── SUMMARY ─────────────────────────────────────────────
    def get_summary(self) -> dict:
        if not self.emotional_trajectory:
            return {}
        return {
            "turns":         self.turn_count,
            "trajectory":    self.emotional_trajectory,
            "start_state":   self.emotional_trajectory[0],
            "current_state": self.current_state,
            "goal_state":    self.session_goal,
            "progress":      self._progress(),
        }

    def _progress(self) -> int:
        ORDER = ["suicidal","depressed","hopeless","sad","lonely","anxious",
                 "stressed","tired","neutral","okay","relaxed","content",
                 "calm","happy","peaceful","joyful"]
        # Any of these states = goal fulfilled = 100%
        GOAL_FULFILLED = {"calm", "happy", "peaceful", "joyful"}
        if self.current_state in GOAL_FULFILLED:
            return 100
        try:
            return round(ORDER.index(self.current_state) / (len(ORDER)-1) * 100)
        except ValueError:
            return 50

    def reset(self):
        self.__init__()
