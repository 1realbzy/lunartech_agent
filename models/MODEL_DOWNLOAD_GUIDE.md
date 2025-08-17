# LunarTech Interview Agent - Model Download Guide

This guide will help you download and set up the necessary models for the LunarTech Interview Agent.

## Required Models

The application requires two types of models:

1. **Speech Recognition Model (Vosk)** - For converting spoken interview answers to text
2. **Language Model (LLM)** - For analyzing responses, generating summaries, and extracting information

## 1. Speech Recognition Model (Vosk)

### Recommended Option: Small English Model

This model provides a good balance between accuracy and resource usage, ideal for most interview scenarios.

- **Model Name:** `vosk-model-small-en-us-0.15`
- **Size:** ~40MB
- **Download Link:** [https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)

### Alternative: Full English Model (Higher Accuracy)

If you need higher accuracy and have more RAM available, you can use this larger model.

- **Model Name:** `vosk-model-en-us-0.22`
- **Size:** ~1.8GB
- **Download Link:** [https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip](https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip)

### Installation Steps:

1. Download the zip file using one of the links above
2. Extract the contents of the zip file
3. Place the entire extracted folder in this `models/` directory
4. Ensure the folder name starts with "vosk" or contains "vosk" in its name

## 2. Language Model (LLM)

The application supports two types of language models: Llama (preferred) and GPT4All.

### Option 1: Llama 2 (Recommended for Best Results)

#### For 16GB RAM Systems:

- **Model Name:** `llama-2-7b-chat.Q4_0.gguf`
- **Size:** ~4GB
- **Download Link:** [https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_0.gguf](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_0.gguf)

#### For 8GB RAM Systems:

- **Model Name:** `llama-2-7b-chat.Q2_K.gguf`
- **Size:** ~2.9GB
- **Download Link:** [https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q2_K.gguf](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q2_K.gguf)

### Option 2: Smaller Alternative Models

If you need a smaller model that still performs well:

- **Model Name:** `orca-mini-3b-gguf2-q4_0.gguf`
- **Size:** ~2GB
- **Download Link:** [https://huggingface.co/TheBloke/orca_mini_3B-GGUF/resolve/main/orca-mini-3b-gguf2-q4_0.gguf](https://huggingface.co/TheBloke/orca_mini_3B-GGUF/resolve/main/orca-mini-3b-gguf2-q4_0.gguf)

### Installation Steps:

1. Download the model file using one of the links above
2. Place the downloaded file directly in this `models/` directory
3. No need to extract or rename the file

## Model Selection Logic

The application will automatically look for GGUF models (files with `.gguf` extension) and use the first suitable model it finds.

## Troubleshooting

- **Memory Issues:** If you encounter out-of-memory errors, try a smaller model
- **Slow Performance:** Reduce the `n_threads` parameter in the code if your CPU is overloaded
- **Model Not Found:** Ensure the model files are placed directly in this directory and have the correct file extensions

## Download Commands

If you're comfortable with the command line, you can use these commands to download the models:

### For Vosk Model:
```
# Download
curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o vosk-model.zip

# Extract
powershell Expand-Archive -Path vosk-model.zip -DestinationPath .

# Clean up
del vosk-model.zip
```

### For Llama Model:
```
curl -L https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_0.gguf -o llama-2-7b-chat.Q4_0.gguf
```
