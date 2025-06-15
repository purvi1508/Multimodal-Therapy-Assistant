import os
import tempfile
import requests
from deepface import DeepFace
from services.mcp_server.server import mcp
from typing import Union

@mcp.tool(name="Facial Emotion")
def detect_facial_emotion(image: Union[str, bytes]) -> dict:
    """
    Detects the dominant facial emotion in an image using DeepFace.
    Accepts either a file path, URL, or raw image upload.

    Parameters:
        image (str or bytes): Path to image file, URL to an image, or image file bytes.

    Returns:
        dict: Contains the dominant emotion and full emotion score breakdown.
    """

    if isinstance(image, bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(image)
            img_path = tmp_file.name

    elif isinstance(image, str) and image.startswith("http"):
        response = requests.get(image)
        if response.status_code != 200:
            raise ValueError(f"Could not fetch image from URL: {image}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(response.content)
            img_path = tmp_file.name

    elif isinstance(image, str) and os.path.exists(image):
        img_path = image

    else:
        raise ValueError("Invalid image input. Provide a valid file path, URL, or image bytes.")

    analysis = DeepFace.analyze(img_path=img_path, actions=["emotion"])
    dominant_emotion = analysis[0]["dominant_emotion"]
    emotion_scores = analysis[0]["emotion"]

    if not (isinstance(image, str) and os.path.exists(image)):
        os.remove(img_path)

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_scores": emotion_scores
    }
