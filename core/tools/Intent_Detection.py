import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from llm_object import llm
from services.mcp_server.server import mcp

class IntentResult(BaseModel):
    label: str
    confidence: float = Field(..., ge=0, le=1)
    explanation: str

def extract_json_from_code_block(content: str) -> dict:
    """
    Extract JSON from markdown-style code block returned by Gemini LLM.
    """
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return json.loads(content)

@mcp.tool(name="Detect Intent")
def detect_intent(text: str) -> IntentResult:

    prompt = f"""
        You are an intelligent assistant that detects the **intent** behind a user's message.

        User message: "{text}"

        1. Decide what the user's intent is.
        2. Name the intent clearly and concisely (like "ask_weather", "book_flight", "express_sadness", "cancel_meeting", etc).
        3. Estimate your confidence in this classification between 0 and 1.
        4. Explain why you chose this intent.

        Respond in **JSON** like this (wrap in a Markdown JSON block):

        ```json
        {{
        "label": "intent_name",
        "confidence": 0.93,
        "explanation": "Reasoning behind the intent classification."
        }}
        """
    output = llm.invoke(prompt)

    try:
        parsed = extract_json_from_code_block(output.content)
        return IntentResult(**parsed)
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini output:\n{output.content}") from e