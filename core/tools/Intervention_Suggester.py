import json
import re
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from llm_object import llm
from services.mcp_server.server import mcp

class InterventionSuggestion(BaseModel):
    intervention_type: str
    intervention_text: str
    rationale: str

def extract_json(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return json.loads(content)

@mcp.tool(name="Suggest Intervention")
def suggest_intervention(text: str) -> InterventionSuggestion:
    prompt = f"""
        You are a therapy assistant. Based on the user's input, suggest one appropriate psychological intervention. 
        It could be a CBT technique, mindfulness prompt, coping strategy, journaling task, or a supportive message.

        Text:
        \"\"\"{text}\"\"\"

        Respond in this format (in a markdown JSON block):

        ```json
        {{
        "intervention_type": <intervention_type>,
        "intervention_text": <intervention_text>,
        "rationale": <rationale>
        }}
        """
    output = llm.invoke(prompt)

    try:
        parsed = extract_json(output.content)
        return InterventionSuggestion(**parsed)
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini output:\n{output.content}") from e
