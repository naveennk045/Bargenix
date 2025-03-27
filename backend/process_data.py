#  Import necessary libraries
import re
import json
import os
import spacy
import logging
from pathlib import Path
from typing import List, Dict

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

nlp = spacy.load("en_core_web_sm")

#  Preprocess text by lowercasing, removing punctuation except price symbols, and tokenizing.

def preprocess_text(text: str) -> str:
    
    doc = nlp(text.lower())
    tokens = [token.orth_ for token in doc if not token.is_punct]
    cleaned_text = " ".join(tokens)
    return re.sub(r"[^\w\s$]", "", cleaned_text)

# Convert raw chat text into structured JSON format.
def convert_raw_text_to_json(input_file: Path, output_file: Path) -> List[Dict[str, str]]:
   
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open('r', encoding='utf-8') as f:
        raw_text = f.read().strip()

    if not raw_text:
        raise ValueError("Input file is empty")

    conversation_parts = re.findall(r"(User|Bot):\s*(.+)", raw_text)

    if not conversation_parts:
        raise ValueError("Invalid conversation format")

    conversation: List[Dict[str, str]] = []
    temp_message = None

    for speaker, message in conversation_parts:
        message = preprocess_text(message)
        
        if speaker == "User":
            temp_message = message
        elif speaker == "Bot" and temp_message:
            conversation.append({
                "user_message": temp_message,
                "bot_response": message
            })
            temp_message = None

    if not conversation:
        raise ValueError("No valid conversation pairs found")

    with output_file.open('w', encoding='utf-8') as f:
        json.dump(conversation, f, indent=4, ensure_ascii=False)

    logging.info(f"Successfully converted {len(conversation)} conversation pairs")
    logging.info(f"Output saved to: {output_file}")

    return conversation

# Main function to convert raw text to JSON
def main():
    base_dir = Path(__file__).resolve().parent
    input_file = base_dir / "data" / "raw.txt"
    output_file = base_dir / "data" / "negotiation_data.json"

    try:
        convert_raw_text_to_json(input_file, output_file)
    except Exception as e:
        logging.error(f"Processing failed: {e}")

if __name__ == "__main__":
    main()
