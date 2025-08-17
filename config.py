#!/usr/bin/env python3
"""
Configuration settings for LunarTech AI Interview Agent
"""

# Audio Settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
SILENCE_THRESHOLD = 2.5  # Seconds of silence before stopping recording
MIN_CONFIDENCE = 0.6     # Minimum confidence threshold for transcriptions

# Speech Recognition Settings - NATURAL CONVERSATION TIMING
MAX_RETRY_ATTEMPTS = 1   # Reduced retries to feel more natural
TIMEOUT_DEFAULT = 30     # Longer timeout - give people time to think (was 20)
TIMEOUT_NAME = 35        # Even longer for names - people need time (was 25)
TIMEOUT_FAQ = 25         # More time for questions (was 15)
SILENCE_THRESHOLD_NATURAL = 4.0  # Wait longer before assuming they're done (was 2.5)
PATIENCE_MODE = True     # Enable patient, human-like waiting

# TTS Settings
SPEECH_RATE = 150        # Words per minute
SPEECH_VOLUME = 0.9      # Volume level (0.0 to 1.0)

# Interview Settings
QUESTIONS = [
    "Please tell me your full name and a bit about your background.",
    "Why are you interested in joining LunarTech?",
    "Could you describe your experience in Data Science and AI?",
    "What are your goals for the next two years?",
    "Are you ready to start immediately? If not, when?"
]

# File Paths
DATA_DIR = "data"
TRANSCRIPTS_DIR = f"{DATA_DIR}/transcripts"
SUMMARIES_DIR = f"{DATA_DIR}/summaries"
MODELS_DIR = "models"
FAQ_FILE = f"{DATA_DIR}/faq.json"
DATABASE_FILE = f"{DATA_DIR}/interviews.db"
DASHBOARD_FILE = "dashboard.html"

# Confidence Scoring Weights
CONFIDENCE_WEIGHTS = {
    'base_confidence': 0.5,
    'length_bonus': 0.2,      # Bonus for longer responses
    'filler_penalty': 0.1,    # Penalty per filler word
    'sentence_bonus': 0.1,    # Bonus for complete sentences
    'max_filler_penalty': 0.3 # Maximum penalty from fillers
}

# Common filler words that reduce confidence
FILLER_WORDS = ['um', 'uh', 'er', 'like', 'you know', 'well', 'so']

# Letter mappings for spelled names (phonetic alphabet + common variations)
LETTER_MAPPINGS = {
    'a': 'A', 'alpha': 'A', 'able': 'A', 'apple': 'A',
    'b': 'B', 'bravo': 'B', 'boy': 'B', 'ball': 'B',
    'c': 'C', 'charlie': 'C', 'cat': 'C', 'car': 'C',
    'd': 'D', 'delta': 'D', 'dog': 'D', 'door': 'D',
    'e': 'E', 'echo': 'E', 'easy': 'E', 'egg': 'E',
    'f': 'F', 'foxtrot': 'F', 'fox': 'F', 'fire': 'F',
    'g': 'G', 'golf': 'G', 'george': 'G', 'green': 'G',
    'h': 'H', 'hotel': 'H', 'house': 'H', 'hat': 'H',
    'i': 'I', 'india': 'I', 'ice': 'I', 'item': 'I',
    'j': 'J', 'juliet': 'J', 'john': 'J', 'jump': 'J',
    'k': 'K', 'kilo': 'K', 'king': 'K', 'key': 'K',
    'l': 'L', 'lima': 'L', 'love': 'L', 'light': 'L',
    'm': 'M', 'mike': 'M', 'mary': 'M', 'moon': 'M',
    'n': 'N', 'november': 'N', 'nancy': 'N', 'night': 'N',
    'o': 'O', 'oscar': 'O', 'ocean': 'O', 'open': 'O',
    'p': 'P', 'papa': 'P', 'peter': 'P', 'pen': 'P',
    'q': 'Q', 'quebec': 'Q', 'queen': 'Q', 'quick': 'Q',
    'r': 'R', 'romeo': 'R', 'robert': 'R', 'red': 'R',
    's': 'S', 'sierra': 'S', 'sam': 'S', 'sun': 'S',
    't': 'T', 'tango': 'T', 'tom': 'T', 'tree': 'T',
    'u': 'U', 'uniform': 'U', 'uncle': 'U', 'up': 'U',
    'v': 'V', 'victor': 'V', 'victory': 'V', 'voice': 'V',
    'w': 'W', 'whiskey': 'W', 'william': 'W', 'water': 'W',
    'x': 'X', 'xray': 'X', 'x-ray': 'X', 'box': 'X',
    'y': 'Y', 'yankee': 'Y', 'yellow': 'Y', 'yes': 'Y',
    'z': 'Z', 'zulu': 'Z', 'zebra': 'Z', 'zero': 'Z'
}

# Dashboard styling
DASHBOARD_COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'background': 'rgba(255, 255, 255, 0.1)',
    'border': 'rgba(255, 255, 255, 0.2)'
}
