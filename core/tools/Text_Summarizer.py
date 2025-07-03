from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from llm_object import llm
from services.mcp_server.server import mcp

class SummaryResult(BaseModel):
    summary: str

@mcp.tool(name="Summarize Text")
def summarize_text(text: str) -> SummaryResult:
    style="paragraph"
    prompt = f"""
Summarize the following text in a {style} format:

\"\"\"{text}\"\"\"
"""

    response = llm.invoke(prompt)

    return SummaryResult(summary=response.content.strip())
