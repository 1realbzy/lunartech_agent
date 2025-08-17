# Models Directory

This directory should contain the following models:

## 1. Speech Recognition Model (Vosk)

Download one of the following models from [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models):

- **Small English Model (Recommended for most users):**
  - `vosk-model-small-en-us-0.15` (~40MB)
  - Good balance of accuracy and resource usage

- **Complete English Model (Better accuracy, more resources):**
  - `vosk-model-en-us-0.22` (~1.8GB)
  - Higher accuracy but requires more memory

Extract the downloaded model archive into this directory, maintaining the original folder structure.

## 2. Language Model (LLM)

You have two options:

### Option 1: Llama 2 (Recommended)

Download the GGUF format of Llama 2 7B Chat from [HuggingFace](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF):

- **Recommended file:** `llama-2-7b-chat.Q4_0.gguf` (~4GB)
  - Good balance of quality and performance on 16GB RAM systems

- **For systems with less RAM:** `llama-2-7b-chat.Q3_K_M.gguf` (~3GB)
  - Slightly lower quality but works better on systems with 8GB RAM

Place the downloaded GGUF file directly in this directory.

### Option 2: GPT4All

Download a model from [GPT4All's model list](https://gpt4all.io/models/models.json):

- **Recommended:** `orca-mini-3b-gguf2-q4_0.gguf` (~2GB)
  - Good for systems with limited RAM

Place the downloaded model file directly in this directory.

## Memory Requirements

- Ensure you have at least 8GB of available RAM
- 16GB RAM is recommended for optimal performance
- If using a system with 8GB RAM, choose the smaller model options

The application will automatically detect and use the models placed in this directory.
