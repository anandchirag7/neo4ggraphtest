#!/usr/bin/env python3
"""
generate_ontology_config.py

Use an LLM to auto-generate an ONTOLOGY_CONFIG entry for a document,
and append/merge it into ontology_config.py.

Typical usage:

    python generate_ontology_config.py \
        --raw_json raw_rt6220.json \
        --doc_id RT6220_DS-12 \
        --ontology_file ontology_config.py

You MUST plug in your own LLM call inside `call_llm_for_ontology()`.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Dict, List
import pprint
import sys
import re

# Add parent directory to sys.path to allow importing 'config' and 'main'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import llm_infer


# =====================================
# 1. LLM HOOK
# =====================================

def call_llm_for_ontology(doc_id: str, text_snippet: str) -> Dict[str, Any]:
    """
    Call the LLM to infer ontology configuration from datasheet text.
    Returns a dict with 'ics' field containing IC definitions.
    """
    system_prompt = """You are an expert electronics engineer specializing in IC datasheet analysis.

Your task: Extract structured ontology from datasheet text into strict JSON format.

EXTRACTION RULES:
1. IC Identification:
   - Extract ALL integrated circuits mentioned (ICs, crystals, diodes, transistors, etc.)
   - Use the exact part number/model as the "name" (e.g., "RT6220", "7M", "B220A")
   - If multiple variants exist, create separate entries

2. Pin Extraction:
   - List ALL pin names/signals mentioned (VIN, VOUT, GND, EN, FB, etc.)
   - Use standard abbreviations (e.g., "F0" for frequency, "CL" for load capacitance)
   - For components without traditional pins (crystals, passives), use relevant parameters as "pins"

3. Constraint Extraction - Extract ALL specifications:
   
   ELECTRICAL:
   - Voltages: min_voltage, max_voltage, recommended_voltage, typical_voltage
   - Currents: min_current, max_current, quiescent_current
   - Power: max_power, typical_power
   - Impedance: max_impedance, min_impedance, typical_impedance
   
   FREQUENCY/TIMING:
   - frequency_range, min_frequency, max_frequency
   - frequency_tolerance, frequency_stability
   
   TEMPERATURE:
   - operating_temperature_range, storage_temperature_range
   - min_temperature, max_temperature
   
   CAPACITANCE:
   - load_capacitance, shunt_capacitance, input_capacitance
   
   OTHER:
   - drive_level, esr, accuracy, efficiency
   - Use descriptive snake_case for any other parameter types

4. Constraint Details:
   - "id": Format as <IC>_<PARAMETER>_<TYPE> (e.g., "7M_F0_MAX", "RT6220_VIN_MIN")
   - "pin": The specific pin/parameter this applies to (empty string if device-level)
   - "type": Use snake_case from categories above
   - "value": Extract numeric value (null if range or non-numeric)
   - "unit": Standard units (V, A, W, Ω, MHz, pF, degC, ppm, %) or null
   - "description": Clear, concise explanation
   - "keywords": Extract 2-5 relevant phrases from the original text

IMPORTANT:
- Be thorough: Extract ALL specifications, even if they seem minor
- Be precise: Use exact values and units from the text
- Be consistent: Use standard naming conventions
- Output ONLY valid JSON, no markdown formatting

JSON SCHEMA:
{
  "ics": [
    {
      "name": "PART_NUMBER",
      "pins": ["PIN1", "PIN2", ...],
      "constraints": [
        {
          "id": "IC_PARAM_TYPE",
          "pin": "PIN_NAME or empty",
          "type": "parameter_type",
          "value": number or null,
          "unit": "unit or null",
          "description": "Clear description",
          "keywords": ["phrase1", "phrase2", ...]
        }
      ]
    }
  ]
}"""

    user_prompt = f"""Document ID: {doc_id}

Analyze the following datasheet text and extract ALL ICs and their specifications.
Be thorough and extract every constraint you can identify.

TEXT:
{text_snippet}

OUTPUT: Return ONLY the JSON object, no additional text."""

    # Combine system and user prompts
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    # Use the new llm_infer function
    content = llm_infer(combined_prompt)
    
    # Clean up markdown code blocks if present
    cleaned_content = re.sub(r"```json|```", "", content).strip()
    
    # Debug output
    with open("debug_llm_response.txt", "w", encoding="utf-8") as f:
        f.write(f"RAW:\n{content}\n\nCLEANED:\n{cleaned_content}\n")

    try:
        return json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse LLM response as JSON. See debug_llm_response.txt. Error: {e}")
        return {}


# =====================================
# 2. HELPER: LOAD RAW JSON + BUILD SNIPPET
# =====================================

def load_raw_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_text_snippet(raw_json: Dict[str, Any], max_chars: int = 12000) -> str:
    """
    Build a text snippet from the most relevant pages to infer pins + constraints.

    Heuristic:
      - Prefer the first ~8 pages (General Description, Pin config, Abs Max, Elec Char)
      - Truncate to max_chars.
    """
    pages = raw_json.get("pages", [])
    # Take first N pages; you can tune this
    selected_pages = [p for p in pages if p.get("page_number", 0) <= 12]

    snippets = []
    for p in selected_pages:
        pno = p.get("page_number")
        txt = p.get("raw_text", "").strip()
        snippets.append(f"=== PAGE {pno} ===\n{txt}\n")

    full = "\n".join(snippets)
    if len(full) > max_chars:
        full = full[:max_chars] + "\n...[TRUNCATED]..."
    return full


# =====================================
# 3. ONTOLOGY CONFIG FILE MANAGEMENT
# =====================================

def load_existing_ontology(ontology_file: Path) -> Dict[str, Any]:
    """
    Safely import ONTOLOGY_CONFIG from ontology_config.py
    even if it's not in sys.path.
    """
    if not ontology_file.exists():
        return {}

    spec = importlib.util.spec_from_file_location("ontology_config", ontology_file)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    config = getattr(module, "ONTOLOGY_CONFIG", {})
    if not isinstance(config, dict):
        raise ValueError("ONTOLOGY_CONFIG in ontology_config.py is not a dict")
    return config


def write_ontology_file(ontology_file: Path, config: Dict[str, Any]) -> None:
    """
    Overwrite ontology_config.py with a pretty-printed ONTOLOGY_CONFIG dict.
    """
    ontology_file.parent.mkdir(parents=True, exist_ok=True)
    with ontology_file.open("w", encoding="utf-8") as f:
        f.write("# Auto-generated ontology configuration for datasheet documents\n")
        f.write("# Feel free to edit/extend by hand.\n\n")
        f.write("ONTOLOGY_CONFIG = ")
        f.write(pprint.pformat(config, sort_dicts=False))
        f.write("\n")


# =====================================
# 4. MAIN PIPELINE
# =====================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_json", required=True, help="Path to raw_<doc>.json from extract_raw_pdf.py")
    parser.add_argument("--doc_id", required=True, help="Document ID key for ONTOLOGY_CONFIG (e.g., RT6220_DS-12)")
    parser.add_argument("--ontology_file", default="ontology_config.py", help="Path to ontology_config.py")

    args = parser.parse_args()

    raw_json = load_raw_json(args.raw_json)
    snippet = build_text_snippet(raw_json)

    print(f"[INFO] Built text snippet of length {len(snippet)} characters for doc_id={args.doc_id}")

    # --- Call LLM here ---
    print("[INFO] Calling LLM to infer ontology config ...")
    ontology_entry = call_llm_for_ontology(args.doc_id, snippet)
    # Expect something like: {"ics": [ {name, pins, constraints} ]}

    if not isinstance(ontology_entry, dict) or "ics" not in ontology_entry:
        raise ValueError("LLM response is not in expected dict format with 'ics' field")

    # Filter out ICs with empty or missing constraints
    filtered_ics = []
    for ic in ontology_entry.get("ics", []):
        constraints = ic.get("constraints", [])
        if constraints and len(constraints) > 0:
            filtered_ics.append(ic)
        else:
            print(f"[INFO] Skipping IC '{ic.get('name', 'unknown')}' - no constraints found")
    
    # Update the ontology entry with filtered ICs
    ontology_entry["ics"] = filtered_ics
    
    # Only proceed if we have at least one IC with constraints
    if not filtered_ics:
        print(f"[WARNING] No ICs with constraints found for doc_id={args.doc_id}")
        print(f"[INFO] Skipping ontology config update")
        return

    # --- Merge into ONTOLOGY_CONFIG ---
    ontology_path = Path(args.ontology_file)
    existing_config = load_existing_ontology(ontology_path)

    # Insert/overwrite config for this doc_id
    existing_config[args.doc_id] = ontology_entry

    # Write back
    write_ontology_file(ontology_path, existing_config)

    print(f"[OK] Updated {ontology_path} with ontology for doc_id={args.doc_id}")
    print(f"[INFO] Added {len(filtered_ics)} IC(s) with constraints")


if __name__ == "__main__":
    main()
