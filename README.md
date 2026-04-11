# Agentic AI Research App

An agentic research system that plans a web search task, gathers sources, scrapes content, filters results, and synthesizes a structured answer.

## Demo Video

A short walkthrough of the system, showing the agent pipeline (planning → search → scraping → synthesis) and example queries:

👉 https://drive.google.com/file/d/1BTM7RtjRFJMayW-O6w-WTDiv3fSwWkyg/view?usp=sharing
 

The project now has a clear frontend/backend split:

- `backend/` contains the research pipeline and Flask server.
- `frontend/` contains the browser UI.

## Why An Agentic Approach

This problem is not just a single prompt-and-response task. It benefits from a staged workflow:

1. Plan the task first so the system knows what to look for.
2. Search the web for relevant sources.
3. Scrape and clean the content.
4. Filter weak results before synthesis.
5. Generate a final response from the collected evidence.

That approach is better than asking the model to answer immediately because it creates a traceable pipeline, makes failures easier to isolate, and gives the UI a structured result to display.

## Architecture Overview

```text
User query
	-> Flask app ([backend/app.py](backend/app.py))
	-> Planner ([backend/planner.py](backend/planner.py))
	-> Executor ([backend/executor.py](backend/executor.py))
			-> Search tool ([backend/tools/search.py](backend/tools/search.py))
			-> Scraper tool ([backend/tools/scraper.py](backend/tools/scraper.py))
			-> Filter/rank ([backend/utils/filter.py](backend/utils/filter.py))
	-> Synthesizer ([backend/synthesizer.py](backend/synthesizer.py))
	-> JSON response
	-> Frontend ([frontend/templates/index.html](frontend/templates/index.html) + [frontend/static/app.js](frontend/static/app.js))
```

The Flask app serves the UI and exposes a single research API endpoint. The frontend sends the query, shows progress, and renders the structured result.

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
cd /Users/nishadshirodkar/Documents/GitHub/Agentic_AI
python -m venv venv
source venv/bin/activate
python -m pip install -r backend/requirements.txt
```

## Environment Variables

Set your keys in `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_key
SERPER_API_KEY=your_serper_key
```

`GEMINI_API_KEY` is used by the planner and synthesizer. `SERPER_API_KEY` is used by the search tool.

## Run The System

Web app:

```bash
python backend/app.py
```

Open `http://127.0.0.1:5000` in your browser.

CLI mode:

```bash
python backend/main.py
```

## Tools Used And Why

- `search.py`: finds candidate sources quickly via Serper.
- `scraper.py`: extracts clean readable text from each source.
- `filter.py`: removes low-value, duplicate, or weak content and ranks the rest.
- `planner.py`: turns a query into a simple search-and-scrape plan.
- `synthesizer.py`: turns collected evidence into a structured answer.

The stack is intentionally small. Each tool does one job, which keeps debugging simpler and makes the pipeline easier to reason about.

## How Bad Tool Results Are Handled

- Search failures return an empty result list.
- Scrape failures skip that URL and continue with the remaining sources.
- Filtered-out results are removed before synthesis.
- If nothing usable remains, synthesis returns a low-confidence structured response.
- If the LLM output cannot be parsed as JSON, the synthesizer returns a safe structured error payload.

This means one bad source does not break the whole run.

## How Hallucinations Are Reduced

- The system grounds synthesis in scraped source text instead of answering from memory only.
- The prompt asks for JSON output and constrains the shape of the response.
- Filtering removes weak or irrelevant pages before synthesis.
- The synthesizer is instructed to prefer evidence-backed claims.
- The UI shows sources so users can inspect where the answer came from.

This does not eliminate hallucinations completely, but it reduces them materially.

## Design Decisions

- A staged agentic pipeline was chosen instead of one large prompt because it is easier to debug and easier to evolve.
- The frontend is a simple Flask-served single page so the app stays lightweight.
- Structured JSON output was used so the UI can render answers predictably.
- The repository was split into `backend/` and `frontend/` to make ownership and deployment cleaner.
- Symlinks are used so Flask can still load templates and static assets without changing code behavior.

## Key Tradeoffs

- More moving parts: the pipeline is more complex than a single call to an LLM.
- More latency: search and scraping add time before the final answer appears.
- More operational dependencies: the app now depends on both Gemini and Serper.
- Better transparency and control: each stage can be inspected and improved independently.

## Known Limitations

- The system depends on external APIs and can fail when quota is exhausted.
- Search quality depends on the Serper response and the availability of good sources.
- Scraping can fail on heavily protected or dynamic pages.
- There are no automated tests in the repository yet, so regression coverage is limited.
- The current LLM integration uses `google.generativeai`, which is deprecated upstream.

## Production Readiness

To make this production-ready, I would:

- Switch from the development Flask server to a production WSGI server such as Gunicorn or Waitress.
- Move secrets to a real secret manager instead of a local `.env` file.
- Add retries, circuit breakers, and explicit timeout handling around external API calls.
- Add caching for repeated searches and repeated final answers.
- Add structured logging and request IDs end-to-end.
- Add automated tests for planner, filtering, and response formatting.
- Replace the deprecated Gemini SDK with the supported `google.genai` client.
- Add authentication and rate limiting if this is exposed publicly.

## What To Monitor In Production

- API error rate for Gemini and Serper.
- Quota exhaustion and rate-limit responses.
- Search success rate and scrape success rate.
- End-to-end latency per request.
- Number of sources collected per query.
- Final answer confidence distribution.
- Parse failures in the synthesizer.
- Frontend request failures and server 5xx responses.

## Future Improvements

- Add streaming or step-level progress updates in the UI.
- Add query history and saved reports.
- Add citations with source excerpts instead of only source URLs.
- Add test coverage for the planner, executor, and synthesizer.
- Add a better ranking model for source selection.
- Add provider abstraction so the LLM backend can be swapped more easily.
- Add a background job queue for long-running research tasks.

## Notes On The Current Structure

- Run the web app from `backend/app.py`.
- Run the CLI from `backend/main.py`.
- Frontend assets live under `frontend/` and are served by Flask through the template/static links inside `backend/`.