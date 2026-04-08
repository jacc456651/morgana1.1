"""
Hook PostToolUse — guarda análisis de earnings en output/reportes/[TICKER]/[FECHA]_earnings.md

Recibe por stdin el JSON de Claude Code con:
  {
    "tool_name": "Write",
    "tool_input": { "file_path": "...", "content": "..." },
    ...
  }

Solo actúa si el archivo escrito parece un análisis de earnings.
"""
import json
import os
import re
import sys
from datetime import date

EARNINGS_KEYWORDS = {"earnings", "quarterly", "q1", "q2", "q3", "q4", "10-q", "beat", "miss"}


def _is_earnings_content(path: str, content: str) -> bool:
    """True si el archivo parece un reporte de earnings."""
    path_lower = path.lower()
    content_preview = content[:500].lower()
    if "earnings" in path_lower:
        return True
    return bool(EARNINGS_KEYWORDS.intersection(content_preview.split()))


def _extract_ticker(path: str, content: str) -> str | None:
    """
    Intenta extraer el ticker de la ruta o del contenido markdown.
    Busca en orden:
      1. Segmento de ruta tipo output/reportes/AAPL/...
      2. Patrón 'Ticker: AAPL' o '**Ticker**: AAPL' en el contenido
      3. Primera palabra en mayúsculas del primer encabezado H1
    """
    # 1. Desde la ruta
    m = re.search(r"output[/\\]reportes[/\\]([A-Z]{1,5})[/\\]", path)
    if m:
        return m.group(1)

    # 2. Patrón explícito en el contenido
    m = re.search(r"\*{0,2}[Tt]icker\*{0,2}\s*[:\-]\s*([A-Z]{1,5})\b", content)
    if m:
        return m.group(1)

    # 3. Primer token en mayúsculas del título H1
    m = re.search(r"^#\s+([A-Z]{1,5})\b", content, re.MULTILINE)
    if m:
        return m.group(1)

    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # stdin vacío o no JSON — salir silenciosamente

    if payload.get("tool_name") != "Write":
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    if not _is_earnings_content(file_path, content):
        sys.exit(0)

    ticker = _extract_ticker(file_path, content)
    if not ticker:
        print("[hook:save_earnings] No se pudo extraer el ticker — archivo no guardado.", file=sys.stderr)
        sys.exit(0)

    today = date.today().strftime("%Y-%m-%d")
    dest_dir = os.path.join("output", "reportes", ticker)
    dest_path = os.path.join(dest_dir, f"{today}_earnings.md")

    # No sobreescribir si ya es el destino correcto
    if os.path.abspath(file_path) == os.path.abspath(dest_path):
        sys.exit(0)

    os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[hook:save_earnings] Guardado: {dest_path}")


if __name__ == "__main__":
    main()
