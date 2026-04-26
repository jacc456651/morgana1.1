# Morgana Web UI — Design Spec
**Date:** 2026-04-25  
**Status:** Approved  
**Stack:** FastAPI + React/Vite + Tailwind + SSE

---

## Overview

A local web dashboard that replaces the CMD for all Morgana interactions. Ticker-centric design: everything about a company lives in one dossier. Stage indicator shows where each ticker is in the investment process. ⌘K command palette for speed.

**Zero changes to existing system** — all current files (`morgana.py`, `agents/`, `graph/`, `connectors/`, `memory/`, `frontend/`, `backend/`) remain untouched. New code lives entirely in `morgana_ui/`.

---

## Architecture

### Directory structure (~17 new files)

```
Sistema_Morgana/
└── morgana_ui/
    ├── server.py          # FastAPI + SSE endpoints + static file serving
    ├── start.bat          # One-command startup: build check + py server.py
    ├── requirements.txt   # fastapi, uvicorn, sse-starlette, python-dotenv
    └── app/               # React + Vite
        ├── package.json
        ├── vite.config.js
        ├── tailwind.config.js
        └── src/
            ├── main.jsx
            ├── App.jsx            # Router: / → Dossier, /sabueso → Sabueso
            ├── pages/
            │   ├── Dossier.jsx    # Main ticker view (tabs + stage)
            │   └── Sabueso.jsx    # Screener results
            └── components/
                ├── Watchlist.jsx      # Left sidebar — ticker list with stages
                ├── StageTrack.jsx     # 5-step progress indicator
                ├── DossierTabs.jsx    # Tab switcher with ✓/● status
                ├── ActorsGrid.jsx     # 10 actors, click to run
                ├── LiveRunner.jsx     # Stepper + log panel (SSE consumer)
                ├── ReportView.jsx     # Markdown render + pillar scorecards
                └── CommandPalette.jsx # ⌘K overlay
```

### Startup behavior

```
First time:   start.bat
              → checks if app/dist/ exists
              → if not: npm install && npm run build
              → py server.py

Daily use:    py morgana_ui/server.py
              → http://localhost:8080 (serves pre-built dist/)
              → identical to Option B single-command startup
```

### Data flow

```
Browser (React) ←→ server.py (FastAPI :8080) ←→ graph/morgana.py (LangGraph) ←→ Supabase
```

### API endpoints (server.py, ~80 lines)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/analyses` | All analyses from Supabase |
| GET | `/api/analyses/{ticker}` | History for a single ticker |
| GET | `/api/analyze?ticker=X&command=Y` | **SSE stream** — runs graph, emits events |
| GET | `/` | Serves `dist/index.html` (SPA) |
| GET | `/assets/*` | Serves `dist/assets/` (JS/CSS) |

**SSE event types** (emitted by `/api/analyze`):

```json
{"type": "step",  "agent": "scout",      "status": "running"}
{"type": "step",  "agent": "scout",      "status": "done", "elapsed": 1.4}
{"type": "log",   "agent": "boss",       "text": "P1 moat: network effects..."}
{"type": "step",  "agent": "boss",       "status": "done", "elapsed": 42.1}
{"type": "done",  "score": 78, "decision": "BUY", "analysis_id": "uuid"}
{"type": "error", "message": "..."}
```

**Streaming mechanism:** LangGraph's native `graph.stream(state, stream_mode="updates")` — one event per node completion. No background threads, no job state, no log interception. The SSE connection IS the job.

**Command routing — two categories:**
- **LangGraph commands** (`analiza`, `chequea`): use `graph.stream()` from `graph/morgana.py`. Server imports from parent directory (`sys.path.insert(0, ROOT_DIR.parent)`).
- **Direct Claude API commands** (all 10 actors, `/compounder`, `/consejo`, `/sabueso`): thin wrappers in `server.py` that call Anthropic Claude API with the appropriate system prompt + ticker data. Same SSE event format. The implementation plan defines each wrapper.

---

## UI Design

### Layout

Two-panel layout:
- **Left (190px):** Watchlist sidebar — ticker cards with stage + progress bar + pending count. Bottom: Sabueso button.
- **Right (flex):** Active ticker dossier — header + stage track + tabs + content.

### Watchlist sidebar

Each ticker card shows:
- Ticker symbol + current score
- Stage progress bar (width = stage/5 * 100%)
- Stage label + pending command count

### Ticker dossier

**Header:**
- Ticker + company name + market cap + sector
- Score (large) + BUY/HOLD/AVOID badge
- Stage track (5 circles: Descubrir → Analizar → Validar → Decidir → Monitor)
- "Faltan en esta etapa" banner listing pending commands as clickable chips

**Tabs** (each shows status indicator):
| Tab | ✓ When done | ● When pending | Content |
|-----|-------------|----------------|---------|
| Overview | /analiza ran | — | Pillar bars + key metrics + actors mini-grid |
| Análisis | /analiza ran | missing | Full 5-pillar report (Markdown) |
| Unit Econ. | /compounder ran | missing | ARR cohorts, LTV/CAC, NDR, payback |
| Actores | N/A | shows "X/10" | 10-actor grid, click to run, compare side-by-side |
| Tesis | /consejo ran | missing | Falsifiable thesis scorecard |
| Historia | always | — | Score evolution chart + past analyses list |
| Modelo | /modelo ran | missing | DCF output |

### Stage system

5 investment stages. Each ticker has one current stage derived from which commands have been run:

| Stage | Name | Required commands | Completed when |
|-------|------|-------------------|----------------|
| 1 | Descubrir | /sabueso result | Ticker added to watchlist |
| 2 | Analizar | /analiza | /analiza ran |
| 3 | Validar | /compounder + /consejo | Both ran |
| 4 | Decidir | /asignacion | /asignacion ran |
| 5 | Monitor | /chequea | At least one /chequea after buy |

Stage is computed client-side from Supabase history (which commands have results for this ticker).

### ⌘K Command Palette

Global keyboard shortcut `Ctrl+K` (Windows). Context-aware: knows active ticker.

**Search behavior:**
- Type a command name → filters and ranks commands
- Type a ticker symbol → opens that ticker's dossier
- Results grouped: "Pendientes en etapa actual" → "Actores" → "Todos los comandos"
- Already-run commands shown with green "ya corrido" label
- Pending commands shown with orange "pendiente" label

### LiveRunner component (shared by all commands)

Used whenever a command is running (analiza, compounder, morgan, etc.):
- **Left panel:** Stepper with agent steps (✓ done / ⏳ running / ○ pending) + elapsed time
- **Right panel:** Live log stream colored by agent (scout=purple, researcher=violet, boss=blue)
- On completion: stepper collapses to summary, report appears below

### Actors tab

10-actor grid. Each actor card:
- Icon + name + "ran" status
- Click → runs actor analysis via SSE, LiveRunner appears inline
- After running: shows actor's key outputs (rating, price target, conviction)
- "Correr todos" button → queues all 10 sequentially
- After 2+ actors run: comparison table appears (side-by-side ratings/PTs)

### Sabueso page (`/sabueso`)

Accessible via watchlist footer button or ⌘K "sabueso".

- Capital + horizon + strategy selectors
- "Cazar ahora" button → SSE stream with live results table
- Results: ticker, strategy tag (growth/value/quality/thematic), entry reason, CAGR, P/E, fit score
- Each row: "→ /analiza" link that opens ticker dossier and immediately starts analysis
- "Agregar a watchlist" button per row

---

## Error states

- **SSE disconnects mid-stream:** LiveRunner shows reconnect button, partial log preserved
- **Supabase unreachable:** Dashboard shows cached local state with "offline" badge; analysis still runs but shows "guardado solo en .md" warning
- **Claude API error:** Boss node error propagates as `{"type":"error"}` SSE event, shown inline in LiveRunner
- **Ticker not found:** Validated client-side before SSE request (same regex as `connectors/validators.py`)

---

## Token context considerations (Claude Pro)

The implementation plan is scoped to stay lean:
- `server.py`: ~80 lines (4 endpoints + static serving)
- `LiveRunner.jsx`: the most complex component (~150 lines) — SSE consumer + stepper state
- `CommandPalette.jsx`: ~120 lines
- All other components: ~50-80 lines each
- Total new code: ~900 lines across 17 files

Each file is independently implementable. The plan will sequence them so each step is verifiable before the next begins.

---

## Out of scope (v1)

- Authentication (local-only tool, no auth needed)
- Multi-user support
- Dark/light mode toggle (dark mode only)
- Mobile responsiveness
- Real-time price feeds
- Export to PDF
- Notifications / alerts
