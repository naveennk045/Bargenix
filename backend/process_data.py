import re
import json
import os
import spacy
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")



def preprocess_text(text: str) -> str:
    doc = nlp(text.lower())
    tokens = [token.text for token in doc if not token.is_punct]
    cleaned_text = " ".join(tokens)
    cleaned_text = re.sub(r"[^\w\s$]", "", cleaned_text) 
    return cleaned_text

def convert_raw_text_to_json(input_file: str, output_file: str) -> List[Dict[str, str]]:
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
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

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=4, ensure_ascii=False)

        return conversation

    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "data", "raw.txt")
    output_file = os.path.join(base_dir, "data", "negotiation_data.json")

    try:
        conversation = convert_raw_text_to_json(input_file, output_file)
        print(f"Successfully converted {len(conversation)} conversation pairs")
        print(f"Output saved to: {output_file}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
