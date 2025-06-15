from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from services.mcp_server.server import mcp

model_name = "j-hartmann/emotion-english-distilroberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

@mcp.tool(name="Text Emotion")
def detect_emotion(text: str) -> dict:
    """
    Detects the emotion expressed in the given input text using a DistilRoBERTa model
    fine-tuned on the GoEmotions dataset.

    Parameters:
        text (str): The input text to analyze.

    Returns:
        dict: Contains the predicted emotion label and confidence scores for each class.
    """
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1)
        predicted_class = torch.argmax(probs).item()
        label = model.config.id2label[predicted_class]

    scores = {
        model.config.id2label[i]: float(p)
        for i, p in enumerate(probs.squeeze())
    }

    return {
        "text": text,
        "predicted_label": label,
        "scores": scores
    }
