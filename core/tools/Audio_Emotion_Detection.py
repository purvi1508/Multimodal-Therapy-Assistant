import os
import tempfile
from typing import Union
from speechbrain.inference.interfaces import foreign_class
from services.mcp_server.server import mcp

classifier = foreign_class(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    pymodule_file="custom_interface.py",
    classname="CustomEncoderWav2vec2Classifier"
)

label_map = {
    'ang': 'Angry',
    'hap': 'Happy',
    'sad': 'Sad',
    'neu': 'Neutral'
}

@mcp.tool(name="Speech Emotion")
def detect_audio_emotion(audio: Union[str, bytes]) -> dict:
    """
    Detects emotion from speech audio using a Wav2Vec2 model fine-tuned on IEMOCAP.

    Parameters:
        audio (str or bytes): File path to .wav file or raw audio bytes.

    Returns:
        dict: Contains predicted emotion label and raw model output scores.
    """
    if isinstance(audio, bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio)
            audio_path = tmp_file.name
    elif isinstance(audio, str) and os.path.exists(audio):
        audio_path = audio
    else:
        raise ValueError("Invalid audio input. Provide a valid file path or WAV byte stream.")

    out_prob, score, index, text_lab = classifier.classify_file(audio_path)
    label_code = text_lab[0]
    emotion = label_map.get(label_code, "Unknown")

    if not (isinstance(audio, str) and os.path.exists(audio)):
        os.remove(audio_path)

    return {
        "predicted_label": emotion,
        "label_code": label_code,
        "score": float(score),
        "probabilities": {
            label_map.get(classifier.hparams.label_encoder.decode_ndim([i])[0], f"Class_{i}"): float(prob)
            for i, prob in enumerate(out_prob)
        }
    }
