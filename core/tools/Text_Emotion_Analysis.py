from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List
import json
from llm_object import llm
import re

TAXONOMIES = {
    "ekman": ["anger", "disgust", "fear", "joy", "sadness", "surprise"],
    "plutchik": ["joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"],
    "therapy": ["burnout", "hope", "anxiety", "gratitude", "overwhelm", "isolation"]
}


class EmotionResult(BaseModel):
    taxonomy: str
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class EmotionAnalysisOutput(BaseModel):
    input_text: str
    results: List[EmotionResult]


def extract_json_from_code_block(content: str) -> dict:
    """
    Extract JSON from markdown-style code block returned by Gemini LLM.
    """
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return json.loads(content)

def analyze_emotions(text: str) -> EmotionAnalysisOutput:

    all_results = []

    for taxonomy, labels in TAXONOMIES.items():
        prompt = f"""
            Given the following text: "{text}"

            Choose the most appropriate emotion from this list: {labels}

            Return:
            1. The predicted emotion label
            2. Confidence (between 0 and 1, approximate)
            3. A short explanation for your choice

            Respond strictly in this JSON format:
            {{
            "label": "...",
            "confidence": <confidence_value>,
            "explanation": "..."
            }}
        """.strip()

        output = llm.invoke(prompt)

        try:
            data = extract_json_from_code_block(output.content)
            result = EmotionResult(
                taxonomy=taxonomy,
                label=data["label"],
                confidence=float(data["confidence"]),
                explanation=data["explanation"]
            )
            all_results.append(result)

        except Exception as e:
            raise ValueError(f"Failed to parse LLM output for taxonomy '{taxonomy}': {output.content}") from e

    return EmotionAnalysisOutput(input_text=text, results=all_results)

