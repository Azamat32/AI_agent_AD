from __future__ import annotations

import os
import uuid
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from services.ai_service import summarize_with_groq
from services.dataset_service import (
    UPLOAD_DIR,
    ai_context_payload,
    dataset_path,
    load_dataset,
    stats_payload,
    suspicious_payload,
)
from services.report_service import render_markdown_report

load_dotenv()

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app = FastAPI(title="AD Security Log Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LAST_AI_SUMMARIES: dict[str, dict] = {}


def ensure_csv_upload(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)) -> dict[str, str]:
    ensure_csv_upload(file)

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_UPLOAD_MB:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_UPLOAD_MB}MB")

    dataset_id = str(uuid.uuid4())
    output_path = dataset_path(dataset_id)
    output_path.write_bytes(content)

    try:
        pd.read_csv(output_path, nrows=5)
    except Exception as exc:
        output_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Invalid CSV format") from exc

    return {"dataset_id": dataset_id}


@app.get("/dataset/{dataset_id}/stats")
def dataset_stats(dataset_id: str) -> JSONResponse:
    try:
        df = load_dataset(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return JSONResponse(stats_payload(df))


@app.get("/dataset/{dataset_id}/suspicious")
def suspicious(dataset_id: str) -> JSONResponse:
    try:
        df = load_dataset(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return JSONResponse(suspicious_payload(df))


@app.post("/dataset/{dataset_id}/ai/summary")
def ai_summary(dataset_id: str) -> JSONResponse:
    try:
        df = load_dataset(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    context = ai_context_payload(df)

    try:
        summary = summarize_with_groq(context)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI summary failed: {exc}") from exc

    LAST_AI_SUMMARIES[dataset_id] = summary
    return JSONResponse(summary)


@app.get("/dataset/{dataset_id}/report")
def report(dataset_id: str, format: str = "markdown"):
    try:
        df = load_dataset(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    stats = stats_payload(df)
    suspicious_data = suspicious_payload(df)
    ai_data = LAST_AI_SUMMARIES.get(dataset_id)
    markdown = render_markdown_report(dataset_id, stats, suspicious_data, ai_data)

    if format.lower() == "json":
        return JSONResponse(
            {
                "dataset_id": dataset_id,
                "stats": stats,
                "suspicious": suspicious_data,
                "ai_summary": ai_data,
                "limitations": [
                    "Rule-based detections are heuristic and may miss complex attacks.",
                    "AI analysis may be inaccurate and requires human validation.",
                ],
                "disclaimer": "AI-generated analysis may be inaccurate.",
            }
        )

    return PlainTextResponse(markdown, media_type="text/markdown")


@app.on_event("startup")
def on_startup() -> None:
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
