import os
import sys
from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models.file import File

def transcribe_audio(api_key, file_path, model="voxtral-mini-latest"):
    """
    Transcribes an audio file using the Mistral AI API.

    Args:
        api_key (str): Your Mistral AI API key.
        file_path (str): The path to the audio file.
        model (str): The model to use for transcription.

    Returns:
        str: The transcribed text.
    """
    try:
        with Mistral(api_key=api_key) as client:
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_obj = File(file_name=os.path.basename(file_path), content=file_data)
                response = client.audio.transcriptions.complete(
                    model=model,
                    file=file_obj
                )
            return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set in environment or .env file.")

    if len(sys.argv) < 2:
        print("Usage: python transcribe_audio.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]

    transcribed_text = transcribe_audio(api_key, file_path)

    output_file_path = os.path.splitext(file_path)[0] + ".txt"

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(transcribed_text)

    print(f"Transcription saved to: {output_file_path}")
