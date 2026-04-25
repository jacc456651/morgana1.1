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
