#!/usr/bin/env python3
# download_models.py - Script to download models for LunarTech Interview Agent

import os
import sys
import argparse
import urllib.request
import zipfile
import shutil
from pathlib import Path

def print_progress(count, block_size, total_size):
    """Display download progress."""
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\r{percent}% downloaded ({count * block_size / 1024 / 1024:.1f} MB of {total_size / 1024 / 1024:.1f} MB)")
    sys.stdout.flush()

def download_file(url, output_path):
    """Download a file with progress display."""
    print(f"Downloading {url} to {output_path}")
    urllib.request.urlretrieve(url, output_path, reporthook=print_progress)
    print("\nDownload complete!")

def extract_zip(zip_path, extract_dir):
    """Extract a zip file."""
    print(f"Extracting {zip_path} to {extract_dir}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("Extraction complete!")

def main():
    parser = argparse.ArgumentParser(description="Download models for LunarTech Interview Agent")
    parser.add_argument("--vosk", choices=["small", "large"], default="small", 
                        help="Vosk model size: 'small' (~40MB) or 'large' (~1.8GB)")
    parser.add_argument("--llm", choices=["llama_standard", "llama_small", "orca"], default="llama_standard",
                        help="LLM model: 'llama_standard' (~4GB), 'llama_small' (~2.9GB), or 'orca' (~2GB)")
    
    args = parser.parse_args()
    
    # Ensure models directory exists
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Download Vosk model
    if args.vosk == "small":
        vosk_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        vosk_zip = models_dir / "vosk-model-small-en-us-0.15.zip"
    else:
        vosk_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
        vosk_zip = models_dir / "vosk-model-en-us-0.22.zip"
    
    # Download LLM model
    if args.llm == "llama_standard":
        llm_url = "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_0.gguf"
        llm_file = models_dir / "llama-2-7b-chat.Q4_0.gguf"
    elif args.llm == "llama_small":
        llm_url = "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q2_K.gguf"
        llm_file = models_dir / "llama-2-7b-chat.Q2_K.gguf"
    else:  # orca
        llm_url = "https://huggingface.co/TheBloke/orca_mini_3B-GGUF/resolve/main/orca-mini-3b-gguf2-q4_0.gguf"
        llm_file = models_dir / "orca-mini-3b-gguf2-q4_0.gguf"
    
    # Download and extract Vosk model
    try:
        print("\n===== Downloading Vosk Speech Recognition Model =====")
        download_file(vosk_url, vosk_zip)
        extract_zip(vosk_zip, models_dir)
        # Remove zip file after extraction
        os.remove(vosk_zip)
    except Exception as e:
        print(f"Error downloading or extracting Vosk model: {e}")
        sys.exit(1)
    
    # Download LLM model
    try:
        print("\n===== Downloading Language Model =====")
        download_file(llm_url, llm_file)
    except Exception as e:
        print(f"Error downloading LLM model: {e}")
        sys.exit(1)
    
    print("\n===== All models downloaded successfully! =====")
    print(f"Vosk model: {models_dir / vosk_zip.stem}")
    print(f"LLM model: {llm_file}")
    print("\nYou can now run the LunarTech Interview Agent with:")
    print("python main.py")

if __name__ == "__main__":
    main()
