import os
import tempfile
import requests
import imghdr
from deepface import DeepFace
from services.mcp_server.server import mcp
from typing import Union

@mcp.tool(name="Facial Emotion, Age & Gender")
def detect_facial_attributes(image: Union[str, bytes]) -> dict:
    """
    Detects facial attributes (emotion, age, gender) using DeepFace.
    Supports local file path, image URL, or raw image bytes.

    Parameters:
        image (str or bytes): Image file path, URL, or raw bytes.

    Returns:
        dict: {
            dominant_emotion: str,
            emotion_scores: dict,
            age: int,
            gender: str
        }

    Raises:
        ValueError: If input is invalid or no face is detected.
    """

    temp_file = None
    img_path = None

    try:
        if isinstance(image, bytes):
            image_type = imghdr.what(None, h=image)
            if image_type not in {"jpeg", "png", "bmp", "gif", "tiff", "webp"}:
                raise ValueError(f"Unsupported image format: {image_type}")

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{image_type}")
            temp_file.write(image)
            temp_file.close()
            img_path = temp_file.name

        elif isinstance(image, str) and image.startswith("http"):
            response = requests.get(image)
            if response.status_code != 200:
                raise ValueError(f"Could not fetch image from URL: {image}")
            ext = os.path.splitext(image)[-1].lower().strip(".")
            ext = ext if ext in {"jpeg", "jpg", "png", "bmp", "gif", "tiff", "webp"} else "jpg"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
            temp_file.write(response.content)
            temp_file.close()
            img_path = temp_file.name

        elif isinstance(image, str) and os.path.exists(image):
            img_path = image

        else:
            raise ValueError("Invalid image input. Must be file path, URL, or raw bytes.")

        analysis = DeepFace.analyze(
            img_path=img_path,
            actions=["emotion", "age", "gender"],
            enforce_detection=True
        )
        result = analysis[0]

        return {
            "dominant_emotion": result.get("dominant_emotion"),
            "emotion_scores": result.get("emotion"),
            "age": result.get("age"),
            "gender": result.get("gender")
        }

    except ValueError as ve:
        raise ValueError(f"Face analysis error: {str(ve)}")
    except Exception as e:
        raise ValueError(f"Unexpected error during face analysis: {str(e)}")
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)
