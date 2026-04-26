import sys
import json
import logging
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from memory.supabase_client import get_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("morgana.ui")

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
async def get_ticker_history(ticker: str):
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


DIST_DIR = Path(__file__).parent / "app" / "dist"

if DIST_DIR.exists():
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
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=False)
