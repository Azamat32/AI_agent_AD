from __future__ import annotations

import json
import os
from typing import Any

from groq import Groq

MODEL_NAME = "llama-3.1-8b-instant"


def build_prompt(context: dict[str, Any]) -> str:
    return (
        "You are a SOC analyst specialized in Active Directory logs. "
        "Given the compact JSON context below, produce a strict JSON response with keys: "
        "summary, suspicious_patterns (array), attack_techniques (array), recommended_detections (array), "
        "mitre_attack_mapping (array of objects with tactic and technique), limitations (array). "
        "Keep it concise and security-focused. Include uncertainty if confidence is low.\n\n"
        f"DATASET_CONTEXT:\n{json.dumps(context, indent=2)}"
    )


def summarize_with_groq(context: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing")

    client = Groq(api_key=api_key, timeout=25.0)

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You generate JSON-only SOC analysis with cautious language.",
            },
            {"role": "user", "content": build_prompt(context)},
        ],
    )

    content = completion.choices[0].message.content
    if not content:
        raise RuntimeError("AI service returned empty response")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Failed to parse AI response") from exc

    return {
        "summary": parsed.get("summary", "No summary generated."),
        "suspicious_patterns": parsed.get("suspicious_patterns", []),
        "most_likely_attack_techniques": parsed.get("attack_techniques", []),
        "recommended_actions": parsed.get("recommended_detections", []),
        "mitre_attack_mapping": parsed.get("mitre_attack_mapping", []),
        "limitations": parsed.get("limitations", []),
        "disclaimer": "AI-generated analysis may be inaccurate and must be validated by a human analyst.",
    }
