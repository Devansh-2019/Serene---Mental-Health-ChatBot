# ============================================================
#  genetic_algorithm.py  —  AI Concept: Genetic Algorithm
#
#  API MODE   : GA evolves the best prompt strategy (tone,
#               technique, empathy) → sent to Gemini API
#  FALLBACK   : GA evolves best response from hardcoded pool
# ============================================================

import random, copy
from knowledge_base import RESPONSE_POOL, KEYWORD_STATE_MAP

TONE_PREF = {
    "suicidal":  ["urgent","caring"],
    "depressed": ["warm","gentle","encouraging"],
    "hopeless":  ["warm","encouraging","gentle"],
    "sad":       ["warm","gentle","thoughtful"],
    "lonely":    ["warm","encouraging"],
    "anxious":   ["calm","gentle","thoughtful"],
    "stressed":  ["calm","practical"],
    "tired":     ["gentle","warm"],
    "neutral":   ["friendly","light"],
    "content":   ["warm","positive"],
    "relaxed":   ["calm","warm"],
    "okay":      ["friendly","positive"],
    "calm":      ["warm","positive","encouraging"],
    "happy":     ["cheerful","encouraging"],
    "peaceful":  ["calm","joyful"],
    "joyful":    ["joyful","cheerful"],
}

TECHNIQUE_PREF = {
    "suicidal":  ["crisis-support","safety-planning","active-listening"],
    "depressed": ["validation","behavioural-activation","open-questioning"],
    "hopeless":  ["meaning-finding","cognitive-reframe","hope-instillation"],
    "sad":       ["empathic-reflection","permission-to-feel","grounding"],
    "lonely":    ["connection-building","validation","social-activation"],
    "anxious":   ["breathing-exercise","grounding","cognitive-defusion"],
    "stressed":  ["task-breakdown","mindfulness","boundary-setting"],
    "tired":     ["self-compassion","rest-permission","energy-audit"],
    "neutral":   ["open-inquiry","positive-exploration","psychoeducation"],
    "calm":      ["strengths-reflection","gratitude","goal-setting"],
    "happy":     ["savoring","positive-reinforcement","future-planning"],
    "joyful":    ["celebration","savoring","gratitude"],
}

PREFERRED_TAGS = {
    "suicidal":  ["crisis","helpline","support"],
    "depressed": ["empathy","validation","open-question","strength"],
    "hopeless":  ["hope","reframe","meaning","validation"],
    "sad":       ["empathy","permission","support"],
    "lonely":    ["connection","presence","strength"],
    "anxious":   ["breathing","grounding","CBT"],
    "stressed":  ["grounding","problem-solving","mindfulness"],
    "tired":     ["self-care","permission","rest"],
    "neutral":   ["open-question","presence"],
    "calm":      ["reflection","strengths","forward"],
    "happy":     ["positive","inquiry","celebration"],
    "joyful":    ["celebration","positive"],
}

# ══════════════════════════════════════════════════════
#  PROMPT-STRATEGY GA  (used when API is available)
# ══════════════════════════════════════════════════════

def _make_chrom(state):
    return {
        "tone":        random.choice(TONE_PREF.get(state, ["warm"])),
        "technique":   random.choice(TECHNIQUE_PREF.get(state, ["validation"])),
        "empathy":     random.choice(["high","medium","subtle"]),
        "ask_q":       random.choice([True, True, False]),
        "crisis_mode": state == "suicidal",
        "score":       0.0,
    }

def _fitness_prompt(c, state):
    s = 0.0
    pt = TONE_PREF.get(state, [])
    if c["tone"] in pt:
        s += 0.35 * max(0.4, 1 - pt.index(c["tone"]) * 0.15)
    tech = TECHNIQUE_PREF.get(state, [])
    if c["technique"] in tech:
        s += 0.35 * max(0.4, 1 - tech.index(c["technique"]) * 0.15)
    ep = {"suicidal":"high","depressed":"high","hopeless":"high","sad":"high","lonely":"high","anxious":"medium","stressed":"medium","tired":"medium"}.get(state,"subtle")
    s += 0.15 if c["empathy"] == ep else (0.07 if c["empathy"] != "high" and ep != "high" else 0)
    if c["ask_q"] and state in ["neutral","sad","depressed","lonely","hopeless"]: s += 0.10
    elif not c["ask_q"] and state not in ["neutral","sad","depressed","lonely","hopeless"]: s += 0.05
    if c["crisis_mode"] == (state == "suicidal"): s += 0.05
    return round(min(s, 1.0), 4)

def _cross_prompt(p1, p2):
    f = p1 if p1["score"] >= p2["score"] else p2
    return {"tone": random.choice([p1["tone"], p2["tone"]]),
            "technique": random.choice([p1["technique"], p2["technique"]]),
            "empathy": random.choice([p1["empathy"], p2["empathy"]]),
            "ask_q": random.choice([p1["ask_q"], p2["ask_q"]]),
            "crisis_mode": f["crisis_mode"], "score": 0.0}

def _mutate_prompt(c, state, rate=0.3):
    m = copy.deepcopy(c)
    if random.random() < rate: m["tone"]      = random.choice(TONE_PREF.get(state, ["warm"]))
    if random.random() < rate: m["technique"] = random.choice(TECHNIQUE_PREF.get(state, ["validation"]))
    if random.random() < rate: m["empathy"]   = random.choice(["high","medium","subtle"])
    if random.random() < rate: m["ask_q"]     = not m["ask_q"]
    return m

def evolve_prompt_strategy(state, generations=12, pop_size=8):
    pop = [_make_chrom(state) for _ in range(pop_size)]
    for c in pop: c["score"] = _fitness_prompt(c, state)
    history = []
    for _ in range(generations):
        pop.sort(key=lambda c: c["score"], reverse=True)
        new = copy.deepcopy(pop[:2])
        while len(new) < pop_size:
            p1 = max(random.sample(pop, 3), key=lambda c: c["score"])
            p2 = max(random.sample(pop, 3), key=lambda c: c["score"])
            child = _mutate_prompt(_cross_prompt(p1, p2), state)
            child["score"] = _fitness_prompt(child, state)
            new.append(child)
        pop = new
        history.append(round(max(c["score"] for c in pop), 4))
    best = max(pop, key=lambda c: c["score"])
    return {**best, "history": history, "fitness": best["score"], "generations": generations}


def build_system_prompt(state, strategy, bds_path, therapy_step, history):
    tone_map = {
        "urgent":      "Respond with URGENT warmth. Be direct and caring. Always include crisis helplines.",
        "caring":      "Be deeply caring and non-judgmental. Make the user feel completely safe.",
        "warm":        "Use a warm, nurturing tone — like a trusted friend who truly listens.",
        "gentle":      "Be very gentle and soft. Never push. Never judge.",
        "encouraging": "Gently highlight the user's strengths and resilience.",
        "calm":        "Speak calmly and slowly. Your tone itself should be grounding.",
        "practical":   "Balance empathy with practical, actionable guidance.",
        "thoughtful":  "Be thoughtful and reflective. Think with the user, not at them.",
        "friendly":    "Be warm and friendly, like a knowledgeable supportive companion.",
        "light":       "Keep things light and open — no pressure, just presence.",
        "positive":    "Gently highlight the positive while validating any challenges.",
        "cheerful":    "Be genuinely cheerful and celebratory.",
        "joyful":      "Match and amplify the user's joy with genuine enthusiasm.",
    }
    tech_map = {
        "crisis-support":      "Prioritise safety. Include iCall: 9152987821 and Vandrevala: 1860-2662-345. Ask if they are safe right now.",
        "safety-planning":     "Gently explore what has kept them safe so far. Suggest one small safety step.",
        "active-listening":    "Reflect back what you hear using 'It sounds like...' and 'I hear you saying...'",
        "validation":          "Validate their feelings fully before offering any suggestions.",
        "behavioural-activation": "Gently suggest one small enjoyable activity they could do today.",
        "open-questioning":    "Ask one open-ended question to help them explore their feelings more deeply.",
        "meaning-finding":     "Help them find one small thing that still has meaning or matters to them.",
        "cognitive-reframe":   "Gently challenge one negative thought pattern with a compassionate reframe.",
        "hope-instillation":   "Plant a small seed of hope without dismissing their pain.",
        "empathic-reflection": "Mirror their emotional experience back to them with compassion.",
        "permission-to-feel":  "Explicitly give them permission to feel what they're feeling.",
        "grounding":           "Guide them through a brief grounding exercise (5-4-3-2-1 senses or box breathing).",
        "breathing-exercise":  "Guide them through box breathing: inhale 4 counts, hold 4, exhale 4, hold 4.",
        "connection-building": "Reinforce that reaching out for connection is brave and healthy.",
        "cognitive-defusion":  "Help them observe anxious thoughts from a distance rather than being fused with them.",
        "task-breakdown":      "Help them break one overwhelming thing into the smallest possible next step.",
        "mindfulness":         "Invite them to focus on just the present moment for 30 seconds.",
        "self-compassion":     "Encourage them to speak to themselves the way they'd speak to a good friend.",
        "rest-permission":     "Explicitly give them permission to rest — rest is productive recovery.",
        "open-inquiry":        "Ask a warm, curious question about what's on their mind.",
        "strengths-reflection":"Help them identify and celebrate a personal strength.",
        "gratitude":           "Invite them to name one small thing they're grateful for today.",
        "savoring":            "Encourage them to fully savour and extend this positive feeling.",
        "celebration":         "Genuinely celebrate their joy and ask what's sparking it.",
    }
    empathy_map = {
        "high":   "Lead with STRONG emotional validation — spend the first sentence purely acknowledging their pain.",
        "medium": "Open with genuine empathy, then gently transition to support.",
        "subtle": "Weave empathy naturally throughout rather than leading heavily with it.",
    }
    path_str = " → ".join(bds_path) if bds_path else state
    recent_ctx = ""
    if len(history) > 2:
        recent = history[-4:]
        recent_ctx = "\n\nRecent conversation:\n" + "\n".join(
            f"{'User' if m['role']=='user' else 'Serene'}: {m['content']}"
            for m in recent if "content" in m
        )
    q_instr = ("End with ONE open, caring question." if strategy["ask_q"]
               else "Do NOT end with a question — let your response be a moment of quiet support.")

    return f"""You are Serene, a compassionate AI mental health companion. You are NOT a therapist or doctor, but you are deeply empathetic and genuinely caring.

EMOTIONAL STATE DETECTED: {state}
THERAPY PATH (Bi-Directional Search): {path_str}
CURRENT THERAPY STEP: {therapy_step}

GA-EVOLVED RESPONSE STRATEGY:
- Tone: {tone_map.get(strategy['tone'], 'warm and caring')}
- Technique: {tech_map.get(strategy['technique'], 'active listening')}
- Empathy: {empathy_map.get(strategy['empathy'], 'medium')}
- {q_instr}

RULES:
- 3 to 5 sentences maximum. Be concise but deeply human.
- NEVER mention you are an AI, or mention Groq, Llama, or Google.
- NEVER diagnose or prescribe anything.
- NEVER dismiss or minimise feelings.
- If crisis_mode is True: ALWAYS include iCall: 9152987821 and Vandrevala: 1860-2662-345.
- crisis_mode: {strategy['crisis_mode']}
- Only if it feels natural and helpful, end your response with a new line starting with "TIP:" followed by one short actionable suggestion (max 10 words, with emoji) that directly relates to what you said. Skip the TIP line entirely if the response doesn't call for one.
  Example: TIP: 🌬️ Try box breathing for 2 minutes right now{recent_ctx}"""


# ══════════════════════════════════════════════════════
#  RESPONSE-TEXT GA  (fallback when no API key)
# ══════════════════════════════════════════════════════

def _fitness_response(c, state, user_input):
    s = 0.0
    pt = TONE_PREF.get(state, [])
    if c["tone"] in pt: s += 0.35 * (1 - pt.index(c["tone"]) * 0.1)
    ptags = set(PREFERRED_TAGS.get(state, []))
    s += min(0.35, len(ptags & set(c.get("tags",[]))) * 0.12)
    kws = KEYWORD_STATE_MAP.get(state, [])
    s += min(0.20, sum(1 for k in kws if k in c.get("text","").lower()) * 0.07)
    l = len(c.get("text",""))
    s += 0.10 if 60 <= l <= 200 else (0.05 if 40 <= l <= 250 else 0)
    return round(min(s, 1.0), 4)

def evolve_response(state, user_input, generations=12, pop_size=8):
    pool = RESPONSE_POOL.get(state, RESPONSE_POOL.get("neutral", []))
    pop  = [copy.deepcopy(random.choice(pool)) for _ in range(pop_size)]
    for i, item in enumerate(RESPONSE_POOL.get(state, [])):
        if i < pop_size: pop[i] = copy.deepcopy(item)
    for c in pop: c["score"] = _fitness_response(c, state, user_input)
    history = []
    for _ in range(generations):
        pop.sort(key=lambda c: c["score"], reverse=True)
        new = copy.deepcopy(pop[:2])
        while len(new) < pop_size:
            p1 = max(random.sample(pop, min(3, len(pop))), key=lambda c: c["score"])
            p2 = max(random.sample(pop, min(3, len(pop))), key=lambda c: c["score"])
            s1, s2 = p1["text"].split(". "), p2["text"].split(". ")
            txt = ". ".join(s1[:max(1,len(s1)//2)] + s2[max(0,len(s2)//2):]) if len(s1)>1 and len(s2)>1 else (p1 if p1["score"]>=p2["score"] else p2)["text"]
            f   = p1 if p1["score"] >= p2["score"] else p2
            child = {"text": txt, "tags": list(set(p1.get("tags",[]) + p2.get("tags",[]))), "tone": f["tone"], "score": 0.0}
            if random.random() < 0.25:
                pt2 = PREFERRED_TAGS.get(state, [])
                if pt2: child["tags"].append(random.choice(pt2))
            if random.random() < 0.25:
                pt3 = TONE_PREF.get(state, [])
                if pt3: child["tone"] = random.choice(pt3)
            child["score"] = _fitness_response(child, state, user_input)
            new.append(child)
        pop = new
        history.append(round(max(c["score"] for c in pop), 4))
    best = max(pop, key=lambda c: c["score"])
    return {"response": best["text"], "tone": best["tone"], "fitness": best["score"],
            "history": history, "generations": generations, "technique": "pool-selection (fallback)"}
