from __future__ import annotations

from typing import Any


def render_markdown_report(
    dataset_id: str,
    stats: dict[str, Any],
    suspicious: dict[str, Any],
    ai_summary: dict[str, Any] | None,
) -> str:
    lines: list[str] = [
        f"# Active Directory Security Log Report - {dataset_id}",
        "",
        "## Dataset Statistics",
        f"- Rows: {stats.get('rows', 0)}",
        f"- Columns: {stats.get('cols', 0)}",
        f"- Important Columns: {', '.join(stats.get('important_columns_detected', [])) or 'None detected'}",
        "",
        "### Top Event IDs",
    ]

    for item in stats.get("top_event_ids", []):
        lines.append(f"- Event {item.get('event_id')}: {item.get('count')}")

    lines.extend(["", "## Rule-Based Suspicious Detections"])
    detections = suspicious.get("detections", [])
    if detections:
        for detection in detections:
            lines.append(
                f"- **{detection.get('rule')}** ({detection.get('severity')}): {detection.get('description')}"
            )
            lines.append(f"  - Evidence: {detection.get('evidence')}")
    else:
        lines.append("- No suspicious patterns found by current heuristics.")

    lines.extend(["", "## AI Summary"])
    if ai_summary:
        lines.append(f"- Summary: {ai_summary.get('summary', 'N/A')}")
        lines.append("- Suspicious patterns:")
        for item in ai_summary.get("suspicious_patterns", []):
            lines.append(f"  - {item}")
        lines.append("- Most likely attack techniques:")
        for item in ai_summary.get("most_likely_attack_techniques", []):
            lines.append(f"  - {item}")
        lines.append("- Recommended detections/actions:")
        for item in ai_summary.get("recommended_actions", []):
            lines.append(f"  - {item}")
        lines.append("- MITRE ATT&CK mapping:")
        for mapping in ai_summary.get("mitre_attack_mapping", []):
            lines.append(f"  - {mapping}")
        lines.append("- Limitations:")
        for item in ai_summary.get("limitations", []):
            lines.append(f"  - {item}")
    else:
        lines.append("- AI summary not generated yet.")

    lines.extend(
        [
            "",
            "## Human-in-the-Loop Notes",
            "- Validate all AI findings with SIEM queries and endpoint telemetry.",
            "- Confirm account and host criticality before escalation.",
            "",
            "## Disclaimer",
            "AI-generated analysis may be inaccurate. Use analyst validation before making security decisions.",
        ]
    )

    return "\n".join(lines)
