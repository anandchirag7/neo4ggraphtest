
from typing import List, Dict, Any, Optional
import textwrap
import json
from llm.answer_llm import answer_llm as call_prompt_llm

PROMPT_GENERATOR_SYSTEM = textwrap.dedent("""
You are a Prompt-Generator AI whose job is to build the BEST possible prompt
for a downstream LLM that will generate the final answer for the user.

Given:
1) user question
2) retrieved context chunks
3) optional hard constraints
4) optional image references
5) optional ontology hints

Your task:
→ Construct a COMPLETE answer-prompt for the downstream LLM.

The generated prompt MUST:
- Include the user question verbatim.
- Include ALL context chunks grouped by document and type.
- Include image references ONLY if they add meaning.
- Include hard constraints in a section called HARD CONSTRAINTS.
- Include a TASK section that clearly instructs the answering-LLM.
- Include safety rules:
    • Never violate any constraint.
    • Never hallucinate undocumented values.
    • If information is insufficient, say so.
Be formatted as plain text — do NOT wrap inside JSON.

DO NOT answer the user question yourself.
You ONLY produce the prompt that another LLM will answer.
""").strip()

def _format_context_chunks(context_chunks: List[Dict[str, Any]]) -> str:
    lines = []
    for i, c in enumerate(context_chunks, start=1):
        doc_id = c.get("doc_id", "UNKNOWN_DOC")
        source = c.get("source", "Unknown")
        page = c.get("page")
        pin = c.get("pin")
        node_id = c.get("node_id")
        text = (c.get("text") or "").strip()
        img = c.get("image_path")

        header = f"[{i}] [DOC {doc_id}] [{source}"
        if page is not None:
            header += f" page {page}"
        if pin:
            header += f" pin {pin}"
        header += f"] node_id={node_id}"
        lines.append(header)

        if img:
            lines.append(f"Image path: {img}")

        if len(text) > 1000:
            text = text[:1000] + " ...[TRUNCATED]..."
        lines.append(text)
        lines.append("")
    return "\n".join(lines) if lines else "(no context chunks)"

def _format_constraints(constraints: List[Dict[str, Any]]) -> str:
    if not constraints:
        return "(no hard constraints available)"
    lines = []
    for c in constraints:
        cid = c.get("id", "UNKNOWN_ID")
        ic = c.get("ic", "UNKNOWN_IC")
        pin = c.get("pin", "UNKNOWN_PIN")
        ctype = c.get("type", "unknown_type")
        value = c.get("value")
        unit = c.get("unit")
        desc = c.get("description", "")
        val_str = "null"
        if value is not None and unit:
            val_str = f"{value} {unit}"
        elif value is not None:
            val_str = str(value)
        lines.append(f"- {cid}: {ic}.{pin} – {ctype} – {val_str} – {desc}")
    return "\n".join(lines)

def _format_ontology_hints(ontology_hints: Optional[Dict[str, Any]]) -> str:
    if not ontology_hints:
        return "(no ontology hints provided)"
    return json.dumps(ontology_hints, indent=2)

def build_prompt(
    user_question: str,
    context_chunks: List[Dict[str, Any]],
    constraints: List[Dict[str, Any]],
    ontology_hints: Optional[Dict[str, Any]] = None,
    answer_length_hint: str = "medium",
) -> str:
    context_str = _format_context_chunks(context_chunks)
    constraints_str = _format_constraints(constraints)
    ontology_str = _format_ontology_hints(ontology_hints)

    if answer_length_hint == "short":
        length_instructions = "Aim for 3-6 concise bullet points or <=150 words."
    elif answer_length_hint == "long":
        length_instructions = "You may use up to 600-800 words if needed."
    else:
        length_instructions = "Aim for 150-300 words, concise but clear."

    user_message = textwrap.dedent(f"""
        SYSTEM (for downstream LLM):
        You are an expert electronics/datasheet assistant. Obey all datasheet constraints and never invent values.

        USER QUESTION:
        {user_question}

        CONTEXT CHUNKS:
        {context_str}

        HARD CONSTRAINTS:
        {constraints_str}

        ONTOLOGY HINTS:
        {ontology_str}

        TASK:
        - Answer the USER QUESTION using only the provided context and constraints.
        - {length_instructions}
        - If figures/images are referenced, mention their node IDs and image paths.
        - If multiple documents contribute, clearly separate them by document ID.
        - If information is insufficient, say so.
    """).strip()

    # Call same LLM as final but in "prompt-generator mode"
    # In a more advanced setup, you'd use a separate smaller model here.
    generated_prompt = call_prompt_llm(
        f"{PROMPT_GENERATOR_SYSTEM}\n\nUSER INPUT:\n{user_message}"
    )
    return generated_prompt
