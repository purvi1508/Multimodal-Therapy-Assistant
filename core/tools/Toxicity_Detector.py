import json
import re
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from llm_object import llm
from services.mcp_server.server import mcp

class ToxicityResult(BaseModel):
    is_toxic: bool
    toxicity_type: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: str


def extract_json(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return json.loads(content)

@mcp.tool(name="Detect Toxicity")
def detect_toxicity(text: str) -> ToxicityResult:
    prompt = f"""
    Analyze the following text for any form of harmful or unethical content:

    "{text}"

    Identify if it contains **any** of the following:
    - abuse (verbal or emotional)
    - toxicity (hostility, personal attacks)
    - racism
    - sexism
    - partiality, unfairness, or discrimination
    - hate speech
    - harassment
    - inappropriate content

    Respond with this JSON format (in a markdown JSON block):

    ```json
    {{
    "is_toxic": true,
    "toxicity_type": ["racism", "partiality"],
    "confidence": 0.92,
    "description": "The text makes unfair generalizations about a race and expresses biased opinions."
    }}
    """
    output = llm.invoke(prompt)

    try:
        parsed = extract_json(output.content)
        return ToxicityResult(**parsed)
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini output:\n{output.content}") from e
