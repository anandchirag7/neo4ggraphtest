
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
    # ontology_str = _format_ontology_hints(ontology_hints) # Optional, keeping it simple for now

    if answer_length_hint == "short":
        length_instructions = "Aim for 3-6 concise bullet points or <=150 words."
    elif answer_length_hint == "long":
        length_instructions = "You may use up to 600-800 words if needed."
    else:
        length_instructions = "Aim for 150-300 words, concise but clear."

    # DETERMINISTIC PROMPT (No intermediate LLM)
    # This ensures 100% faithfulness to the retrieved context.
    
    final_prompt = textwrap.dedent(f"""
        SYSTEM:
        You are an expert technical assistant.
        
        ### GOAL:
        Produce a **comprehensive, self-contained** answer.
        The answer must be written such that if the user did NOT see the question, they would still know exactly what is being answered.

        ### GUIDELINES:
        1. **Include Context**: Explicitly mention the product name, parameter name, and conditions from the question.
        2. **Faithfulness**: **COPY text exactly** from the context. Do not correct OCR errors. If the context says "97AFRZ", you write "97AFRZ".
        3. **No Fluff**: **ABSOLUTELY NO PREAMBLE**. Do not say "The provided text contains..." or "Based on the chunks...". Start the answer IMMEDIATELY.
        4. **Structure**: Use a dense paragraph for explanations, or **bullet points** for lists (like ordering codes or pins).

        ### EXAMPLES:

        **Context**: 
        [1] [DOC WidgetX] node_id=node_10 Text: The WidgetX Pro operates from 10Hz to 50Hz.
        
        **User Question**: What is the frequency range?
        **Ideal Answer**: The WidgetX Pro device operates with a frequency range extending from 10Hz to 50Hz.

        **Context**:
        [2] [DOC WidgetX] node_id=node_99 Text: Ordering Information: WX-100-A (Box, 50pcs), WX-200-B (Crate, 10pcs).
        
        **User Question**: How do I order the WidgetX?
        **Ideal Answer**: The ordering options found in the text are:
        * **WX-100-A**: Box, 50pcs
        * **WX-200-B**: Crate, 10pcs

        ### END EXAMPLES

        USER QUESTION:
        {user_question}

        HARD CONSTRAINTS:
        {constraints_str}

        CONTEXT CHUNKS:
        {context_str}

        TASK:
        Answer the USER QUESTION following the GUIDELINES above.
        {length_instructions}
    """).strip()

    return final_prompt
