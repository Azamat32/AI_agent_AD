from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATASET_ID_PATTERN = re.compile(r"^[a-f0-9\-]{36}$")

IMPORTANT_COLUMNS = [
    "EventID",
    "TimeCreated",
    "AccountName",
    "IpAddress",
    "ComputerName",
    "TargetUserName",
    "SubjectUserName",
    "LogonType",
    "ProcessName",
]

FAILED_LOGON_EVENT_ID = 4625
SUCCESS_LOGON_EVENT_ID = 4624


def sanitize_dataset_id(dataset_id: str) -> str:
    if not DATASET_ID_PATTERN.match(dataset_id):
        raise ValueError("Invalid dataset id")
    return dataset_id


def dataset_path(dataset_id: str) -> Path:
    safe_id = sanitize_dataset_id(dataset_id)
    return UPLOAD_DIR / f"{safe_id}.csv"


def load_dataset(dataset_id: str) -> pd.DataFrame:
    path = dataset_path(dataset_id)
    if not path.exists():
        raise FileNotFoundError("Dataset not found")
    return pd.read_csv(path)


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lowered = {col.lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None


def stats_payload(df: pd.DataFrame) -> dict[str, Any]:
    event_col = find_column(df, ["EventID", "Event Id", "event_id"])
    time_col = find_column(df, ["TimeCreated", "Timestamp", "time", "datetime"])

    missing_values = {col: int(df[col].isna().sum()) for col in df.columns}
    important_detected = [col for col in df.columns if col in IMPORTANT_COLUMNS]

    top_event_ids: list[dict[str, Any]] = []
    if event_col:
        dist = (
            df[event_col]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
            .reset_index()
            .rename(columns={"index": "event_id", event_col: "count"})
        )
        top_event_ids = dist.to_dict(orient="records")

    hourly_distribution: list[dict[str, Any]] = []
    if time_col:
        parsed = pd.to_datetime(df[time_col], errors="coerce", utc=True)
        hours = parsed.dt.hour.value_counts().sort_index()
        hourly_distribution = [
            {"hour": int(hour), "count": int(count)} for hour, count in hours.items()
        ]

    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": list(df.columns),
        "missing_values": missing_values,
        "important_columns_detected": important_detected,
        "top_event_ids": top_event_ids,
        "hourly_distribution": hourly_distribution,
    }


def suspicious_payload(df: pd.DataFrame) -> dict[str, Any]:
    event_col = find_column(df, ["EventID", "Event Id", "event_id"])
    account_col = find_column(df, ["AccountName", "TargetUserName", "SubjectUserName"])
    time_col = find_column(df, ["TimeCreated", "Timestamp", "time", "datetime"])

    if not event_col:
        return {
            "detections": [],
            "notes": ["EventID column not found; rule-based detections are limited."],
        }

    event_series = pd.to_numeric(df[event_col], errors="coerce")

    def event_count(event_id: int) -> int:
        return int((event_series == event_id).sum())

    detections: list[dict[str, Any]] = []

    failed_count = event_count(4625)
    if failed_count > 0:
        detections.append(
            {
                "rule": "many_failed_logons",
                "severity": "high" if failed_count > 50 else "medium",
                "description": "Detected failed logon attempts (Event ID 4625).",
                "evidence": {"event_id": 4625, "count": failed_count},
            }
        )

    if account_col and failed_count > 0:
        failed_users = (
            df[event_series == 4625][account_col].dropna().astype(str).nunique()
        )
        if failed_users >= 10:
            detections.append(
                {
                    "rule": "password_spraying_indicator",
                    "severity": "high",
                    "description": "Many failed logons across distinct users indicate possible password spraying.",
                    "evidence": {
                        "failed_logons": failed_count,
                        "distinct_users": int(failed_users),
                    },
                }
            )

    special_priv_count = event_count(4672)
    if special_priv_count > 0:
        detections.append(
            {
                "rule": "suspicious_admin_privileges",
                "severity": "medium",
                "description": "Special privileges assigned to new logon (Event ID 4672).",
                "evidence": {"event_id": 4672, "count": special_priv_count},
            }
        )

    kerberos_4768 = event_count(4768)
    kerberos_4769 = event_count(4769)
    if kerberos_4768 > 0 or kerberos_4769 > 0:
        detections.append(
            {
                "rule": "kerberos_anomalies",
                "severity": "medium",
                "description": "Kerberos authentication activity detected (Event IDs 4768/4769).",
                "evidence": {"4768": kerberos_4768, "4769": kerberos_4769},
            }
        )

    group_changes_4728 = event_count(4728)
    group_changes_4732 = event_count(4732)
    if group_changes_4728 > 0 or group_changes_4732 > 0:
        detections.append(
            {
                "rule": "group_membership_changes",
                "severity": "medium",
                "description": "Security group membership changes detected (4728/4732).",
                "evidence": {"4728": group_changes_4728, "4732": group_changes_4732},
            }
        )

    timeline_hint: dict[str, str] = {}
    if time_col:
        parsed = pd.to_datetime(df[time_col], errors="coerce", utc=True).dropna()
        if not parsed.empty:
            timeline_hint = {
                "start": parsed.min().isoformat(),
                "end": parsed.max().isoformat(),
            }

    return {"detections": detections, "time_range": timeline_hint, "notes": []}


def ai_context_payload(df: pd.DataFrame) -> dict[str, Any]:
    event_col = find_column(df, ["EventID", "Event Id", "event_id"])
    time_col = find_column(df, ["TimeCreated", "Timestamp", "time", "datetime"])
    account_col = find_column(df, ["AccountName", "TargetUserName", "SubjectUserName"])
    ip_col = find_column(df, ["IpAddress", "Ip", "SourceIP", "ClientAddress"])
    computer_col = find_column(df, ["ComputerName", "Host", "WorkstationName"])

    payload: dict[str, Any] = {
        "rows": int(df.shape[0]),
        "columns": list(df.columns),
        "important_columns_present": [
            col
            for col in [event_col, time_col, account_col, ip_col, computer_col]
            if col is not None
        ],
    }

    if event_col:
        event_series = pd.to_numeric(df[event_col], errors="coerce")
        payload["event_distribution_top20"] = (
            event_series.dropna().astype(int).value_counts().head(20).to_dict()
        )
        payload["failed_vs_successful_logons"] = {
            "failed_4625": int((event_series == FAILED_LOGON_EVENT_ID).sum()),
            "success_4624": int((event_series == SUCCESS_LOGON_EVENT_ID).sum()),
        }

    if time_col:
        parsed = pd.to_datetime(df[time_col], errors="coerce", utc=True)
        payload["hourly_activity"] = parsed.dt.hour.value_counts().sort_index().to_dict()

    if account_col:
        payload["top_accounts"] = (
            df[account_col].dropna().astype(str).value_counts().head(15).to_dict()
        )

    if ip_col:
        payload["top_ips"] = df[ip_col].dropna().astype(str).value_counts().head(15).to_dict()

    if computer_col:
        payload["top_computers"] = (
            df[computer_col].dropna().astype(str).value_counts().head(15).to_dict()
        )

    return payload
