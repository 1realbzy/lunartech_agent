# lunartech_agent
LunarTech AI Engineering assignment: local voice interview agent with offline STT, TTS, and summarization.

# 🎤 LunarTech Offline AI Interview Agent

> **An entirely offline, open-source voice interview system** — built as an MVP for the LunarTech AI Engineering & Data Science Intern Assignment.  
> Runs 100% locally using free, open-source tools — no cloud APIs, no paid services, no internet after setup.

---

## 📜 Project Overview

This project implements a **voice-powered AI Interview Agent** that conducts real-time, human-like interviews with candidates for the LunarTech AI/Data Science bootcamp.

The agent:
- 🎙️ **Speaks** questions to the candidate.
- 👂 **Listens** to spoken answers via offline STT.
- 🧠 Uses a **local LLM** to process and summarize responses.
- 📝 Saves all interactions in human- and machine-readable formats.

This follows **exactly** the requirements from the LunarTech assignment:
1. Conversational workflow with 5 specific questions.
2. Speech-to-Text and Text-to-Speech integration.
3. Real-time summarization.
4. Data logging and session memory.
5. Optional FAQ handling.

---

## 🎯 Core Features

### **1. Conversational Workflow**
- 5 mandatory questions:
  1. Full name & background
  2. Why are you interested in the program?
  3. Experience with data science or AI
  4. Short-term & long-term goals
  5. Are you ready to start immediately?
- Waits for responses, can rephrase if unclear.
- Tracks answers internally for summarization.

### **2. Offline Speech-to-Text (STT)**
- Uses **Vosk** (lightweight, ~40 MB model).
- No internet needed after download.

### **3. Offline Text-to-Speech (TTS)**
- Uses **pyttsx3** for local TTS across Windows, macOS, and Linux.

### **4. Real-Time Summarization**
- Local LLM (e.g., GPT4All or Llama 2 7B Chat quantized) creates:
  - Candidate profile summary.
  - Structured JSON output (name, interest, readiness, background).

### **5. Data Logging & Session Memory**
- Saves:
  - `transcript.txt` — full Q/A with timestamps.
  - `summary.md` — human-readable summary.
  - `summary.json` — machine-readable data.
  - Optional `session_logs.csv` — quick reference.

---

## 🛠️ Tech Stack

| Component        | Tool/Library         | Reason |
|------------------|----------------------|--------|
| Speech-to-Text   | [Vosk](https://alphacephei.com/vosk/) | Lightweight, offline, accurate |
| Text-to-Speech   | [pyttsx3](https://pyttsx3.readthedocs.io/) | Offline, cross-platform |
| LLM Engine       | [GPT4All](https://gpt4all.io/) or [llama.cpp](https://github.com/ggerganov/llama.cpp) | Runs locally without GPU |
| Orchestration    | Python               | Simple, modular, extensible |

---

## 📂 Folder Structure

lunartech_agent/
├── main.py
├── requirements.txt
├── README.md
├── models/
│ └── vosk-model-small-en-us-0.15/
├── data/
│ ├── transcripts/
│ ├── summaries/
│ ├── logs/
├── faq.json


---

## 🚀 Quick Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/1realbzy/lunartech_agent.git
   cd lunartech_agent
   
2. Create Virtual Environment
   python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

3. Install Requirements
   pip install -r requirements.txt

4. Download Vosk Model
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/

5. Run Agent
   python main.py

