import sys
import os
from typing import Dict, Any
import requests

# Add parent directory to sys.path to allow importing 'pipeline'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.main import llm_infer
from config import ANSWER_URL, ANSWER_MODEL, EURON_API_KEY, MAX_TOKENS, TEMPERATURE

def answer_llm(prompt: str) -> str:
    """
    Call the LLM to generate an answer.
    Uses the llm_infer function from pipeline.main.
    """
    return llm_infer(prompt)



def call_llm_for_ontology(doc_id: str, text_snippet: str) -> Dict[str, Any]:
    system_prompt = """You are an expert in electronics and IC datasheets.
You read raw text extracted from PDF datasheets and build a clean JSON ontology.

- Extract every IC (integrated circuit) described in the text.
- For each IC, list:
  - "name": the part number (e.g. "RT6220")
  - "pins": a list of pin names (like VIN, PG, SW, FB, PGND, AGND, VCC, VBYP, EN, etc.)
  - "constraints": a list of operating or safety constraints.

For each constraint:
  - "id": a stable identifier like "<IC>_<PIN>_<THING>" (e.g. "RT6220_PG_MAX_5V").
  - "pin": the pin name the constraint applies to (e.g. "PG", "VIN", "VOUT").
  - "type": a short snake_case type (e.g. "max_voltage", "recommended_max_voltage", "uvp_threshold", "ovp_threshold", "operating_temperature_range").
  - "value": numeric value when meaningful (use ratio for thresholds like 58% → 0.58), otherwise null.
  - "unit": "V", "ratio", "degC", etc. If not numeric, use null.
  - "description": short human-readable explanation.
  - "keywords": list of phrases that appear in the text that support this constraint (snippets to help matching later).

Only include constraints that clearly appear in the text snippet.
The output MUST be strict JSON with this schema:

{
  "ics": [
    {
      "name": "<IC name>",
      "pins": ["PIN1", "PIN2", ...],
      "constraints": [
        {
          "id": "STRING",
          "pin": "STRING",
          "type": "STRING",
          "value": <number or null>,
          "unit": "STRING or null",
          "description": "STRING",
          "keywords": ["STRING", ...]
        }
      ]
    }
  ]
}
"""

    user_prompt = f"""Document ID: {doc_id}

Below is raw text extracted from the datasheet. It may contain line breaks and OCR noise.
Read it carefully and output ONLY the JSON object described above.

---------------- TEXT SNIPPET START ----------------
{text_snippet}
---------------- TEXT SNIPPET END ----------------
"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {EURON_API_KEY}"
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "model": ANSWER_MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }

    resp = requests.post(ANSWER_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    # Adjust path according to actual API schema
    content = data["choices"][0]["message"]["content"]
    return content
