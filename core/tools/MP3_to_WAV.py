from pydub import AudioSegment
import os

def convert_mp3_to_wav(input_path: str, output_path: str = None) -> str:
    """
    Converts an MP3 file to WAV format using pydub.
    
    Args:
        input_path (str): Path to the .mp3 file
        output_path (str): Optional path to save .wav (default: same name)

    Returns:
        str: Path to the .wav file
    """
    if not output_path:
        output_path = os.path.splitext(input_path)[0] + ".wav"

    audio = AudioSegment.from_mp3(input_path)
    audio.export(output_path, format="wav")
    return output_path
