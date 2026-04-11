# Agentic AI Research App

Professionalized structure with clear frontend/backend separation.

## Project Layout

```text
Agentic_AI/
├── backend/
│   ├── app.py
│   ├── main.py
│   ├── planner.py
│   ├── executor.py
│   ├── synthesizer.py
│   ├── requirements.txt
│   ├── .env
│   ├── tools/
│   ├── utils/
│   ├── test/
│   ├── templates -> ../frontend/templates
│   └── static -> ../frontend/static
├── frontend/
│   ├── templates/
│   └── static/
└── venv/
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

## Environment Variables

Set keys in `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_key
SERPER_API_KEY=your_serper_key
```

## Run Web App

```bash
python backend/app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Run CLI Mode

```bash
python backend/main.py
```