import json
import re
from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from llm_object import llm
from services.mcp_server.server import mcp

class SuicideRiskResult(BaseModel):
    is_at_risk: bool
    risk_level: Literal["low", "moderate", "high"]
    warning_signs: List[str]
    explanation: str


def extract_json(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return json.loads(content)


@mcp.tool(name="Detect Suicide Risk")
def detect_suicide_risk(text: str) -> SuicideRiskResult:
    prompt = f"""
You are a mental health safety monitor.

Read the following message and assess the suicide or self-harm risk level.

Text:
\"\"\"{text}\"\"\"

Determine:
- If there is any risk of suicidal thoughts or self-harm.
- Classify the risk level: "low", "moderate", or "high".
- Extract warning signs (e.g. phrases showing hopelessness, plans, withdrawal).
- Provide a brief explanation for the decision.

Respond in this JSON format (within markdown):

```json
{{
  "is_at_risk": <is_at_risk>,
  "risk_level": <risk_level>,
  "warning_signs": <warning_signs>,
  "explanation": <explanation>
}}
"""
    output = llm.invoke(prompt)

    try:
        parsed = extract_json(output.content)
        return SuicideRiskResult(**parsed)
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini output:\n{output.content}") from e

