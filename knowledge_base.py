# ============================================================
#  knowledge_base.py  —  Emotional states, responses, strategies
# ============================================================

GOAL_STATE = "calm"

# ── Emotional State Graph (Bi-Directional Search) ──
EMOTIONAL_STATES = {
    "suicidal":  ["depressed"],
    "depressed": ["sad", "hopeless"],
    "hopeless":  ["sad", "anxious"],
    "sad":       ["lonely", "neutral"],
    "lonely":    ["neutral", "anxious"],
    "anxious":   ["stressed", "neutral"],
    "stressed":  ["neutral", "tired"],
    "tired":     ["neutral"],
    "neutral":   ["okay", "relaxed"],
    "okay":      ["calm", "content"],
    "relaxed":   ["calm", "content"],
    "content":   ["happy", "calm"],
    "calm":      ["happy", "peaceful"],
    "happy":     ["peaceful", "joyful"],
    "peaceful":  ["joyful"],
    "joyful":    [],
}

# ── Keyword → Emotional State (priority order, longest match wins) ──
KEYWORD_STATE_MAP = {
    "suicidal": [
        "suicide", "kill myself", "killing myself", "end my life", "ending my life",
        "want to die", "i want to die", "feel like dying", "wish i was dead",
        "wish i were dead", "better off dead", "no reason to live",
        "cant go on", "can't go on", "cannot go on", "want to disappear",
        "end it all", "take my life", "taking my life", "don't want to be here",
        "dont want to be here", "thinking of suicide", "suicidal",
        "hurt myself", "harm myself", "self harm", "self-harm", "cutting myself",
        "don't want to live", "dont want to live",
    ],
    "depressed": ["depressed", "depression", "no point", "worthless", "empty inside", "numb", "nothing matters"],
    "hopeless":  ["hopeless", "no hope", "never get better", "pointless", "no future", "giving up"],
    "sad":       ["sad", "crying", "tears", "upset", "heartbroken", "miserable", "devastated"],
    "lonely":    ["lonely", "alone", "isolated", "no one cares", "nobody", "no friends"],
    "anxious":   ["anxious", "anxiety", "panic", "panicking", "worried", "scared", "fear", "nervous", "dread"],
    "stressed":  ["stressed", "stress", "overwhelmed", "pressure", "burnout", "too much"],
    "tired":     ["tired", "exhausted", "drained", "no energy", "fatigue", "worn out"],
    "neutral":   ["okay", "fine", "alright", "not sure"],
    "content":   ["content", "decent", "managing"],
    "calm":      ["calm", "relaxed", "peaceful", "serene", "composed"],
    "happy":     ["happy", "good", "great", "better", "glad"],
    "joyful":    ["joyful", "amazing", "wonderful", "fantastic", "elated"],
}

# ── Therapy Actions on State Graph Edges ──
THERAPY_ACTIONS = {
    ("suicidal",  "depressed"): "crisis-support",
    ("depressed", "sad"):       "validation + open-talk",
    ("depressed", "hopeless"):  "psychoeducation",
    ("hopeless",  "sad"):       "meaning-finding",
    ("hopeless",  "anxious"):   "CBT reframe",
    ("sad",       "lonely"):    "connection exercise",
    ("sad",       "neutral"):   "grounding + breathing",
    ("lonely",    "neutral"):   "social connection prompt",
    ("lonely",    "anxious"):   "mindfulness",
    ("anxious",   "stressed"):  "identify stressors",
    ("anxious",   "neutral"):   "breathing exercise",
    ("stressed",  "neutral"):   "break-down tasks",
    ("stressed",  "tired"):     "rest permission",
    ("tired",     "neutral"):   "self-care reminder",
    ("neutral",   "okay"):      "positive inquiry",
    ("neutral",   "relaxed"):   "mindfulness",
    ("okay",      "calm"):      "gratitude practice",
    ("okay",      "content"):   "strengths reflection",
    ("relaxed",   "calm"):      "breathing deepening",
    ("relaxed",   "content"):   "savoring exercise",
    ("content",   "happy"):     "joy amplification",
    ("content",   "calm"):      "stability anchoring",
    ("calm",      "happy"):     "positive affirmation",
    ("calm",      "peaceful"):  "body scan meditation",
    ("happy",     "peaceful"):  "gratitude journaling",
    ("happy",     "joyful"):    "celebration ritual",
    ("peaceful",  "joyful"):    "presence exercise",
}

# ── Coping Strategy Tips ──
COPING_STRATEGIES = {
    "breathing":  "🌬️  Box Breathing: Inhale 4s → Hold 4s → Exhale 4s → Hold 4s",
    "grounding":  "🌍  5-4-3-2-1: Name 5 things you see, 4 hear, 3 touch, 2 smell, 1 taste",
    "journaling": "📓  Write 3 honest sentences about how you feel right now",
    "movement":   "🚶  Take a 10-minute walk — even just around your room",
    "connection": "📞  Text or call one person you trust today",
    "rest":       "😴  Set a 20-minute rest timer — no screens, just quiet",
    "gratitude":  "🙏  Write 3 small things you're grateful for today",
    "reframe":    "🔄  Ask yourself: 'Will this matter in 5 years?'",
}

# ── Hardcoded Response Pool (GA fallback when no API key) ──
RESPONSE_POOL = {
    "suicidal": [
        {"text": "I hear you, and I'm really glad you're talking to me right now. Please reach out to iCall: 9152987821 — they're there for you right now.", "tags": ["crisis", "helpline"], "tone": "urgent"},
        {"text": "What you're feeling is real and valid. Please call Vandrevala Foundation: 1860-2662-345. You don't have to face this alone.", "tags": ["crisis", "helpline"], "tone": "urgent"},
        {"text": "You reached out — that took courage. Please call iCall (9152987821) right now. A trained person is ready to listen.", "tags": ["crisis"], "tone": "caring"},
    ],
    "depressed": [
        {"text": "Depression can feel like carrying the whole world. What's been weighing on you the most lately?", "tags": ["empathy", "open-question"], "tone": "warm"},
        {"text": "It takes strength to keep going through depression. I'm here with you — can you tell me one small thing that happened today?", "tags": ["strength", "grounding"], "tone": "encouraging"},
        {"text": "You're not broken — depression lies to us. What did you enjoy doing before things got heavy?", "tags": ["reframe"], "tone": "gentle"},
    ],
    "hopeless": [
        {"text": "When everything feels pointless, it's hard to see any way forward. But you reached out — that matters. What made today especially hard?", "tags": ["validation"], "tone": "gentle"},
        {"text": "Hopelessness is one of the cruelest feelings. Your brain is lying to you right now. Can we find one tiny thing that still has meaning?", "tags": ["reframe", "meaning"], "tone": "warm"},
        {"text": "Even in the darkest tunnels there's always an exit. I'm here to help you look.", "tags": ["hope"], "tone": "encouraging"},
    ],
    "sad": [
        {"text": "I'm really sorry you're feeling sad. It's okay to feel this way. Do you want to talk about what's going on?", "tags": ["empathy"], "tone": "warm"},
        {"text": "Sadness is a signal that something matters to you. What are you grieving or missing right now?", "tags": ["insight"], "tone": "thoughtful"},
        {"text": "It's okay to cry and feel low. You don't have to be strong all the time. I'm listening.", "tags": ["permission"], "tone": "gentle"},
    ],
    "lonely": [
        {"text": "Loneliness can be painful even when you're surrounded by people. What kind of connection are you craving right now?", "tags": ["empathy"], "tone": "warm"},
        {"text": "Feeling alone is one of the hardest human experiences. I'm here and I genuinely want to understand what you're going through.", "tags": ["presence"], "tone": "warm"},
        {"text": "You reached out — that's a brave and healthy instinct. What's been making you feel disconnected?", "tags": ["strength"], "tone": "encouraging"},
    ],
    "anxious": [
        {"text": "Anxiety can feel like your mind is running on overdrive. Let's slow down — try breathing in for 4 counts, hold 4, out for 4. How does that feel?", "tags": ["breathing"], "tone": "calm"},
        {"text": "What's your mind racing about right now? Naming the worry takes away some of its power.", "tags": ["CBT"], "tone": "gentle"},
        {"text": "Anxiety makes unlikely things feel inevitable. What's the specific thing you're most afraid of?", "tags": ["reframe"], "tone": "thoughtful"},
    ],
    "stressed": [
        {"text": "Stress is your body's way of saying you're carrying too much. What's on your plate right now?", "tags": ["validation"], "tone": "calm"},
        {"text": "Let's break it down. What's the single most stressful thing today? We'll tackle it one piece at a time.", "tags": ["problem-solving"], "tone": "practical"},
        {"text": "Even 5 minutes of rest can reset your nervous system. Take 3 slow deep breaths with me before we continue.", "tags": ["mindfulness"], "tone": "calm"},
    ],
    "tired": [
        {"text": "Your body and mind are asking for rest. When did you last truly take a break and recharge?", "tags": ["self-care"], "tone": "gentle"},
        {"text": "Exhaustion makes everything harder. What's draining you the most — physical work, emotional burden, or both?", "tags": ["inquiry"], "tone": "thoughtful"},
        {"text": "It's okay to slow down. Rest is not laziness — it's necessary. What small rest could you give yourself today?", "tags": ["permission"], "tone": "warm"},
    ],
    "neutral": [
        {"text": "Sometimes 'okay' is enough. Is there anything specific on your mind, or did you just need someone to talk to?", "tags": ["open-question"], "tone": "friendly"},
        {"text": "How's your day been so far? I'd love to know more about what's going on with you.", "tags": ["inquiry"], "tone": "friendly"},
        {"text": "I'm here whenever you're ready to share. No pressure — we can talk about anything.", "tags": ["presence"], "tone": "light"},
    ],
    "calm": [
        {"text": "It's good to hear you're feeling calm. What helped you get to this place?", "tags": ["reflection"], "tone": "warm"},
        {"text": "Calmness is a skill. What practices help you stay grounded when things get hard?", "tags": ["skill-building"], "tone": "encouraging"},
        {"text": "Wonderful. Let's protect this feeling. What would you like to focus on today?", "tags": ["goal"], "tone": "positive"},
    ],
    "happy": [
        {"text": "That's great to hear! What's been making you feel good lately?", "tags": ["positive"], "tone": "cheerful"},
        {"text": "Happiness is worth celebrating. Tell me more — what's going well?", "tags": ["celebration"], "tone": "cheerful"},
    ],
    "joyful": [
        {"text": "Pure joy is rare and precious! What's sparking this wonderful feeling?", "tags": ["celebration"], "tone": "joyful"},
        {"text": "Your joy is contagious! What made today so special?", "tags": ["positive"], "tone": "joyful"},
    ],
    "content":  [{"text": "It sounds like things are in a decent place. What's been helping you feel content?", "tags": ["reflection"], "tone": "warm"}],
    "relaxed":  [{"text": "Relaxation is so valuable. What helped you unwind?", "tags": ["reflection"], "tone": "calm"}],
    "okay":     [{"text": "Glad to hear you're okay! Anything you want to talk through today?", "tags": ["open-question"], "tone": "friendly"}],
    "peaceful": [{"text": "Peace of mind is a beautiful thing. What's bringing you this sense of peace?", "tags": ["reflection"], "tone": "calm"}],
    "hopeless": [{"text": "It sounds really heavy right now. Would you like to talk about what's making things feel so bleak?", "tags": ["validation"], "tone": "gentle"}],
}
