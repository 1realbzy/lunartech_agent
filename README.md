# LunarTech Offline AI Interview Agent (MVP)

This project is a Minimum Viable Product (MVP) of an offline AI-powered interview agent for LunarTech. It conducts a 5-question interview using voice, transcribes the answers, and generates a summary and structured JSON output. The entire system is designed to run locally without any internet connection.

## Features

- **Offline Voice-to-Text:** Uses the Vosk library for speech recognition.
- **Offline Text-to-Speech:** Uses the pyttsx3 library for voice responses.
- **Local LLM Integration:** Uses a local Large Language Model (Llama 2 7B Chat or GPT4All) for dialogue, summarization, and JSON extraction.
- **Automated Interview Flow:** Asks a predefined set of 5 interview questions covering:
  - Full name and background
  - Reason for joining LunarTech
  - Data Science and AI experience
  - Future goals
  - Readiness for the program
- **FAQ Handling:** Responds to basic FAQ queries using a local JSON file.
- **Output Generation:** 
  - Detailed transcript with timestamps
  - Summary in Markdown format
  - Structured JSON with extracted candidate information
  - Optional SQLite database storage

## Project Structure

```
main.py                 # Main application script with hybrid Whisper+Vosk
config.py               # Centralized configuration settings
utils.py                # Database management and utility functions
README.md               # Project documentation
requirements.txt        # Python dependencies (includes Whisper)
dashboard.html          # Real-time analytics dashboard (auto-generated)
download_models.py      # Model download utility
data/
  ├── faq.json          # Frequently asked questions and answers
  ├── interviews.db     # SQLite database (created on first run)
  ├── summaries/        # Interview summaries in MD and JSON formats
  └── transcripts/      # Detailed interview transcripts
models/                 # Directory for speech recognition models
  ├── vosk-model-xx/    # Downloaded Vosk model (fallback)
  └── whisper models/   # Whisper models (auto-downloaded)
ENHANCEMENTS.md         # Technical enhancements documentation
IMPLEMENTATION_SUMMARY.md # Complete implementation overview
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- 16GB RAM (minimum 8GB, but may experience performance issues)
- Microphone for speech input
- Speakers for audio output

### 2. Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/Lunartech_agent.git
   cd Lunartech_agent
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Note: PyAudio installation may require additional system libraries on Linux/macOS. See [PyAudio documentation](https://people.csail.mit.edu/hubert/pyaudio/) for details.

### 3. Download Required Models

#### Option 1: Using the Download Script (Recommended)

The easiest way to download the required models is to use the provided download script:

```bash
# Download recommended models (Vosk small + Llama 7B)
python download_models.py

# For systems with less RAM
python download_models.py --llm llama_small

# For a larger, more accurate speech model
python download_models.py --vosk large

# To see all options
python download_models.py --help
```

#### Option 2: Manual Download

Alternatively, you can download the models manually:

##### Vosk Speech Recognition Model

1. Download a Vosk model from [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
   - For English, the `vosk-model-small-en-us-0.15` is recommended for a balance of accuracy and size (~40MB)
   - Larger models like `vosk-model-en-us-0.22` provide better accuracy but require more RAM (~1.8GB)

2. Extract the downloaded model to the `models/` directory

##### Local Language Model

Llama 2 7B Chat (Recommended)
1. Download the GGUF format of Llama 2 7B Chat from [HuggingFace](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF)
2. Recommended file: `llama-2-7b-chat.Q4_0.gguf` (~4GB - provides good balance of quality and performance)
3. For systems with less RAM: `llama-2-7b-chat.Q2_K.gguf` (~2.9GB)
4. Place the downloaded GGUF file in the `models/` directory

For more detailed instructions, see the [MODEL_DOWNLOAD_GUIDE.md](models/MODEL_DOWNLOAD_GUIDE.md) in the models directory.

### 4. Running the Application

1. Ensure your microphone and speakers are connected and working
2. Run the application:

   ```bash
   python main.py
   ```

3. The agent will:
   - Initialize speech recognition, text-to-speech, and the LLM
   - Greet you and begin the interview
   - Ask 5 questions, listening for your spoken responses
   - Ask if you have any questions (you can test FAQ functionality here)
   - Generate a summary and save all outputs

## Customization

### Interview Questions

To customize the interview questions, modify the `QUESTIONS` list in `main.py`:

```python
QUESTIONS = [
    "Your first question here.",
    "Your second question here.",
    # ...
]
```

### FAQ Database

Edit the `data/faq.json` file to add, remove, or modify FAQ entries:

```json
{
  "faqs": [
    {
      "question": "Your question here?",
      "answer": "Your answer here."
    },
    // Add more FAQ entries...
  ]
}
```

### LLM Parameters

You can adjust the LLM parameters in the `initialize_llm` method in `main.py`:

```python
# For Llama models
self.llm = Llama(
    model_path=model_path,
    n_ctx=2048,      # Context length
    n_batch=512,     # Batch size
    n_threads=4      # Number of CPU threads
)

# For GPT4All models
self.llm = GPT4All(model_path)
```

## Troubleshooting

### Speech Recognition Issues

- Ensure your microphone is properly connected and set as the default input device
- Try using a headset microphone for better quality
- If speech recognition is poor, download a larger Vosk model for better accuracy

### LLM Performance Issues

- If the application is slow or crashes, try using a smaller quantized model
- Reduce the `n_ctx` parameter if you encounter memory issues
- Ensure you have at least 8GB of available RAM (16GB recommended)

### Output Files

- All output files are stored in the `data/transcripts/` and `data/summaries/` directories
- Each interview session creates files with a unique timestamp
- The SQLite database (`data/interviews.db`) contains all interview data for easy querying

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for the offline speech recognition technology
- [Llama 2](https://ai.meta.com/llama/) from Meta AI for the local language model
- [GPT4All](https://gpt4all.io/) for local AI capabilities
