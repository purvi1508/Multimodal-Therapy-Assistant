import re
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from llm_object import llm

class RewrittenOutput(BaseModel):
    rewritten_text: str
    explanation: str

def extract_json(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return json.loads(content)

def adapt_tone(text: str, tone: str) -> RewrittenOutput:
    prompt = f"""
            Rewrite the following text in a {tone} tone, while preserving its original meaning.

            Text:
            "{text}"

            Return JSON with:
            - rewritten_text: the rewritten version
            - explanation: how the tone was adapted

            Respond in this format:

            ```json
            {{
            "rewritten_text": "...",
            "explanation": "..."
            }}
            """
    output = llm.invoke(prompt)

    try:
        parsed = extract_json(output.content)
        return RewrittenOutput(**parsed)
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini output:\n{output.content}") from e
