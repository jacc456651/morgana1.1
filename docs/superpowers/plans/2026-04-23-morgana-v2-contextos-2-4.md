# MORGANA V2 — Plan Maestro: Contextos 2-4

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement each contexto task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Cómo usar este plan:**
Cada "Contexto" es una sesión independiente de Claude Code (~200k tokens).
Al inicio de cada sesión, di: *"Ejecuta el Contexto N del plan en docs/superpowers/plans/2026-04-23-morgana-v2-contextos-2-4.md"*

**Estado actual (post-Contexto 1):**
- ✅ LangGraph: Scout → Boss funcionando
- ✅ 18 tests pasando
- ✅ `py morgana.py analiza TICKER` en terminal
- ❌ Sin memoria persistente
- ❌ Sin inteligencia web
- ❌ Sin monitor de alertas

---

## CONTEXTO 2 — Supabase + Output .md (~200k tokens)

**Goal:** Cada análisis se guarda automáticamente en Supabase y escribe un reporte .md compatible con Obsidian.

**Prerequisitos antes de empezar:**
1. `.env` con `ANTHROPIC_API_KEY` y `SEC_USER_AGENT` rellenos
2. Smoke test exitoso: `py morgana.py analiza AAPL`
3. Cuenta Supabase (supabase.com — free tier): obtener `SUPABASE_URL` y `SUPABASE_ANON_KEY`
4. Agregar al `.env`: `SUPABASE_URL=https://xxx.supabase.co` y `SUPABASE_ANON_KEY=eyJ...`

**File Map:**

| Archivo | Rol |
|---|---|
| `memory/__init__.py` | Package marker |
| `memory/supabase_client.py` | Factory del cliente Supabase |
| `memory/save_analysis.py` | Guarda análisis en Supabase + extrae score/clasificación del reporte |
| `memory/write_report.py` | Escribe reporte .md a `output/reportes/[TICKER]/` |
| `memory/get_history.py` | Recupera análisis anteriores de Supabase para /chequea |
| `agents/state.py` | Agregar campo `analysis_id: Optional[str]` |
| `graph/morgana.py` | Agregar nodo `save` después de Boss |
| `morgana.py` | Agregar comando `chequea` al CLI |
| `tests/memory/test_save_analysis.py` | Tests de extracción de score/clasificación |
| `tests/memory/test_write_report.py` | Tests de escritura de .md |

---

### Tarea C2-1: Smoke test + instalar supabase-py

**Files:**
- Modify: `.env`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Verificar que el smoke test pasa**

```bash
py morgana.py analiza AAPL
```
Expected: Reporte con 5 pilares y decisión BUY/HOLD/AVOID impreso en terminal. Si falla, verificar `ANTHROPIC_API_KEY` en `.env`.

- [ ] **Step 2: Instalar supabase-py**

```bash
py -m pip install supabase
```

Verificar:
```bash
py -c "import supabase; print('supabase ok')"
```
Expected: `supabase ok`

- [ ] **Step 3: Crear tablas en Supabase**

Ir a supabase.com → proyecto → SQL Editor → ejecutar:

```sql
-- Tabla principal de análisis
CREATE TABLE IF NOT EXISTS analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker VARCHAR(10) NOT NULL,
  date TIMESTAMPTZ DEFAULT NOW(),
  command VARCHAR(50),
  score_final DECIMAL(5,2),
  classification VARCHAR(50),
  stage VARCHAR(20),
  decision VARCHAR(10),
  reporte TEXT,
  errors JSONB DEFAULT '[]'::jsonb
);

-- Watchlist activa
CREATE TABLE IF NOT EXISTS watchlist (
  ticker VARCHAR(10) PRIMARY KEY,
  added_date TIMESTAMPTZ DEFAULT NOW(),
  last_analysis_id UUID REFERENCES analyses(id),
  monitor_active BOOLEAN DEFAULT FALSE
);

-- Índices para queries rápidas
CREATE INDEX IF NOT EXISTS idx_analyses_ticker ON analyses(ticker);
CREATE INDEX IF NOT EXISTS idx_analyses_date ON analyses(date DESC);
```

- [ ] **Step 4: Agregar supabase al requirements.txt**

```
supabase>=2.0.0
```

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt
git commit -m "feat: add supabase-py dependency"
```

---

### Tarea C2-2: Cliente Supabase

**Files:**
- Create: `memory/__init__.py`
- Create: `memory/supabase_client.py`
- Create: `tests/memory/__init__.py`
- Create: `tests/memory/test_supabase_client.py`

- [ ] **Step 1: Crear directorios**

```bash
mkdir -p memory tests/memory
touch memory/__init__.py tests/memory/__init__.py
```

- [ ] **Step 2: Escribir el test**

Crear `tests/memory/test_supabase_client.py`:

```python
import os
from unittest.mock import patch
import pytest
from memory.supabase_client import get_supabase


def test_get_supabase_raises_without_url():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="SUPABASE_URL"):
            get_supabase()


def test_get_supabase_raises_without_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    with pytest.raises(ValueError, match="SUPABASE_ANON_KEY"):
        get_supabase()


def test_get_supabase_returns_client(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    client = get_supabase()
    assert client is not None
```

- [ ] **Step 3: Ejecutar test — debe fallar**

```bash
py -m pytest tests/memory/test_supabase_client.py -v
```
Expected: `ModuleNotFoundError: No module named 'memory.supabase_client'`

- [ ] **Step 4: Implementar memory/supabase_client.py**

```python
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url:
        raise ValueError("SUPABASE_URL es requerida en .env")
    if not key:
        raise ValueError("SUPABASE_ANON_KEY es requerida en .env")
    return create_client(url, key)
```

- [ ] **Step 5: Ejecutar test — debe pasar**

```bash
py -m pytest tests/memory/test_supabase_client.py -v
```
Expected: `3 passed`

- [ ] **Step 6: Commit**

```bash
git add memory/__init__.py memory/supabase_client.py tests/memory/__init__.py tests/memory/test_supabase_client.py
git commit -m "feat: add Supabase client factory"
```

---

### Tarea C2-3: Save analysis — extracción de score y guardado

**Files:**
- Create: `memory/save_analysis.py`
- Create: `tests/memory/test_save_analysis.py`

- [ ] **Step 1: Escribir el test**

Crear `tests/memory/test_save_analysis.py`:

```python
from unittest.mock import patch, MagicMock
from memory.save_analysis import extract_score, extract_classification, save_analysis

SAMPLE_REPORT = """
## AAPL — Apple Inc. | Analisis Morgana

**SCORE FINAL: 87/100 — COMPOUNDER ELITE**
**ETAPA:** Compounder
**DECISION: BUY**

### P1 — MOAT DINAMICO | Score: 9/10
Moat expansivo via ecosistema.
"""


def test_extract_score_from_report():
    assert extract_score(SAMPLE_REPORT) == 87.0


def test_extract_score_returns_none_when_missing():
    assert extract_score("reporte sin score") is None


def test_extract_classification_compounder_elite():
    assert extract_classification(SAMPLE_REPORT) == "COMPOUNDER ELITE"


def test_extract_classification_high_growth():
    report = "**SCORE FINAL: 75/100 — HIGH GROWTH**"
    assert extract_classification(report) == "HIGH GROWTH"


def test_extract_classification_watchlist():
    report = "**SCORE FINAL: 65/100 — WATCHLIST**"
    assert extract_classification(report) == "WATCHLIST"


def test_extract_classification_descartar():
    report = "**SCORE FINAL: 50/100 — DESCARTAR**"
    assert extract_classification(report) == "DESCARTAR"


@patch("memory.save_analysis.get_supabase")
def test_save_analysis_returns_id(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "test-uuid-123"}
    ]
    mock_get_sb.return_value = mock_sb

    result = save_analysis("AAPL", "analiza", SAMPLE_REPORT, "BUY", [])

    assert result == "test-uuid-123"
    mock_sb.table.assert_called_with("analyses")


@patch("memory.save_analysis.get_supabase")
def test_save_analysis_returns_none_on_error(mock_get_sb):
    mock_get_sb.side_effect = Exception("DB connection failed")

    result = save_analysis("AAPL", "analiza", SAMPLE_REPORT, "BUY", [])

    assert result is None
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
py -m pytest tests/memory/test_save_analysis.py -v
```
Expected: `ModuleNotFoundError: No module named 'memory.save_analysis'`

- [ ] **Step 3: Implementar memory/save_analysis.py**

```python
import re
import logging
from memory.supabase_client import get_supabase

logger = logging.getLogger("morgana.memory")


def extract_score(reporte: str) -> float | None:
    match = re.search(r"SCORE FINAL:\s*(\d+(?:\.\d+)?)/100", reporte)
    return float(match.group(1)) if match else None


def extract_classification(reporte: str) -> str | None:
    match = re.search(
        r"SCORE FINAL:.*?—\s*(COMPOUNDER ELITE|HIGH GROWTH|WATCHLIST|DESCARTAR)",
        reporte
    )
    return match.group(1) if match else None


def extract_stage(reporte: str) -> str | None:
    match = re.search(r"\*\*ETAPA:\*\*\s*(Early Growth|Scaling|Compounder)", reporte)
    return match.group(1) if match else None


def save_analysis(
    ticker: str, command: str, reporte: str, decision: str, errors: list
) -> str | None:
    """Guarda el análisis en Supabase. Retorna el UUID generado o None si falla."""
    try:
        sb = get_supabase()
        result = sb.table("analyses").insert({
            "ticker": ticker,
            "command": command,
            "score_final": extract_score(reporte),
            "classification": extract_classification(reporte),
            "stage": extract_stage(reporte),
            "decision": decision,
            "reporte": reporte,
            "errors": errors,
        }).execute()

        if result.data:
            analysis_id = result.data[0]["id"]
            logger.info("[Supabase] Análisis guardado: %s → %s", ticker, analysis_id)
            return analysis_id

    except Exception as exc:
        logger.warning("[Supabase] Error guardando análisis: %s", exc)

    return None
```

- [ ] **Step 4: Ejecutar test — debe pasar**

```bash
py -m pytest tests/memory/test_save_analysis.py -v
```
Expected: `8 passed`

- [ ] **Step 5: Commit**

```bash
git add memory/save_analysis.py tests/memory/test_save_analysis.py
git commit -m "feat: add save_analysis — Supabase persistence with score/classification extraction"
```

---

### Tarea C2-4: Writer de reportes .md (Obsidian-compatible)

**Files:**
- Create: `memory/write_report.py`
- Create: `tests/memory/test_write_report.py`

- [ ] **Step 1: Escribir el test**

Crear `tests/memory/test_write_report.py`:

```python
import os
from pathlib import Path
from unittest.mock import patch
from memory.write_report import write_report_md


def test_write_report_creates_file(tmp_path):
    report_path = write_report_md(
        ticker="AAPL",
        reporte="## AAPL\n**SCORE FINAL: 87/100**\n**DECISION: BUY**",
        decision="BUY",
        score=87.0,
        output_dir=str(tmp_path)
    )
    assert Path(report_path).exists()


def test_write_report_path_includes_ticker(tmp_path):
    report_path = write_report_md(
        ticker="MNDY",
        reporte="## MNDY\n**SCORE FINAL: 75/100**\n**DECISION: HOLD**",
        decision="HOLD",
        score=75.0,
        output_dir=str(tmp_path)
    )
    assert "MNDY" in report_path


def test_write_report_file_has_content(tmp_path):
    write_report_md(
        ticker="AAPL",
        reporte="## AAPL\n**SCORE FINAL: 87/100**\n**DECISION: BUY**",
        decision="BUY",
        score=87.0,
        output_dir=str(tmp_path)
    )
    files = list(Path(tmp_path).glob("AAPL/**/*.md"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "AAPL" in content
    assert "BUY" in content
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
py -m pytest tests/memory/test_write_report.py -v
```
Expected: `ModuleNotFoundError: No module named 'memory.write_report'`

- [ ] **Step 3: Implementar memory/write_report.py**

```python
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("morgana.memory")

DEFAULT_OUTPUT_DIR = "output/reportes"


def write_report_md(
    ticker: str,
    reporte: str,
    decision: str,
    score: float | None = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
) -> str:
    """
    Escribe el reporte de análisis como .md en output/reportes/[TICKER]/.
    Retorna la ruta del archivo creado.
    Compatible con Obsidian vault apuntando a output/.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    ticker_dir = Path(output_dir) / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{date_str}_analisis.md"
    filepath = ticker_dir / filename

    score_str = f"{score:.0f}" if score is not None else "N/A"
    frontmatter = f"""---
ticker: {ticker}
fecha: {date_str}
score: {score_str}
decision: {decision}
---

"""
    filepath.write_text(frontmatter + reporte, encoding="utf-8")
    logger.info("[Output] Reporte escrito: %s", filepath)
    return str(filepath)
```

- [ ] **Step 4: Ejecutar test — debe pasar**

```bash
py -m pytest tests/memory/test_write_report.py -v
```
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add memory/write_report.py tests/memory/test_write_report.py
git commit -m "feat: add write_report_md — Obsidian-compatible .md output"
```

---

### Tarea C2-5: Integrar memoria en el grafo

**Files:**
- Modify: `agents/state.py` — agregar `analysis_id`
- Create: `agents/save_node.py` — nodo de persistencia
- Modify: `graph/morgana.py` — añadir nodo save al grafo
- Modify: `tests/agents/test_state.py` — actualizar test
- Create: `tests/agents/test_save_node.py`

- [ ] **Step 1: Escribir test del nodo save**

Crear `tests/agents/test_save_node.py`:

```python
from unittest.mock import patch
from agents.save_node import save_node
from agents.state import initial_state


@patch("agents.save_node.write_report_md", return_value="output/reportes/AAPL/2026-04-23_analisis.md")
@patch("agents.save_node.save_analysis", return_value="uuid-123")
def test_save_node_persists_analysis(mock_save, mock_write):
    state = initial_state("AAPL", "analiza")
    state["reporte"] = "## AAPL\n**SCORE FINAL: 87/100**\n**DECISION: BUY**"
    state["decision"] = "BUY"
    state["errors"] = []

    result = save_node(state)

    assert mock_save.called
    assert mock_write.called
    assert result.get("analysis_id") == "uuid-123"
    assert result.get("report_path") == "output/reportes/AAPL/2026-04-23_analisis.md"


@patch("agents.save_node.write_report_md", side_effect=Exception("disk full"))
@patch("agents.save_node.save_analysis", return_value="uuid-123")
def test_save_node_continues_on_write_error(mock_save, mock_write):
    state = initial_state("AAPL", "analiza")
    state["reporte"] = "## AAPL"
    state["decision"] = "BUY"
    state["errors"] = []

    result = save_node(state)
    # No debe lanzar excepción
    assert "analysis_id" in result or "errors" in result
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
py -m pytest tests/agents/test_save_node.py -v
```
Expected: `ModuleNotFoundError: No module named 'agents.save_node'`

- [ ] **Step 3: Actualizar agents/state.py**

Agregar `analysis_id` y `report_path` al TypedDict:

```python
from typing import TypedDict, Optional


class MorganaState(TypedDict):
    ticker: str
    command: str
    datos_financieros: Optional[dict]
    reporte: Optional[str]
    decision: Optional[str]
    errors: list
    analysis_id: Optional[str]
    report_path: Optional[str]


def initial_state(ticker: str, command: str) -> MorganaState:
    return {
        "ticker": ticker.upper(),
        "command": command,
        "datos_financieros": None,
        "reporte": None,
        "decision": None,
        "errors": [],
        "analysis_id": None,
        "report_path": None,
    }
```

- [ ] **Step 4: Implementar agents/save_node.py**

```python
import logging
from agents.state import MorganaState
from memory.save_analysis import save_analysis, extract_score
from memory.write_report import write_report_md

logger = logging.getLogger("morgana.save")


def save_node(state: MorganaState) -> dict:
    """
    Nodo de persistencia: guarda el análisis en Supabase y escribe el .md.
    Se ejecuta después de Boss. Nunca bloquea el flujo aunque falle.
    """
    ticker = state["ticker"]
    reporte = state.get("reporte") or ""
    decision = state.get("decision") or "HOLD"
    errors = list(state.get("errors", []))
    result = {}

    # Guardar en Supabase
    try:
        analysis_id = save_analysis(
            ticker=ticker,
            command=state.get("command", "analiza"),
            reporte=reporte,
            decision=decision,
            errors=errors,
        )
        if analysis_id:
            result["analysis_id"] = analysis_id
    except Exception as exc:
        logger.warning("[Save] Supabase falló: %s", exc)
        errors.append(f"[Save] Supabase: {exc}")

    # Escribir .md
    try:
        score = extract_score(reporte)
        report_path = write_report_md(
            ticker=ticker,
            reporte=reporte,
            decision=decision,
            score=score,
        )
        result["report_path"] = report_path
        print(f"   [Output] Reporte guardado: {report_path}")
    except Exception as exc:
        logger.warning("[Save] Write .md falló: %s", exc)
        errors.append(f"[Save] Write .md: {exc}")

    result["errors"] = errors
    return result
```

- [ ] **Step 5: Ejecutar test — debe pasar**

```bash
py -m pytest tests/agents/test_save_node.py -v
```
Expected: `2 passed`

- [ ] **Step 6: Actualizar graph/morgana.py**

```python
from langgraph.graph import StateGraph, END
from agents.state import MorganaState
from agents.scout import scout_node
from agents.boss import boss_node
from agents.save_node import save_node


def build_graph():
    """Construye y compila el grafo LangGraph de Morgana."""
    graph = StateGraph(MorganaState)

    graph.add_node("scout", scout_node)
    graph.add_node("boss", boss_node)
    graph.add_node("save", save_node)

    graph.set_entry_point("scout")
    graph.add_edge("scout", "boss")
    graph.add_edge("boss", "save")
    graph.add_edge("save", END)

    return graph.compile()
```

- [ ] **Step 7: Ejecutar todos los tests**

```bash
py -m pytest tests/ -v --tb=short -q
```
Expected: Todos los tests pasan (20+ passed)

- [ ] **Step 8: Commit**

```bash
git add agents/state.py agents/save_node.py graph/morgana.py tests/agents/test_save_node.py
git commit -m "feat: add save_node — auto-persist analysis to Supabase + write .md report"
```

---

### Tarea C2-6: Comando /chequea en CLI + get_history

**Files:**
- Create: `memory/get_history.py`
- Create: `tests/memory/test_get_history.py`
- Modify: `morgana.py` — agregar comando `chequea`

- [ ] **Step 1: Escribir el test**

Crear `tests/memory/test_get_history.py`:

```python
from unittest.mock import patch, MagicMock
from memory.get_history import get_last_analysis, get_analysis_count


@patch("memory.get_history.get_supabase")
def test_get_last_analysis_returns_dict(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"ticker": "AAPL", "score_final": 87.0, "decision": "BUY", "date": "2026-04-23"}
    ]
    mock_get_sb.return_value = mock_sb

    result = get_last_analysis("AAPL")

    assert result is not None
    assert result["ticker"] == "AAPL"
    assert result["decision"] == "BUY"


@patch("memory.get_history.get_supabase")
def test_get_last_analysis_returns_none_when_empty(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    mock_get_sb.return_value = mock_sb

    result = get_last_analysis("NEWCO")
    assert result is None


@patch("memory.get_history.get_supabase")
def test_get_analysis_count(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.count = 5
    mock_get_sb.return_value = mock_sb

    count = get_analysis_count("AAPL")
    assert count == 5
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
py -m pytest tests/memory/test_get_history.py -v
```
Expected: `ModuleNotFoundError: No module named 'memory.get_history'`

- [ ] **Step 3: Implementar memory/get_history.py**

```python
import logging
from memory.supabase_client import get_supabase

logger = logging.getLogger("morgana.history")


def get_last_analysis(ticker: str) -> dict | None:
    """Recupera el análisis más reciente de un ticker desde Supabase."""
    try:
        sb = get_supabase()
        result = (
            sb.table("analyses")
            .select("*")
            .eq("ticker", ticker.upper())
            .order("date", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception as exc:
        logger.warning("[History] Error recuperando análisis de %s: %s", ticker, exc)
    return None


def get_analysis_count(ticker: str) -> int:
    """Cuenta cuántos análisis existen para un ticker."""
    try:
        sb = get_supabase()
        result = (
            sb.table("analyses")
            .select("id", count="exact")
            .eq("ticker", ticker.upper())
            .execute()
        )
        return result.count or 0
    except Exception as exc:
        logger.warning("[History] Error contando análisis de %s: %s", ticker, exc)
        return 0
```

- [ ] **Step 4: Ejecutar test — debe pasar**

```bash
py -m pytest tests/memory/test_get_history.py -v
```
Expected: `3 passed`

- [ ] **Step 5: Actualizar morgana.py — agregar comando chequea**

Reemplazar la sección `COMMANDS` y la función `main()` en `morgana.py`:

```python
#!/usr/bin/env python3
"""
MORGANA — Sistema de Inversion Growth Institucional
Uso:
  py morgana.py analiza TICKER    — Análisis completo
  py morgana.py chequea TICKER    — Ver historial + re-análisis rápido
"""
import sys
import logging
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s — %(message)s")

COMMANDS = {"analiza", "chequea"}

HELP = """
MORGANA — Inversion Growth Institucional

Comandos:
  py morgana.py analiza TICKER    Analisis completo 5 pilares
  py morgana.py chequea TICKER    Historial + re-analisis comparativo

Ejemplos:
  py morgana.py analiza AAPL
  py morgana.py chequea MNDY
"""


def cmd_analiza(ticker: str):
    print(f"\nAnalizando {ticker}...\n")
    print("   [Scout] Recolectando datos...")

    from graph.morgana import build_graph
    from agents.state import initial_state

    graph = build_graph()
    result = graph.invoke(initial_state(ticker, "analiza"))

    print("\n" + "=" * 60)
    print(result.get("reporte", "No se genero reporte."))
    print("=" * 60)

    if result.get("report_path"):
        print(f"\n   Reporte guardado: {result['report_path']}")
    if result.get("analysis_id"):
        print(f"   ID Supabase: {result['analysis_id']}")
    if result.get("errors"):
        print(f"\nAdvertencias ({len(result['errors'])}):")
        for err in result["errors"]:
            print(f"   - {err}")

    print(f"\nDecision final: {result.get('decision', 'N/A')}")


def cmd_chequea(ticker: str):
    from memory.get_history import get_last_analysis, get_analysis_count

    count = get_analysis_count(ticker)
    last = get_last_analysis(ticker)

    print(f"\n=== Historial {ticker} ===")
    print(f"Analisis guardados: {count}")

    if last:
        print(f"\nUltimo analisis ({last.get('date', 'N/A')[:10]}):")
        print(f"  Score:     {last.get('score_final', 'N/A')}/100")
        print(f"  Clasif.:   {last.get('classification', 'N/A')}")
        print(f"  Decision:  {last.get('decision', 'N/A')}")
        print(f"\nReporte anterior:\n")
        print(last.get("reporte", "")[:2000])
        if len(last.get("reporte", "")) > 2000:
            print("... [reporte truncado, ver archivo .md para version completa]")
    else:
        print(f"  Sin analisis previos para {ticker}.")
        print(f"  Ejecuta: py morgana.py analiza {ticker}")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in COMMANDS:
        print(HELP)
        sys.exit(0)

    command = sys.argv[1]
    ticker = sys.argv[2].upper()

    try:
        if command == "analiza":
            cmd_analiza(ticker)
        elif command == "chequea":
            cmd_chequea(ticker)
    except Exception as exc:
        print(f"\nError: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Ejecutar todos los tests**

```bash
py -m pytest tests/ -q --tb=short
```
Expected: Todos pasan (25+ passed)

- [ ] **Step 7: Commit final del Contexto 2**

```bash
git add memory/get_history.py morgana.py tests/memory/test_get_history.py
git commit -m "feat: add /chequea command and get_history — retrieve analysis from Supabase"
```

---

## CONTEXTO 3 — Researcher Agent + Perplexity (~200k tokens)

**Goal:** El análisis incluye noticias recientes, contexto competitivo y eventos de management del último mes.

**Prerequisitos:**
1. Contexto 2 completo y verificado
2. Cuenta Perplexity API (perplexity.ai/api) — free tier disponible
3. Agregar al `.env`: `PERPLEXITY_API_KEY=pplx-...`

**File Map:**

| Archivo | Rol |
|---|---|
| `connectors/perplexity.py` | Cliente Perplexity API — 3 queries específicas por ticker |
| `agents/researcher.py` | Nodo Researcher: ejecuta queries Perplexity + estructura contexto web |
| `agents/state.py` | Agregar campo `contexto_web: Optional[dict]` |
| `graph/morgana.py` | Actualizar grafo: Scout → Researcher → Boss → Save |
| `agents/boss.py` | Actualizar prompt para incluir `contexto_web` del estado |
| `tests/connectors/test_perplexity.py` | Tests del conector Perplexity |
| `tests/agents/test_researcher.py` | Tests del Researcher node |
| `tests/graph/test_graph_researcher.py` | Test del grafo con 4 nodos |

---

### Tarea C3-1: Conector Perplexity

**Files:**
- Create: `connectors/perplexity.py`
- Create: `tests/connectors/__init__.py`
- Create: `tests/connectors/test_perplexity.py`

- [ ] **Step 1: Instalar openai (Perplexity usa API compatible OpenAI)**

```bash
py -m pip install openai
```

Verificar:
```bash
py -c "import openai; print('openai ok')"
```

- [ ] **Step 2: Escribir el test**

Crear `tests/connectors/test_perplexity.py`:

```python
import os
from unittest.mock import patch, MagicMock
from connectors.perplexity import search_web, get_ticker_context


def _mock_completion(content: str):
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


@patch("connectors.perplexity._get_client")
def test_search_web_returns_string(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_completion("AAPL news: product launch")
    mock_get_client.return_value = mock_client

    result = search_web("AAPL recent news")

    assert isinstance(result, str)
    assert len(result) > 0


@patch("connectors.perplexity._get_client")
def test_get_ticker_context_returns_three_sections(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_completion("Context info here")
    mock_get_client.return_value = mock_client

    result = get_ticker_context("AAPL")

    assert "noticias" in result
    assert "competidores" in result
    assert "management" in result


@patch("connectors.perplexity._get_client")
def test_get_ticker_context_handles_error(mock_get_client):
    mock_get_client.side_effect = Exception("API unavailable")

    result = get_ticker_context("AAPL")

    assert isinstance(result, dict)
    # Retorna dict con errores en lugar de lanzar excepción
    assert all(isinstance(v, str) for v in result.values())
```

- [ ] **Step 3: Ejecutar test — debe fallar**

```bash
py -m pytest tests/connectors/test_perplexity.py -v
```
Expected: `ModuleNotFoundError`

- [ ] **Step 4: Implementar connectors/perplexity.py**

```python
"""
Connector para Perplexity API.
Usa la API compatible con OpenAI. Requiere PERPLEXITY_API_KEY en .env.
"""
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logger = logging.getLogger("morgana.perplexity")

PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
MODEL = "llama-3.1-sonar-large-128k-online"


def _get_client() -> OpenAI:
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY requerida en .env")
    return OpenAI(api_key=api_key, base_url=PERPLEXITY_BASE_URL)


def search_web(query: str, max_tokens: int = 800) -> str:
    """Ejecuta una búsqueda web via Perplexity. Retorna texto con fuentes."""
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente de investigación financiera. Responde en español, con datos concretos y cita las fuentes cuando sea posible.",
            },
            {"role": "user", "content": query},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def get_ticker_context(ticker: str) -> dict:
    """
    Ejecuta 3 búsquedas específicas para un ticker.
    Retorna dict con: noticias, competidores, management.
    Nunca lanza excepción — retorna strings vacíos si falla.
    """
    queries = {
        "noticias": f"{ticker} stock news earnings results last 30 days 2026",
        "competidores": f"{ticker} competitors market share competitive landscape 2026",
        "management": f"{ticker} CEO management team recent decisions strategy 2026",
    }

    context = {}
    for key, query in queries.items():
        try:
            context[key] = search_web(query)
            logger.info("[Perplexity] Query '%s' para %s OK", key, ticker)
        except Exception as exc:
            logger.warning("[Perplexity] Query '%s' falló: %s", key, exc)
            context[key] = f"No disponible ({exc})"

    return context
```

- [ ] **Step 5: Ejecutar test — debe pasar**

```bash
py -m pytest tests/connectors/test_perplexity.py -v
```
Expected: `3 passed`

- [ ] **Step 6: Commit**

```bash
git add connectors/perplexity.py tests/connectors/__init__.py tests/connectors/test_perplexity.py
git commit -m "feat: add Perplexity connector — web search for news/competitors/management"
```

---

### Tarea C3-2: Researcher agent

**Files:**
- Create: `agents/researcher.py`
- Modify: `agents/state.py` — agregar `contexto_web`
- Create: `tests/agents/test_researcher.py`

- [ ] **Step 1: Escribir el test**

Crear `tests/agents/test_researcher.py`:

```python
from unittest.mock import patch
from agents.researcher import researcher_node
from agents.state import initial_state


@patch("agents.researcher.get_ticker_context", return_value={
    "noticias": "AAPL lanza nuevo iPhone con chip M4",
    "competidores": "Samsung y Google son los principales rivales",
    "management": "Tim Cook enfoca en servicios y AI",
})
def test_researcher_node_adds_web_context(mock_perplexity):
    state = initial_state("AAPL", "analiza")
    result = researcher_node(state)

    assert "contexto_web" in result
    ctx = result["contexto_web"]
    assert "noticias" in ctx
    assert "competidores" in ctx
    assert "management" in ctx


@patch("agents.researcher.get_ticker_context", side_effect=Exception("Perplexity down"))
def test_researcher_node_handles_perplexity_failure(mock_perplexity):
    state = initial_state("AAPL", "analiza")
    result = researcher_node(state)

    # No lanza excepción — retorna contexto vacío o con error
    assert "contexto_web" in result
    assert isinstance(result["contexto_web"], dict)
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
py -m pytest tests/agents/test_researcher.py -v
```
Expected: `ModuleNotFoundError: No module named 'agents.researcher'`

- [ ] **Step 3: Actualizar agents/state.py — agregar contexto_web**

```python
from typing import TypedDict, Optional


class MorganaState(TypedDict):
    ticker: str
    command: str
    datos_financieros: Optional[dict]
    contexto_web: Optional[dict]
    reporte: Optional[str]
    decision: Optional[str]
    errors: list
    analysis_id: Optional[str]
    report_path: Optional[str]


def initial_state(ticker: str, command: str) -> MorganaState:
    return {
        "ticker": ticker.upper(),
        "command": command,
        "datos_financieros": None,
        "contexto_web": None,
        "reporte": None,
        "decision": None,
        "errors": [],
        "analysis_id": None,
        "report_path": None,
    }
```

- [ ] **Step 4: Implementar agents/researcher.py**

```python
import logging
from agents.state import MorganaState
from connectors.perplexity import get_ticker_context

logger = logging.getLogger("morgana.researcher")


def researcher_node(state: MorganaState) -> dict:
    """
    Nodo Researcher: obtiene contexto web via Perplexity.
    Ejecuta 3 búsquedas en paralelo: noticias, competidores, management.
    Nunca bloquea el flujo aunque Perplexity falle.
    """
    ticker = state["ticker"]
    errors = list(state.get("errors", []))

    try:
        context = get_ticker_context(ticker)
        logger.info("[Researcher] Contexto web obtenido para %s", ticker)
        return {"contexto_web": context, "errors": errors}
    except Exception as exc:
        error_msg = f"[Researcher] Perplexity falló: {exc}"
        logger.warning(error_msg)
        errors.append(error_msg)
        return {"contexto_web": {}, "errors": errors}
```

- [ ] **Step 5: Ejecutar test — debe pasar**

```bash
py -m pytest tests/agents/test_researcher.py -v
```
Expected: `2 passed`

- [ ] **Step 6: Actualizar graph/morgana.py — Scout → Researcher → Boss → Save**

```python
from langgraph.graph import StateGraph, END
from agents.state import MorganaState
from agents.scout import scout_node
from agents.researcher import researcher_node
from agents.boss import boss_node
from agents.save_node import save_node


def build_graph():
    """Construye y compila el grafo LangGraph de Morgana."""
    graph = StateGraph(MorganaState)

    graph.add_node("scout", scout_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("boss", boss_node)
    graph.add_node("save", save_node)

    graph.set_entry_point("scout")
    graph.add_edge("scout", "researcher")
    graph.add_edge("researcher", "boss")
    graph.add_edge("boss", "save")
    graph.add_edge("save", END)

    return graph.compile()
```

- [ ] **Step 7: Actualizar agents/boss.py — incluir contexto_web en el prompt**

En `ANALYSIS_TEMPLATE`, reemplazar la sección de datos con:

```python
ANALYSIS_TEMPLATE = """Analiza {ticker} usando los siguientes datos:

=== DATOS FINANCIEROS (EDGAR/Yahoo/Finviz) ===
{datos_json}

=== CONTEXTO WEB RECIENTE (Perplexity, últimos 30 días) ===
NOTICIAS:
{noticias}

COMPETIDORES:
{competidores}

MANAGEMENT:
{management}

=== INSTRUCCION ===
Genera un reporte completo con esta estructura EXACTA:
...
[resto del template igual]
"""
```

Y en `boss_node`, actualizar el prompt:

```python
contexto_web = state.get("contexto_web") or {}
prompt = ANALYSIS_TEMPLATE.format(
    ticker=ticker,
    datos_json=datos_str,
    noticias=contexto_web.get("noticias", "No disponible"),
    competidores=contexto_web.get("competidores", "No disponible"),
    management=contexto_web.get("management", "No disponible"),
)
```

- [ ] **Step 8: Ejecutar todos los tests**

```bash
py -m pytest tests/ -q --tb=short
```
Expected: Todos pasan (30+ passed)

- [ ] **Step 9: Commit final Contexto 3**

```bash
git add agents/researcher.py agents/state.py agents/boss.py graph/morgana.py tests/agents/test_researcher.py
git commit -m "feat: add Researcher agent — Perplexity web context enriches Boss analysis"
```

---

## CONTEXTO 4 — Monitor Agent + /seguimiento (~200k tokens)

**Goal:** Vigilancia activa en background. `/seguimiento TICKER` activa alertas cuando hay noticias relevantes.

**Prerequisitos:**
- Contextos 2 y 3 completos
- Perplexity API funcionando

**File Map:**

| Archivo | Rol |
|---|---|
| `agents/monitor.py` | Nodo Monitor: evalúa si noticia impacta algún pilar (Haiku) |
| `memory/watchlist.py` | Agrega/elimina tickers de la watchlist en Supabase |
| `morgana.py` | Agregar comandos `seguimiento` y `watchlist` al CLI |
| `tests/agents/test_monitor.py` | Tests del Monitor node |
| `tests/memory/test_watchlist.py` | Tests de watchlist |

---

### Tarea C4-1: Monitor agent (Haiku)

**Files:**
- Create: `agents/monitor.py`
- Create: `tests/agents/test_monitor.py`

- [ ] **Step 1: Actualizar agents/config.py — agregar MONITOR_MODEL**

```python
BOSS_MODEL = "claude-opus-4-6"
SCOUT_MODEL = "claude-sonnet-4-6"
MONITOR_MODEL = "claude-haiku-4-5-20251001"
```

- [ ] **Step 2: Escribir el test**

Crear `tests/agents/test_monitor.py`:

```python
from unittest.mock import patch, MagicMock
from agents.monitor import evaluate_news_impact, IMPACT_THRESHOLD


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def test_impact_threshold_is_between_1_and_10():
    assert 1 <= IMPACT_THRESHOLD <= 10


@patch("agents.monitor.get_claude_client")
def test_evaluate_news_low_impact_returns_false(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(
        "IMPACTO: 2\nPILAR: ninguno\nRESUMEN: Noticia irrelevante para la tesis."
    )
    mock_get_client.return_value = mock_client

    result = evaluate_news_impact("AAPL", "Apple lanza nuevos colores para iPhone case")

    assert result["impacto"] == 2
    assert result["escalar"] is False


@patch("agents.monitor.get_claude_client")
def test_evaluate_news_high_impact_returns_true(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(
        "IMPACTO: 8\nPILAR: P3\nRESUMEN: CEO renuncia abruptamente, riesgo P4 Management."
    )
    mock_get_client.return_value = mock_client

    result = evaluate_news_impact("AAPL", "CEO Tim Cook anuncia renuncia inmediata")

    assert result["impacto"] == 8
    assert result["escalar"] is True
    assert "P" in result.get("pilar", "")


@patch("agents.monitor.get_claude_client")
def test_evaluate_news_handles_parse_error(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response("respuesta malformada sin estructura")
    mock_get_client.return_value = mock_client

    result = evaluate_news_impact("AAPL", "Some news")
    assert "impacto" in result
    assert "escalar" in result
```

- [ ] **Step 3: Ejecutar test — debe fallar**

```bash
py -m pytest tests/agents/test_monitor.py -v
```
Expected: `ModuleNotFoundError: No module named 'agents.monitor'`

- [ ] **Step 4: Implementar agents/monitor.py**

```python
import re
import logging
from agents.config import get_claude_client, MONITOR_MODEL

logger = logging.getLogger("morgana.monitor")

IMPACT_THRESHOLD = 5

MONITOR_SYSTEM = """Eres el Monitor de MORGANA — evaluador de impacto de noticias financieras.

Tu tarea: dado un ticker y una noticia, evalúa si impacta materialmente alguno de los 5 pilares de análisis.

Pilares: P1 (Moat), P2 (Finanzas), P3 (Motor de crecimiento), P4 (Management), P5 (Contexto/Timing)

Responde EXACTAMENTE en este formato:
IMPACTO: [número del 1 al 10]
PILAR: [P1/P2/P3/P4/P5/ninguno]
RESUMEN: [una oración explicando el impacto]
"""


def evaluate_news_impact(ticker: str, noticia: str) -> dict:
    """
    Evalúa si una noticia impacta materialmente algún pilar de análisis.
    Usa Haiku (modelo más barato) para minimizar costo.
    Retorna dict con: impacto (1-10), pilar, escalar (bool), resumen.
    """
    try:
        client = get_claude_client()
        response = client.messages.create(
            model=MONITOR_MODEL,
            max_tokens=200,
            system=MONITOR_SYSTEM,
            messages=[{
                "role": "user",
                "content": f"Ticker: {ticker}\nNoticia: {noticia}"
            }],
        )
        text = response.content[0].text

        impacto = 1
        pilar = "ninguno"
        resumen = ""

        match_impacto = re.search(r"IMPACTO:\s*(\d+)", text)
        if match_impacto:
            impacto = min(10, max(1, int(match_impacto.group(1))))

        match_pilar = re.search(r"PILAR:\s*(P[1-5]|ninguno)", text, re.IGNORECASE)
        if match_pilar:
            pilar = match_pilar.group(1)

        match_resumen = re.search(r"RESUMEN:\s*(.+)", text)
        if match_resumen:
            resumen = match_resumen.group(1).strip()

        escalar = impacto >= IMPACT_THRESHOLD
        logger.info("[Monitor] %s — Impacto: %d/10, Pilar: %s, Escalar: %s",
                    ticker, impacto, pilar, escalar)

        return {"impacto": impacto, "pilar": pilar, "escalar": escalar, "resumen": resumen}

    except Exception as exc:
        logger.warning("[Monitor] Error evaluando noticia: %s", exc)
        return {"impacto": 1, "pilar": "ninguno", "escalar": False, "resumen": str(exc)}
```

- [ ] **Step 5: Ejecutar test — debe pasar**

```bash
py -m pytest tests/agents/test_monitor.py -v
```
Expected: `4 passed`

- [ ] **Step 6: Commit**

```bash
git add agents/monitor.py agents/config.py tests/agents/test_monitor.py
git commit -m "feat: add Monitor agent — Haiku-powered news impact evaluator"
```

---

### Tarea C4-2: Watchlist + /seguimiento en CLI

**Files:**
- Create: `memory/watchlist.py`
- Create: `tests/memory/test_watchlist.py`
- Modify: `morgana.py` — comandos `seguimiento` y `watchlist`

- [ ] **Step 1: Escribir el test**

Crear `tests/memory/test_watchlist.py`:

```python
from unittest.mock import patch, MagicMock
from memory.watchlist import add_to_watchlist, remove_from_watchlist, get_active_watchlist


@patch("memory.watchlist.get_supabase")
def test_add_to_watchlist(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.upsert.return_value.execute.return_value.data = [{"ticker": "AAPL"}]
    mock_get_sb.return_value = mock_sb

    result = add_to_watchlist("AAPL")
    assert result is True
    mock_sb.table.assert_called_with("watchlist")


@patch("memory.watchlist.get_supabase")
def test_remove_from_watchlist(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"ticker": "AAPL"}]
    mock_get_sb.return_value = mock_sb

    result = remove_from_watchlist("AAPL")
    assert result is True


@patch("memory.watchlist.get_supabase")
def test_get_active_watchlist_returns_list(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"ticker": "AAPL"}, {"ticker": "MNDY"}
    ]
    mock_get_sb.return_value = mock_sb

    tickers = get_active_watchlist()
    assert "AAPL" in tickers
    assert "MNDY" in tickers
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
py -m pytest tests/memory/test_watchlist.py -v
```
Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implementar memory/watchlist.py**

```python
import logging
from memory.supabase_client import get_supabase

logger = logging.getLogger("morgana.watchlist")


def add_to_watchlist(ticker: str) -> bool:
    """Agrega ticker a la watchlist con monitoreo activo."""
    try:
        sb = get_supabase()
        sb.table("watchlist").upsert({
            "ticker": ticker.upper(),
            "monitor_active": True,
        }).execute()
        logger.info("[Watchlist] %s agregado", ticker)
        return True
    except Exception as exc:
        logger.warning("[Watchlist] Error agregando %s: %s", ticker, exc)
        return False


def remove_from_watchlist(ticker: str) -> bool:
    """Desactiva monitoreo de un ticker."""
    try:
        sb = get_supabase()
        sb.table("watchlist").update({"monitor_active": False}).eq("ticker", ticker.upper()).execute()
        logger.info("[Watchlist] %s desactivado", ticker)
        return True
    except Exception as exc:
        logger.warning("[Watchlist] Error desactivando %s: %s", ticker, exc)
        return False


def get_active_watchlist() -> list[str]:
    """Retorna lista de tickers con monitoreo activo."""
    try:
        sb = get_supabase()
        result = sb.table("watchlist").select("ticker").eq("monitor_active", True).execute()
        return [row["ticker"] for row in (result.data or [])]
    except Exception as exc:
        logger.warning("[Watchlist] Error obteniendo watchlist: %s", exc)
        return []
```

- [ ] **Step 4: Ejecutar test — debe pasar**

```bash
py -m pytest tests/memory/test_watchlist.py -v
```
Expected: `3 passed`

- [ ] **Step 5: Agregar comandos seguimiento y watchlist a morgana.py**

Agregar estas funciones antes de `main()`:

```python
def cmd_seguimiento(ticker: str):
    from memory.watchlist import add_to_watchlist
    ok = add_to_watchlist(ticker)
    if ok:
        print(f"\n{ticker} agregado a watchlist con monitoreo activo.")
        print(f"Usa 'py morgana.py watchlist' para ver todos los tickers monitoreados.")
    else:
        print(f"\nError: no se pudo agregar {ticker} a watchlist. Verificar SUPABASE en .env")


def cmd_watchlist():
    from memory.watchlist import get_active_watchlist
    tickers = get_active_watchlist()
    if tickers:
        print(f"\nWatchlist activa ({len(tickers)} tickers):")
        for t in tickers:
            print(f"  - {t}")
    else:
        print("\nWatchlist vacía. Usa: py morgana.py seguimiento TICKER")
```

Actualizar `COMMANDS` y `main()`:

```python
COMMANDS = {"analiza", "chequea", "seguimiento", "watchlist"}

# En main():
elif command == "seguimiento":
    cmd_seguimiento(ticker)
elif command == "watchlist":
    cmd_watchlist()
```

Para `watchlist` (sin ticker), ajustar el parsing en `main()`:

```python
def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(HELP)
        sys.exit(0)

    command = sys.argv[1]
    ticker = sys.argv[2].upper() if len(sys.argv) >= 3 else ""

    if command in {"analiza", "chequea", "seguimiento"} and not ticker:
        print(f"Error: falta el ticker. Uso: py morgana.py {command} TICKER")
        sys.exit(1)

    try:
        if command == "analiza":
            cmd_analiza(ticker)
        elif command == "chequea":
            cmd_chequea(ticker)
        elif command == "seguimiento":
            cmd_seguimiento(ticker)
        elif command == "watchlist":
            cmd_watchlist()
    except Exception as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
```

- [ ] **Step 6: Ejecutar todos los tests**

```bash
py -m pytest tests/ -q --tb=short
```
Expected: Todos pasan (35+ passed)

- [ ] **Step 7: Commit final Contexto 4**

```bash
git add agents/monitor.py memory/watchlist.py morgana.py tests/memory/test_watchlist.py
git commit -m "feat: add /seguimiento + /watchlist — active monitoring with Haiku alert evaluator"
```

---

## Resumen de Contextos

| Contexto | Resultado | Comandos nuevos |
|---|---|---|
| **1** (hecho) | LangGraph Scout → Boss funcionando | `py morgana.py analiza TICKER` |
| **2** | Supabase + reportes .md | + `chequea` |
| **3** | Researcher + Perplexity | análisis enriquecido |
| **4** | Monitor + Watchlist | + `seguimiento`, `watchlist` |

**Al terminar Contexto 4, Morgana V2 Semana 1-4 estará completa.**
Los MCPs premium (Morningstar, FactSet, etc.) se activan cuando el sistema base esté estable.
