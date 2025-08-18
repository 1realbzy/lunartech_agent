#!/usr/bin/env python3
# LunarTech Offline AI Interview Agent
# This script conducts a 5-question voice interview, transcribes responses,
# and generates summary and structured output.

import os
import sys
import json
import time
import datetime
import logging
import threading
import queue
import re
import csv
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Speech-to-text
from vosk import Model, KaldiRecognizer
import pyaudio

# Text-to-speech
import pyttsx3

# Import configuration
from config import *

# Local LLM for dialogue and summarization
# For now, I'll use an enhanced mock LLM that provides better responses
# In production, you would integrate with a working LLM library

class EnhancedLLM:
    """Enhanced LLM with better logic for interview responses."""
    
    def __init__(self):
        print("✅ Initialized Enhanced LLM for interview processing")
    
    def generate(self, prompt, max_tokens=512):
        """Generate intelligent responses based on the prompt."""
        print(f"🧠 [Enhanced LLM] Processing: {prompt[:50]}...")
        
        # Analyze answer quality
        if "clear and relevant" in prompt.lower():
            # Extract the actual answer from the prompt
            lines = prompt.split('\n')
            answer_line = ""
            for line in lines:
                if 'answer:' in line.lower():
                    answer_line = line.split(':')[-1].strip().strip('"')
                    break
            
            if not answer_line:
                return "NO"
            
            # Check answer quality
            words = answer_line.split()
            if len(words) < 3:
                return "NO"
            
            # Look for meaningful content
            meaningful_words = ['experience', 'work', 'study', 'learn', 'develop', 'skills', 
                              'project', 'interested', 'passionate', 'goal', 'ready', 'prepared']
            
            if any(word in answer_line.lower() for word in meaningful_words) and len(words) >= 5:
                return "YES"
            else:
                return "NO"
        
        # Handle FAQ matching
        if "which FAQ" in prompt.lower():
            query_text = prompt.lower()
            if any(word in query_text for word in ['cost', 'price', 'money', 'fee', 'pay']):
                return "1"
            elif any(word in query_text for word in ['requirement', 'apply', 'need', 'prerequisite']):
                return "2"
            elif any(word in query_text for word in ['schedule', 'time', 'duration', 'when', 'hours']):
                return "3"
            elif any(word in query_text for word in ['computer', 'laptop', 'equipment', 'device']):
                return "4"
            elif any(word in query_text for word in ['certificate', 'certification', 'diploma']):
                return "5"
            elif any(word in query_text for word in ['online', 'person', 'remote', 'location']):
                return "6"
            elif any(word in query_text for word in ['job', 'placement', 'career', 'employment']):
                return "7"
            else:
                return "NONE"
        
        # Handle interview summary generation
        if "Below is an interview" in prompt and "JSON_DATA:" in prompt:
            # Extract candidate name from prompt
            candidate_name = "Candidate"
            name_match = re.search(r"a candidate named '([^']*)'", prompt)
            if name_match:
                candidate_name = name_match.group(1)

            # Extract interview content
            lines = prompt.split('\n')
            questions = []
            answers = []
            
            current_question = ""
            current_answer = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('Question'):
                    if current_question and current_answer:
                        questions.append(current_question)
                        answers.append(current_answer)
                    current_question = line
                    current_answer = ""
                elif line.startswith('Answer'):
                    current_answer = line
            
            # Add the last Q&A pair
            if current_question and current_answer:
                questions.append(current_question)
                answers.append(current_answer)
            
            # Generate summary
            summary = self._generate_interview_summary(questions, answers)
            json_data = self._extract_candidate_info(answers, candidate_name=candidate_name)
            
            return f"{summary}\n\nJSON_DATA:\n{json_data}"
        
        # Default response
        return "I understand and will provide appropriate assistance based on the context."
    
    def _generate_interview_summary(self, questions, answers):
        """Generate a summary of the interview."""
        summary = "Interview Summary:\n\n"
        summary += "The candidate participated in a comprehensive interview covering their background, "
        summary += "motivations, experience, and readiness for the LunarTech program. "
        
        # Analyze answers for key themes
        all_text = " ".join(answers).lower()
        
        if any(word in all_text for word in ['experience', 'work', 'job', 'project']):
            summary += "They demonstrated relevant professional experience. "
        
        if any(word in all_text for word in ['interested', 'passionate', 'excited', 'want']):
            summary += "The candidate expressed strong interest in the program. "
        
        if any(word in all_text for word in ['ready', 'prepared', 'committed', 'dedicated']):
            summary += "They appear ready and committed to undertaking the intensive program."
        
        return summary
    
    def _extract_candidate_info(self, answers, candidate_name="Candidate"):
        """Extract structured information from answers."""
        import json
        
        all_text = " ".join(answers).lower()
        
        # Use the provided candidate name
        name = candidate_name
        
        # Determine interest level
        interest_level = "medium"
        if any(word in all_text for word in ['very interested', 'excited', 'passionate', 'love', 'really want']):
            interest_level = "high"
        elif any(word in all_text for word in ['not sure', 'maybe', 'considering']):
            interest_level = "low"
        
        # Determine readiness
        readiness = "medium"
        if any(word in all_text for word in ['ready', 'prepared', 'committed', 'dedicated', 'definitely']):
            readiness = "high"
        elif any(word in all_text for word in ['not ready', 'need time', 'maybe later']):
            readiness = "low"
        
        # Extract background info
        background = "Entry-level candidate"
        if any(word in all_text for word in ['experience', 'years', 'work', 'job', 'project']):
            if any(word in all_text for word in ['senior', 'lead', 'manager', '5 years', 'experienced']):
                background = "Experienced professional with significant background"
            else:
                background = "Professional with some relevant experience"
        
        if any(word in all_text for word in ['student', 'graduate', 'university', 'college', 'degree']):
            background = "Recent graduate or current student"
        
        info = {
            "name": name,
            "interest_level": interest_level,
            "readiness": readiness,
            "background": background
        }
        
        return json.dumps(info, indent=2)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("session_logs.csv", mode="a"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup directories from config
DATA_DIR_PATH = Path(DATA_DIR)
TRANSCRIPTS_DIR_PATH = Path(TRANSCRIPTS_DIR)
SUMMARIES_DIR_PATH = Path(SUMMARIES_DIR)
MODELS_DIR_PATH = Path(MODELS_DIR)
FAQ_FILE_PATH = Path(FAQ_FILE)

# Ensure directories exist
TRANSCRIPTS_DIR_PATH.mkdir(parents=True, exist_ok=True)
SUMMARIES_DIR_PATH.mkdir(parents=True, exist_ok=True)
MODELS_DIR_PATH.mkdir(exist_ok=True)

class InterviewAgent:
    """
    LunarTech AI Interview Agent that conducts voice interviews,
    processes responses, and generates summaries.
    """
    
    def __init__(self):
        self.initialize_speech_recognition()
        self.initialize_text_to_speech()
        self.initialize_llm()
        self.load_faq()
        self.interview_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "questions": QUESTIONS,
            "answers": [],
            "summary": "",
            "extracted_info": {}
        }
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.transcription = ""
        self.candidate_name = "Candidate"
        
    def initialize_speech_recognition(self):
        """Initialize speech recognition with Vosk."""
        try:
            print("🚀 Initializing speech recognition with Vosk...")
            self._initialize_vosk_only()
            logger.info("Speech recognition initialized successfully.")
            print("🎉 Speech recognition ready")
                
        except Exception as e:
            logger.error(f"Failed to initialize speech recognition: {e}")
            print("❌ Speech recognition initialization failed")
            sys.exit(1)
    
    def _initialize_vosk_only(self):
        """Initialize Vosk-only speech recognition (fallback)."""
        # Find available Vosk model in models directory
        vosk_models = list(MODELS_DIR_PATH.glob("vosk*")) + list(MODELS_DIR_PATH.glob("*vosk*"))
        if not vosk_models:
            print("Error: No Vosk model found in the models directory.")
            print("Please download a model from https://alphacephei.com/vosk/models")
            print("and place it in the models/ directory.")
            sys.exit(1)
            
        model_path = str(vosk_models[0])
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        self.use_hybrid_engine = False
        logger.info("Vosk-only speech recognition initialized successfully.")
    
    def initialize_text_to_speech(self):
        """Initialize the pyttsx3 text-to-speech engine."""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Get available voices and set a female voice if available
            voices = self.tts_engine.getProperty('voices')
            female_voices = [v for v in voices if 'female' in v.name.lower()]
            if female_voices:
                self.tts_engine.setProperty('voice', female_voices[0].id)
            
            # Set speech rate and volume from config
            self.tts_engine.setProperty('rate', SPEECH_RATE)
            self.tts_engine.setProperty('volume', SPEECH_VOLUME)
            
            logger.info("Text-to-speech initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize text-to-speech: {e}")
            sys.exit(1)
    
    def initialize_llm(self):
        """Initialize the local large language model."""
        try:
            print("🚀 Initializing Enhanced LLM for interview processing...")
            self.llm = EnhancedLLM()
            logger.info("Enhanced LLM initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced LLM: {e}")
            print(f"❌ Failed to initialize Enhanced LLM: {e}")
            # Create a simple fallback
            self.llm = EnhancedLLM()  # This should still work as it's very basic
            logger.info("Enhanced LLM initialized with fallback")
    
    def load_faq(self):
        """Load FAQ data from JSON file."""
        try:
            if FAQ_FILE_PATH.exists():
                with open(FAQ_FILE_PATH, 'r') as f:
                    self.faq_data = json.load(f)
                logger.info("FAQ data loaded successfully.")
            else:
                self.faq_data = {"faqs": []}
                logger.warning(f"FAQ file not found at {FAQ_FILE_PATH}. Empty FAQ created.")
        except Exception as e:
            logger.error(f"Failed to load FAQ: {e}")
            self.faq_data = {"faqs": []}
    
    def speak(self, text: str):
        """Convert text to speech and play it."""
        try:
            print(f"Agent: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            print(f"Agent: {text} (TTS failed, displaying text only)")
    
    def listen(self, timeout: int = 20) -> str:
        """
        Listen for speech input using best available engine (Whisper or Vosk).
        Returns the transcribed text.
        """
        try:
            # Use hybrid engine if available (Whisper + Vosk fallback)
            if hasattr(self, 'use_hybrid_engine') and self.use_hybrid_engine:
                result = self.speech_engine.listen(timeout)
                
                # Log performance for monitoring
                if hasattr(self.speech_engine, 'current_engine'):
                    engine_used = self.speech_engine.current_engine
                    if engine_used == "whisper":
                        print("🎯 Used Whisper (enhanced accent recognition)")
                    else:
                        print("🔄 Used Vosk (fallback)")
                
                return result
            
            # Fallback to original Vosk implementation
            else:
                return self._listen_vosk_original(timeout)
                
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            # Ultimate fallback to Vosk
            return self._listen_vosk_original(timeout)
    
    def _listen_vosk_original(self, timeout: int = 30) -> str:
        """Original Vosk listening implementation with natural conversation timing."""
        # Clear any previous transcription
        self.transcription = ""
        self.is_listening = True
        
        # Clear the audio queue to avoid interference from previous audio
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        # Reset the recognizer to clear any previous state
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        
        # Start recording in a separate thread
        recording_thread = threading.Thread(target=self._record_audio)
        recording_thread.daemon = True
        recording_thread.start()
        
        print("🎤 Listening... (take your time)")
        start_time = time.time()
        last_speech_time = time.time()
        has_speech = False
        
        # Use natural conversation timing
        silence_threshold = SILENCE_THRESHOLD_NATURAL if hasattr(sys.modules[__name__], 'SILENCE_THRESHOLD_NATURAL') else 4.0
        
        try:
            while time.time() - start_time < timeout:
                if not self.audio_queue.empty():
                    data = self.audio_queue.get()
                    
                    # Process partial results for real-time feedback
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        if result.get("text", "").strip():
                            new_text = result["text"].strip()
                            if new_text:
                                self.transcription = new_text  # Replace, don't append
                                print(f"✓ Heard: {self.transcription}")
                                last_speech_time = time.time()
                                has_speech = True
                    else:
                        # Show partial results for immediate feedback (less aggressive)
                        partial = json.loads(self.recognizer.PartialResult())
                        if partial.get("partial", "").strip():
                            partial_text = partial["partial"].strip()
                            if partial_text and len(partial_text) > 3:  # Longer threshold
                                print(f"... {partial_text}", end="\r")
                
                # More patient - wait longer before assuming they're done
                if has_speech and time.time() - last_speech_time > silence_threshold:
                    print("\n✅ Got your response, processing...")
                    break
                
                # Show patience indicators
                elapsed = time.time() - start_time
                if not has_speech and elapsed > 10 and elapsed % 10 < 0.1:
                    print("💭 I'm listening... take your time")
                
                time.sleep(0.1)  # Slightly longer sleep for more natural feel
            
            # Stop recording
            self.is_listening = False
            recording_thread.join(timeout=2)  # More time for cleanup
            
            # Get final result
            final_result = json.loads(self.recognizer.FinalResult())
            if final_result.get("text", "").strip():
                final_text = final_result["text"].strip()
                if final_text:
                    self.transcription = final_text
            
            # Clean up the transcription
            self.transcription = self.transcription.strip()
            
            if self.transcription:
                print(f"📝 Perfect! I heard: {self.transcription}")
            else:
                print("🤔 I didn't catch that - no worries, let's try again")
            
            return self.transcription
            
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            self.is_listening = False
            return ""
    
    def _record_audio(self):
        """Record audio in chunks and add to the queue for processing."""
        stream = None
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                input_device_index=None  # Use default microphone
            )
            
            while self.is_listening:
                try:
                    data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    if data and self.is_listening:
                        self.audio_queue.put(data)
                except Exception as e:
                    if self.is_listening:  # Only log if we're still supposed to be listening
                        logger.warning(f"Audio read error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Audio recording error: {e}")
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
    
    def llm_query(self, prompt: str) -> str:
        """Query the local LLM with a prompt and return the response."""
        try:
            response = self.llm.generate(prompt, max_tokens=512)
            return response.strip()
        except Exception as e:
            logger.error(f"LLM query error: {e}")
            return "I apologize, but I'm having trouble processing that request."
    
    def test_method(self):
        """Simple test method to check if methods are being added properly."""
        return "test works"
    
    def calculate_confidence(self, transcription: str) -> float:
        """Calculate confidence score for transcription based on various factors."""
        if not transcription:
            return 0.0
        
        # Use hardcoded values instead of config for now
        confidence = 0.5  # base_confidence
        
        # Length factor - longer responses generally more reliable
        word_count = len(transcription.split())
        if word_count >= 5:
            confidence += 0.2  # length_bonus
        elif word_count >= 3:
            confidence += 0.1  # half length_bonus
        
        # Check for common filler words that might indicate uncertainty
        filler_words = ['um', 'uh', 'er', 'like', 'you know', 'well', 'so']
        filler_count = sum(1 for word in transcription.lower().split() if word in filler_words)
        confidence -= min(filler_count * 0.1, 0.3)  # filler_penalty with max
        
        # Check for complete sentences
        if transcription.endswith('.') or transcription.endswith('!') or transcription.endswith('?'):
            confidence += 0.1  # sentence_bonus
        
        return max(0.0, min(1.0, confidence))
    
    def confirm_name_spelling(self, transcribed_name: str) -> str:
        """Confirm name spelling with candidate, especially for non-English names."""
        potential_names = []
        
        # Try to extract name using regex for patterns like "my name is..."
        name_match = re.search(r"(?:my name is|I'm|I am)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)", transcribed_name, re.IGNORECASE)
        if name_match:
            # Capitalize the extracted name properly
            potential_names = [name.title() for name in name_match.group(1).split()]

        # If regex fails, fall back to looking for capitalized words
        if not potential_names:
            words = transcribed_name.split()
            for word in words:
                if word.istitle() and len(word) > 2:
                    potential_names.append(word)

        if not potential_names:
            # If still no name found, ask for spelling
            self.speak("I want to make sure I get your name right. Could you please spell your first name letter by letter?")
            spelled_name = self.listen(timeout=30)
            return self.process_spelled_name(spelled_name)
        
        # If we found potential names, confirm them
        name_to_confirm = " ".join(potential_names[:2])  # Take first two potential names
        self.speak(f"I heard your name as {name_to_confirm}. Is that correct? Please say yes or no.")
        confirmation = self.listen(timeout=15)
        
        if "no" in confirmation.lower() or "wrong" in confirmation.lower() or "incorrect" in confirmation.lower():
            self.speak("I apologize. Could you please spell your name letter by letter, with a pause between each letter?")
            spelled_name = self.listen(timeout=30)
            return self.process_spelled_name(spelled_name)
        
        return name_to_confirm
    
    def process_spelled_name(self, spelled_input: str) -> str:
        """Process letter-by-letter spelled name input."""
        if not spelled_input:
            return "Unknown"
        
        # Letter mappings for speech recognition
        letter_mappings = {
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
        
        words = spelled_input.lower().split()
        letters = []
        
        for word in words:
            if word in letter_mappings:
                letters.append(letter_mappings[word])
            elif len(word) == 1 and word.isalpha():
                letters.append(word.upper())
        
        if letters:
            constructed_name = ''.join(letters)
            # Capitalize first letter and make rest lowercase for proper name format
            formatted_name = constructed_name[0].upper() + constructed_name[1:].lower()
            self.speak(f"Thank you. I have your name as {formatted_name}.")
            return formatted_name
        
        return "Unknown"
    
    def listen_with_confidence(self, timeout: int = 30, min_confidence: float = 0.5) -> str:
        """Enhanced confidence-based listening with natural conversation flow."""
        attempts = 0
        max_attempts = MAX_RETRY_ATTEMPTS  # From config (now 1 for more natural feel)
        
        while attempts < max_attempts:
            # Use hybrid engine if available
            if hasattr(self, 'use_hybrid_engine') and self.use_hybrid_engine:
                try:
                    transcription = self.speech_engine.listen_with_confidence(timeout, min_confidence)
                    return transcription
                except Exception as e:
                    logger.warning(f"Hybrid engine confidence listening failed: {e}")
                    # Fall through to original implementation
            
            # Original implementation with confidence calculation
            transcription = self.listen(timeout)
            confidence = self.calculate_confidence(transcription)
            
            print(f"🎯 Confidence: {confidence:.2f}")
            
            # More lenient confidence threshold and better messaging
            if confidence >= min_confidence or not transcription or len(transcription.split()) >= 3:
                return transcription
                
            if attempts < max_attempts - 1:
                # More natural, encouraging language
                self.speak("I want to make sure I understand you correctly. Could you say that once more?")
            attempts += 1
        
        return transcription
    
    def calculate_confidence(self, transcription: str) -> float:
        """Calculate confidence score for transcription based on various factors."""
        if not transcription:
            return 0.0
        
        confidence = CONFIDENCE_WEIGHTS['base_confidence']
        
        # Length factor - longer responses generally more reliable
        word_count = len(transcription.split())
        if word_count >= 5:
            confidence += CONFIDENCE_WEIGHTS['length_bonus']
        elif word_count >= 3:
            confidence += CONFIDENCE_WEIGHTS['length_bonus'] / 2
        
        # Check for common filler words that might indicate uncertainty
        filler_count = sum(1 for word in transcription.lower().split() if word in FILLER_WORDS)
        confidence -= min(filler_count * CONFIDENCE_WEIGHTS['filler_penalty'], 
                         CONFIDENCE_WEIGHTS['max_filler_penalty'])
        
        # Check for complete sentences
        if transcription.endswith('.') or transcription.endswith('!') or transcription.endswith('?'):
            confidence += CONFIDENCE_WEIGHTS['sentence_bonus']
        
        return max(0.0, min(1.0, confidence))
    
    def confirm_name_spelling(self, transcribed_name: str) -> str:
        """Confirm name spelling with candidate, especially for non-English names."""
        potential_names = []
        
        # Try to extract name using regex for patterns like "my name is..."
        name_match = re.search(r"(?:my name is|I'm|I am)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)", transcribed_name, re.IGNORECASE)
        if name_match:
            # Capitalize the extracted name properly
            potential_names = [name.title() for name in name_match.group(1).split()]

        # If regex fails, fall back to looking for capitalized words
        if not potential_names:
            words = transcribed_name.split()
            for word in words:
                if word.istitle() and len(word) > 2:
                    potential_names.append(word)

        if not potential_names:
            # If still no name found, ask for spelling
            self.speak("I want to make sure I get your name right. Could you please spell your first name letter by letter?")
            spelled_name = self.listen(timeout=30)
            return self.process_spelled_name(spelled_name)
        
        # If we found potential names, confirm them
        name_to_confirm = " ".join(potential_names[:2])  # Take first two potential names
        self.speak(f"I heard your name as {name_to_confirm}. Is that correct? Please say yes or no.")
        confirmation = self.listen(timeout=15)
        
        if "no" in confirmation.lower() or "wrong" in confirmation.lower() or "incorrect" in confirmation.lower():
            self.speak("I apologize. Could you please spell your name letter by letter, with a pause between each letter?")
            spelled_name = self.listen(timeout=30)
            return self.process_spelled_name(spelled_name)
        
        return name_to_confirm
    
    def process_spelled_name(self, spelled_input: str) -> str:
        """Process letter-by-letter spelled name input."""
        if not spelled_input:
            return "Unknown"
        
        words = spelled_input.lower().split()
        letters = []
        
        for word in words:
            if word in LETTER_MAPPINGS:
                letters.append(LETTER_MAPPINGS[word])
            elif len(word) == 1 and word.isalpha():
                letters.append(word.upper())
        
        if letters:
            constructed_name = ''.join(letters)
            # Capitalize first letter and make rest lowercase for proper name format
            formatted_name = constructed_name[0].upper() + constructed_name[1:].lower()
            self.speak(f"Thank you. I have your name as {formatted_name}.")
            return formatted_name
        
        return "Unknown"
    
    def listen_with_confidence(self, timeout: int = TIMEOUT_DEFAULT, min_confidence: float = MIN_CONFIDENCE) -> str:
        """Listen with confidence scoring and retry logic."""
        attempts = 0
        max_attempts = MAX_RETRY_ATTEMPTS
        
        while attempts < max_attempts:
            transcription = self.listen(timeout)
            confidence = self.calculate_confidence(transcription)
            
            print(f"🎯 Confidence: {confidence:.2f}")
            
            if confidence >= min_confidence or not transcription:
                return transcription
                
            if attempts < max_attempts - 1:
                self.speak("I didn't catch that clearly. Could you repeat that please?")
            attempts += 1
        
        return transcription
    
    def analyze_answer(self, question: str, answer: str) -> bool:
        """
        Analyze if the answer is clear and relevant to the question.
        Returns True if the answer is acceptable, False otherwise.
        """
        if not answer or len(answer.split()) < 3:
            return False
        
        prompt = f"""
        Human: Analyze if this answer is clear and relevant to the question.
        Question: "{question}"
        Answer: "{answer}"
        Is this answer clear and relevant? Answer with YES or NO only.
        
        Assistant:
        """
        
        response = self.llm_query(prompt)
        return "YES" in response.upper()
    
    def check_faq(self, query: str) -> Optional[str]:
        """
        Check if the query matches any FAQ and return the answer.
        Returns None if no match is found.
        """
        if not self.faq_data.get("faqs"):
            return None
        
        prompt = f"""
        Human: I need to check if this query matches any of the following FAQs. If it does, return the number of the matching FAQ. If not, return "NONE".

        Query: "{query}"
        
        FAQs:
        {json.dumps(self.faq_data["faqs"], indent=2)}
        
        Which FAQ number (1, 2, 3, etc.) matches this query? Answer with just the number or "NONE".
        
        Assistant:
        """
        
        response = self.llm_query(prompt)
        
        # Extract a number from the response if present
        match = re.search(r'\b(\d+)\b', response)
        if match and not "NONE" in response.upper():
            faq_index = int(match.group(1)) - 1
            if 0 <= faq_index < len(self.faq_data["faqs"]):
                return self.faq_data["faqs"][faq_index]["answer"]
        
        return None
    
    def conduct_interview(self):
        """Conduct the full interview with all questions."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_file = TRANSCRIPTS_DIR_PATH / f"transcript_{timestamp}.txt"
        
        # Introduction
        self.speak("Hello, I'm the LunarTech Interview Agent. I'll be conducting a short interview with you today. Let's get started.")
        
        # Open transcript file
        with open(transcript_file, 'w') as transcript:
            transcript.write(f"LunarTech Interview - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Ask each question
            for i, question in enumerate(QUESTIONS):
                self.speak(question)
                transcript.write(f"Q{i+1}: {question}\n")
                
                # Listen for answer with enhanced processing for first question (name)
                if i == 0:  # First question is about name
                    answer = self.listen_with_confidence(timeout=25)  # Extended timeout for names
                    if answer:
                        # Confirm name spelling for first question
                        self.candidate_name = self.confirm_name_spelling(answer)
                        # Update answer with confirmed name if different
                        if self.candidate_name != "Unknown" and self.candidate_name.lower() not in answer.lower():
                            answer = f"{self.candidate_name}. {answer}"
                else:
                    answer = self.listen_with_confidence()
                
                current_time = datetime.datetime.now().strftime('%H:%M:%S')
                transcript.write(f"A{i+1} [{current_time}]: {answer}\n\n")
                
                # If answer is unclear, ask for clarification (more naturally)
                if not self.analyze_answer(question, answer) and len(answer.split()) < 3:
                    # More natural, encouraging clarification request
                    clarification = f"I want to make sure I capture your response accurately. Could you tell me a bit more about that?"
                    self.speak(clarification)
                    transcript.write(f"Clarification: {clarification}\n")
                    
                    # Listen for clarified answer with more patience
                    clarified_answer = self.listen_with_confidence(timeout=35)  # Extra time for clarification
                    current_time = datetime.datetime.now().strftime('%H:%M:%S')
                    transcript.write(f"Clarified A{i+1} [{current_time}]: {clarified_answer}\n\n")
                    
                    # Use the clarified answer if it's better, otherwise keep original
                    if len(clarified_answer.split()) >= 3:  # More lenient check
                        answer = clarified_answer
                
                # Store the answer
                self.interview_data["answers"].append(answer)
            
            # Check if candidate has questions
            self.speak("Thank you for your responses. Do you have any questions for me about LunarTech or the program?")
            transcript.write("Agent: Thank you for your responses. Do you have any questions for me about LunarTech or the program?\n")
            
            # Handle FAQ questions
            while True:
                question = self.listen(timeout=TIMEOUT_FAQ)
                if not question or "no" in question.lower() or "thank you" in question.lower():
                    self.speak("Great! That concludes our interview. Thank you for your time.")
                    transcript.write("Agent: Great! That concludes our interview. Thank you for your time.\n")
                    break
                
                current_time = datetime.datetime.now().strftime('%H:%M:%S')
                transcript.write(f"Candidate [{current_time}]: {question}\n")
                
                # Check against FAQ
                faq_answer = self.check_faq(question)
                if faq_answer:
                    self.speak(faq_answer)
                    transcript.write(f"Agent: {faq_answer}\n\n")
                else:
                    self.speak("I've made a note of your question for the team because I don't have any specific information on that.")
                    transcript.write("Agent: I don't have specific information on that, but I'll make note of your question for the team.\n\n")
                
                self.speak("Do you have any other questions?")
                transcript.write("Agent: Do you have any other questions?\n")
        
        # Create summary and extracted info
        self.generate_summary(self.candidate_name)
        self.save_outputs(timestamp)
        
        logger.info(f"Interview completed and saved with timestamp {timestamp}")
    
    def generate_summary(self, candidate_name: str):
        """Generate a summary of the interview and extract structured information."""
        # Prepare the interview data for the LLM
        interview_text = ""
        for i, (question, answer) in enumerate(zip(QUESTIONS, self.interview_data["answers"])):
            interview_text += f"Question {i+1}: {question}\nAnswer {i+1}: {answer}\n\n"
        
        # Generate a summary using the LLM
        summary_prompt = f"""
        Human: Below is an interview with a candidate named '{candidate_name}' for LunarTech's program. Please provide:
        1. A concise summary of the interview (3-4 paragraphs)
        2. Structured information in JSON format with these fields:
           - name (the candidate's full name, which is '{candidate_name}')
           - interest_level (high/medium/low based on their reason for joining)
           - readiness (high/medium/low based on their stated readiness)
           - background (a brief description of their background and experience)

        Interview transcript:
        {interview_text}

        First provide the summary, then on a new line after "JSON_DATA:" provide only the JSON object as requested.
        
        Assistant:
        """
        
        llm_response = self.llm_query(summary_prompt)
        
        # Split the response to get summary and JSON separately
        parts = llm_response.split("JSON_DATA:")
        if len(parts) >= 2:
            self.interview_data["summary"] = parts[0].strip()
            
            # Extract and parse JSON data
            try:
                json_text = parts[1].strip()
                # Clean up any markdown formatting
                json_text = re.sub(r'```json|```', '', json_text).strip()
                extracted_info = json.loads(json_text)
                # Ensure the correct name is set
                if 'name' not in extracted_info or extracted_info['name'] in ["Candidate", "Unknown"]:
                    extracted_info['name'] = candidate_name
                self.interview_data["extracted_info"] = extracted_info
            except Exception as e:
                logger.error(f"Error parsing JSON from LLM response: {e}")
                self.interview_data["extracted_info"] = {
                    "name": "Unknown",
                    "interest_level": "unknown",
                    "readiness": "unknown",
                    "background": "Could not extract information"
                }
        else:
            self.interview_data["summary"] = llm_response
            self.interview_data["extracted_info"] = {
                "name": "Unknown",
                "interest_level": "unknown",
                "readiness": "unknown",
                "background": "Could not extract information"
            }
    
    def save_outputs(self, timestamp: str):
        """Save the interview outputs to files."""
        # Save summary as markdown
        summary_md_file = SUMMARIES_DIR_PATH / f"summary_{timestamp}.md"
        with open(summary_md_file, 'w') as f:
            f.write(f"# Interview Summary - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(self.interview_data["summary"])
            f.write("\n\n## Extracted Information\n\n")
            for key, value in self.interview_data["extracted_info"].items():
                f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
        
        # Save structured data as JSON
        summary_json_file = SUMMARIES_DIR_PATH / f"summary_{timestamp}.json"
        with open(summary_json_file, 'w') as f:
            json.dump(self.interview_data, f, indent=2)
        
        # Optionally save to SQLite database
        self.save_to_database(timestamp)
    
    def save_to_database(self, timestamp: str):
        """Save interview data to SQLite database."""
        try:
            db_path = Path(DATABASE_FILE)
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS interviews (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                summary TEXT
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interview_id TEXT,
                question_number INTEGER,
                question TEXT,
                answer TEXT,
                FOREIGN KEY (interview_id) REFERENCES interviews (id)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_info (
                interview_id TEXT PRIMARY KEY,
                name TEXT,
                interest_level TEXT,
                readiness TEXT,
                background TEXT,
                FOREIGN KEY (interview_id) REFERENCES interviews (id)
            )
            ''')
            
            # Insert interview data
            cursor.execute(
                "INSERT INTO interviews (id, timestamp, summary) VALUES (?, ?, ?)",
                (timestamp, self.interview_data["timestamp"], self.interview_data["summary"])
            )
            
            # Insert questions and answers
            for i, (question, answer) in enumerate(zip(QUESTIONS, self.interview_data["answers"])):
                cursor.execute(
                    "INSERT INTO questions_answers (interview_id, question_number, question, answer) VALUES (?, ?, ?, ?)",
                    (timestamp, i+1, question, answer)
                )
            
            # Insert extracted info
            extracted = self.interview_data["extracted_info"]
            cursor.execute(
                "INSERT INTO extracted_info (interview_id, name, interest_level, readiness, background) VALUES (?, ?, ?, ?, ?)",
                (
                    timestamp,
                    extracted.get("name", "Unknown"),
                    extracted.get("interest_level", "unknown"),
                    extracted.get("readiness", "unknown"),
                    extracted.get("background", "")
                )
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Interview data saved to database with ID: {timestamp}")
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    def get_interview_statistics(self) -> Dict[str, Any]:
        """Get interview statistics from the database."""
        try:
            db_path = Path(DATABASE_FILE)
            if not db_path.exists():
                return {"total_interviews": 0, "today_interviews": 0, "avg_interest": "N/A"}
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Total interviews
            cursor.execute("SELECT COUNT(*) FROM interviews")
            total_interviews = cursor.fetchone()[0]
            
            # Today's interviews
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM interviews WHERE DATE(timestamp) = ?", (today,))
            today_interviews = cursor.fetchone()[0]
            
            # Average interest level
            cursor.execute("SELECT interest_level FROM extracted_info WHERE interest_level != 'unknown'")
            interest_levels = cursor.fetchall()
            
            if interest_levels:
                high_count = sum(1 for level in interest_levels if level[0] == 'high')
                medium_count = sum(1 for level in interest_levels if level[0] == 'medium')
                low_count = sum(1 for level in interest_levels if level[0] == 'low')
                
                total = len(interest_levels)
                avg_score = (high_count * 3 + medium_count * 2 + low_count * 1) / total
                
                if avg_score >= 2.5:
                    avg_interest = "High"
                elif avg_score >= 1.5:
                    avg_interest = "Medium"
                else:
                    avg_interest = "Low"
            else:
                avg_interest = "N/A"
            
            conn.close()
            
            return {
                "total_interviews": total_interviews,
                "today_interviews": today_interviews,
                "avg_interest": avg_interest,
                "interest_distribution": {
                    "high": high_count if interest_levels else 0,
                    "medium": medium_count if interest_levels else 0,
                    "low": low_count if interest_levels else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total_interviews": 0, "today_interviews": 0, "avg_interest": "N/A"}
    
    def generate_dashboard(self):
        """Generate HTML dashboard with interview statistics."""
        stats = self.get_interview_statistics()
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LunarTech Interview Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }}
                .stat-card {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .stat-number {{
                    font-size: 3em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .stat-label {{
                    font-size: 1.2em;
                    opacity: 0.9;
                }}
                .interest-chart {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .bar {{
                    display: flex;
                    align-items: center;
                    margin: 15px 0;
                }}
                .bar-label {{
                    width: 80px;
                    text-transform: capitalize;
                }}
                .bar-fill {{
                    height: 25px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 12px;
                    margin: 0 15px;
                    flex: 1;
                    position: relative;
                }}
                .bar-progress {{
                    height: 100%;
                    border-radius: 12px;
                    transition: width 0.5s ease;
                }}
                .high {{ background: #4CAF50; }}
                .medium {{ background: #FF9800; }}
                .low {{ background: #F44336; }}
                .timestamp {{
                    text-align: center;
                    margin-top: 40px;
                    opacity: 0.7;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 LunarTech Interview Dashboard</h1>
                    <p>Real-time interview analytics and candidate insights</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_interviews']}</div>
                        <div class="stat-label">Total Interviews</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['today_interviews']}</div>
                        <div class="stat-label">Today's Interviews</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['avg_interest']}</div>
                        <div class="stat-label">Average Interest</div>
                    </div>
                </div>
                
                <div class="interest-chart">
                    <h2>Interest Level Distribution</h2>
        """
        
        # Add interest level bars if we have data
        if stats.get('interest_distribution'):
            total = sum(stats['interest_distribution'].values())
            if total > 0:
                for level, count in stats['interest_distribution'].items():
                    percentage = (count / total) * 100
                    html_content += f"""
                    <div class="bar">
                        <div class="bar-label">{level.title()}</div>
                        <div class="bar-fill">
                            <div class="bar-progress {level}" style="width: {percentage}%"></div>
                        </div>
                        <div>{count} ({percentage:.1f}%)</div>
                    </div>
                    """
            else:
                html_content += "<p>No interview data available yet.</p>"
        
        html_content += f"""
                </div>
                
                <div class="timestamp">
                    Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """
        
        dashboard_file = Path(DASHBOARD_FILE)
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 Dashboard generated: {dashboard_file.absolute()}")
        return dashboard_file


def main():
    """Main function to run the interview agent."""
    try:
        print("🚀 Starting LunarTech AI Interview Agent...")
        agent = InterviewAgent()
        
        # Generate dashboard before starting interview
        agent.generate_dashboard()
        
        # Conduct the interview
        agent.conduct_interview()
        
        # Generate updated dashboard after interview
        agent.generate_dashboard()
        
        print("✅ Interview completed successfully!")
        print("📊 Dashboard updated with latest data")
        
    except KeyboardInterrupt:
        print("\n❌ Interview interrupted by user")
    except Exception as e:
        logger.error(f"Error during interview: {e}")
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\nThank you for using the LunarTech Interview Agent.")
