import json, re
from pydantic import BaseModel
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from llm_object import llm
from services.mcp_server.server import mcp

class DistortionResult(BaseModel):
    has_distortion: bool
    distortion_type: List[str]
    explanation: str
    reframe_suggestion: str

def extract_json(content: str) -> dict:
    content = re.sub(r"^```(?:json)?\n?", "", content.strip())
    content = re.sub(r"\n?```$", "", content)
    return json.loads(content)

@mcp.tool(name="Detect Cognitive Distortion")
def detect_cognitive_distortion(text: str) -> DistortionResult:

    prompt = f"""
    Analyze the following statement for cognitive distortions (e.g., catastrophizing, black-and-white thinking, overgeneralization).

    Text:
    \"\"\"{text}\"\"\"

    Respond in JSON:

    ```json
    {{
    "has_distortion": <true or false>,
    "distortion_type": <List of distortion types>,
    "explanation": <explanation of the distortion>,
    "reframe_suggestion": <suggestion to reframe the thought>
    }}
    """
    result = llm.invoke(prompt)
    return DistortionResult(**extract_json(result.content))
