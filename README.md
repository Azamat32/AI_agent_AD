# AI-Assisted Active Directory Log Analysis Web App

## Project Structure

```text
backend/
  main.py
  requirements.txt
  .env.example
  services/
    ai_service.py
    dataset_service.py
    report_service.py
  uploads/
frontend/
  package.json
  vite.config.js
  index.html
  postcss.config.js
  tailwind.config.js
  src/
    main.jsx
    App.jsx
    api/
      client.js
    components/
      UploadCard.jsx
      AnalysisPanel.jsx
      ChartsPanel.jsx
      AISummaryPanel.jsx
    styles/
      index.css
README.md
```

## Backend Setup (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `GROQ_API_KEY` in `backend/.env`.

Run backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`
Backend default URL: `http://localhost:8000`

Set custom API URL if needed:

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

## Environment Variables

Backend `.env` example:

```env
GROQ_API_KEY=your_groq_api_key_here
FRONTEND_ORIGIN=http://localhost:5173
MAX_UPLOAD_MB=20
```

## API Endpoints

- `POST /upload` - Upload CSV dataset (max 20MB).
- `GET /dataset/{dataset_id}/stats` - Dataset metadata and statistics.
- `GET /dataset/{dataset_id}/suspicious` - Rule-based suspicious detections.
- `POST /dataset/{dataset_id}/ai/summary` - AI-assisted summary via Groq (`llama-3.1-8b-instant`).
- `GET /dataset/{dataset_id}/report?format=markdown|json` - Export report.

## Security Notes

- CSV type and file size are validated.
- `dataset_id` is sanitized.
- Uploaded content is stored as data only and never executed.
- CORS is restricted to local frontend origin.
- AI output includes a clear in-app disclaimer and in reports.

## Notes

- AI analysis is best-effort and may be inaccurate.
- Human analyst validation is required before operational decisions.
