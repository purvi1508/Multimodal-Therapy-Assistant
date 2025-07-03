from services.mcp_server.server import mcp
from speechbrain.inference.interfaces import foreign_class

classifier = foreign_class(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    classname="EncoderWav2vec2Classifier"
)

@mcp.tool(name="Speech Emotion Detection")
def detect_emotion_from_speech(audio_path: str) -> dict:
    """
    Detects emotion in a given speech audio file.

    Parameters:
        audio_path (str): Path to a .wav file (mono, 16kHz).

    Returns:
        dict: Predicted emotion label and confidence score.
    """
    try:
        out_prob, score, index, text_lab = classifier.classify_file(audio_path)
        return {
            "predicted_emotion": text_lab[0],
            "confidence_score": float(score)
        }
    except Exception as e:
        return {"error": f"Failed to analyze emotion: {str(e)}"}
