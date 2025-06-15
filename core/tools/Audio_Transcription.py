from services.mcp_server.server import mcp
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import torchaudio

processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
model.eval()

@mcp.tool(name="Audio Transcription")
def asr_transcriber(audio_path: str) -> str:
    """
    Transcribes speech from an audio file using Wav2Vec2.

    Args:
        audio_path (str): Path to the input audio file.

    Returns:
        str: Transcribed text.
    """

    def load_audio(file_path):
        waveform, sr = torchaudio.load(file_path)
        if waveform.shape[0] > 1:  
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        if sr != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
            waveform = resampler(waveform)
        return waveform.squeeze()

    waveform = load_audio(audio_path)
    inputs = processor(waveform, return_tensors="pt", sampling_rate=16000)
    
    with torch.no_grad():
        logits = model(inputs.input_values).logits
    
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.decode(predicted_ids[0])
    return transcription
