"""
Lee análisis previos del vault de Obsidian (output/reportes/) para dar
contexto histórico al sistema antes de cada nuevo análisis.
El Boss usa este historial para detectar cambios de conviction y evolución.
"""
import re
import logging
from pathlib import Path

logger = logging.getLogger("morgana.vault")

VAULT_DIR = Path("output/reportes")
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_PILLAR_RE = re.compile(r"^\s+P(\d):\s*(.+)$")


def _parse_frontmatter(text: str) -> dict:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result = {}
    current_block = None
    for line in match.group(1).splitlines():
        if line.startswith("pilares:"):
            current_block = "pilares"
            result["pilares"] = {}
            continue
        if current_block == "pilares":
            pm = _PILLAR_RE.match(line)
            if pm:
                result["pilares"][f"P{pm.group(1)}"] = pm.group(2).strip()
                continue
            else:
                current_block = None
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


def get_vault_context(ticker: str, max_entries: int = 3) -> dict:
    """
    Recupera los últimos `max_entries` análisis del vault para el ticker.
    Retorna un dict con:
      - count: número de análisis previos encontrados
      - summary: texto listo para inyectar en el prompt del Boss
      - entries: lista de dicts con los datos de cada análisis
      - last_score / last_decision: del análisis más reciente
    """
    ticker_dir = VAULT_DIR / ticker.upper()
    if not ticker_dir.exists():
        return {"count": 0, "summary": "", "entries": []}

    md_files = sorted(ticker_dir.glob("*_analisis.md"), reverse=True)[:max_entries]
    if not md_files:
        return {"count": 0, "summary": "", "entries": []}

    entries = []
    for filepath in md_files:
        try:
            text = filepath.read_text(encoding="utf-8")
            fm = _parse_frontmatter(text)
            if fm.get("fecha"):
                entries.append({
                    "fecha":        fm.get("fecha", "N/A"),
                    "score":        fm.get("score", "N/A"),
                    "clasificacion": fm.get("clasificacion", "N/A"),
                    "decision":     fm.get("decision", "N/A"),
                    "etapa":        fm.get("etapa", "N/A"),
                    "pilares":      fm.get("pilares", {}),
                })
        except Exception as exc:
            logger.warning("[Vault] Error leyendo %s: %s", filepath.name, exc)

    if not entries:
        return {"count": 0, "summary": "", "entries": []}

    lines = [f"=== HISTORIAL PREVIO EN VAULT - {ticker} ({len(entries)} analisis) ==="]
    for e in entries:
        pilares_str = " | ".join(
            f"{k}:{v}" for k, v in sorted(e["pilares"].items())
        ) if e["pilares"] else "pilares N/A"
        lines.append(
            f"  * {e['fecha']}  Score:{e['score']}/100  {e['clasificacion']}"
            f"  {e['decision']}  Etapa:{e['etapa']}"
        )
        if e["pilares"]:
            lines.append(f"    Pilares: {pilares_str}")

    # Tendencia de score entre los dos más recientes
    if len(entries) >= 2:
        try:
            delta = float(entries[0]["score"]) - float(entries[1]["score"])
            arrow = "+" if delta > 0 else ("-" if delta < 0 else "=")
            lines.append(
                f"  Tendencia: {arrow} {abs(delta):.0f} pts vs analisis anterior"
            )
        except (ValueError, TypeError):
            pass

    lines.append(
        "INSTRUCCION: usa este historial para detectar cambios de conviction, "
        "comparar evolucion de pilares y destacar si la tesis se ha fortalecido o debilitado."
    )

    return {
        "count":         len(entries),
        "summary":       "\n".join(lines),
        "entries":       entries,
        "last_score":    entries[0].get("score"),
        "last_decision": entries[0].get("decision"),
    }
