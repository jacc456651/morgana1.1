import logging
from datetime import datetime
from pathlib import Path

from memory.save_analysis import extract_classification, extract_stage, extract_pillars

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
    Escribe el reporte como .md en output/reportes/[TICKER]/ con frontmatter
    rico compatible con Obsidian vault (Dataview queries sobre pilares, etapa, etc.)
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    ticker_dir = Path(output_dir) / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{date_str}_analisis.md"
    filepath = ticker_dir / filename

    score_str = f"{score:.0f}" if score is not None else "N/A"
    clasificacion = extract_classification(reporte) or "N/A"
    etapa = extract_stage(reporte) or "N/A"
    pillars = extract_pillars(reporte)
    pillars_yaml = "\n".join(
        f"  P{i}: {pillars.get(f'P{i}', 'N/A')}" for i in range(1, 6)
    )

    frontmatter = f"""---
ticker: {ticker}
fecha: {date_str}
score: {score_str}
clasificacion: {clasificacion}
etapa: {etapa}
decision: {decision}
pilares:
{pillars_yaml}
tags: []
---

"""
    filepath.write_text(frontmatter + reporte, encoding="utf-8")
    logger.info("[Output] Reporte escrito: %s", filepath)
    return str(filepath)
