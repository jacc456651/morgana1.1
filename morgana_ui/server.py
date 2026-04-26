import sys
import json
import logging
import asyncio
import threading
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from fastapi import FastAPI, Path as FPath, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from memory.supabase_client import get_supabase
from graph.morgana import build_graph
from agents.state import initial_state
from memory.save_analysis import extract_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("morgana.ui")

_GRAPH = None
_GRAPH_LOCK = threading.Lock()


def _get_graph():
    global _GRAPH
    if _GRAPH is None:
        with _GRAPH_LOCK:
            if _GRAPH is None:
                _GRAPH = build_graph()
    return _GRAPH


app = FastAPI(title="Morgana UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/analyses")
async def list_analyses():
    try:
        sb = get_supabase()
        result = (
            sb.table("analyses")
            .select("id,ticker,command,score_final,classification,decision,created_at")
            .order("created_at", desc=True)
            .limit(200)
            .execute()
        )
        return {"data": result.data or []}
    except Exception as exc:
        logger.error("Error fetching analyses: %s", exc)
        return {"data": [], "error": str(exc)}


@app.get("/api/analyses/{ticker}")
async def get_ticker_history(
    ticker: str = FPath(..., pattern=r"^[A-Z]{1,5}(-[A-Z])?$")
):
    try:
        sb = get_supabase()
        result = (
            sb.table("analyses")
            .select("*")
            .eq("ticker", ticker.upper())
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return {"data": result.data or []}
    except Exception as exc:
        logger.error("Error fetching ticker %s: %s", ticker, exc)
        return {"data": [], "error": str(exc)}


@app.get("/api/analyze")
async def analyze_sse(
    ticker: str = Query(..., pattern=r"^[A-Z]{1,5}(-[A-Z])?$"),
    command: str = Query(default="analiza"),
):
    """SSE stream: runs LangGraph graph and emits step/log/done/error events."""

    ALLOWED_COMMANDS = {"analiza", "compounder", "consejo", "chequea", "modelo"}
    if command not in ALLOWED_COMMANDS:
        command = "analiza"

    async def event_generator():
        q: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()
        cancel_event = threading.Event()
        t0 = time.time()

        def _run():
            try:
                logger.info("[analyze] Starting: ticker=%s command=%s", ticker, command)
                graph = _get_graph()
                state = initial_state(ticker.upper(), command)
                step_start = {}
                result_data = {"score": None, "decision": None, "analysis_id": None}

                for update in graph.stream(state, stream_mode="updates"):
                    if cancel_event.is_set():
                        break
                    node = list(update.keys())[0]
                    output = update[node]

                    if node not in step_start:
                        step_start[node] = time.time()
                        asyncio.run_coroutine_threadsafe(
                            q.put({"type": "step", "agent": node, "status": "running"}),
                            loop,
                        )

                    node_elapsed = round(time.time() - step_start[node], 1)
                    asyncio.run_coroutine_threadsafe(
                        q.put({
                            "type": "step",
                            "agent": node,
                            "status": "done",
                            "elapsed": node_elapsed,
                        }),
                        loop,
                    )

                    if node == "boss":
                        reporte = output.get("reporte", "")
                        result_data["score"] = extract_score(reporte)
                        result_data["decision"] = output.get("decision")

                    if node == "save":
                        result_data["analysis_id"] = output.get("analysis_id")

                asyncio.run_coroutine_threadsafe(
                    q.put({"type": "done", **result_data, "elapsed": round(time.time() - t0, 1)}),
                    loop,
                )
            except Exception as exc:
                logger.error("[analyze] Error: ticker=%s error=%s", ticker, exc)
                asyncio.run_coroutine_threadsafe(
                    q.put({"type": "error", "message": str(exc)}),
                    loop,
                )
            finally:
                asyncio.run_coroutine_threadsafe(q.put(None), loop)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

        try:
            while True:
                item = await q.get()
                if item is None:
                    break
                yield {"data": json.dumps(item, ensure_ascii=False)}
        except (asyncio.CancelledError, GeneratorExit):
            cancel_event.set()
            raise

    return EventSourceResponse(event_generator())


DIST_DIR = Path(__file__).parent / "app" / "dist"

if DIST_DIR.exists() and (DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(DIST_DIR / "index.html")
else:
    @app.get("/")
    async def dev_mode():
        return {"status": "dev", "message": "Run 'npm run build' in morgana_ui/app first"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)
