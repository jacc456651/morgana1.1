"""
Hook PostToolUse — guarda outputs de modelos en output/models/[TIPO]/[FECHA]_[nombre].md

Detecta: DCF, LBO, comps, 3-statement model, competitive analysis, audit results.

Recibe por stdin el JSON de Claude Code con:
  {
    "tool_name": "Write",
    "tool_input": { "file_path": "...", "content": "..." },
    ...
  }
"""
import json
import os
import re
import sys
from datetime import date

MODEL_KEYWORDS = {
    "dcf", "discounted cash flow", "wacc", "terminal value",
    "lbo", "leveraged buyout", "irr", "moic", "debt schedule",
    "comparable company", "comps", "ev/ebitda", "ev/revenue",
    "3-statement", "three statement", "income statement", "balance sheet",
    "competitive analysis", "competitive landscape", "moat assessment",
    "audit", "formula error", "circular reference",
}

TYPE_MAP = [
    ({"dcf", "discounted cash flow", "wacc", "terminal value"}, "dcf"),
    ({"lbo", "leveraged buyout", "debt schedule"}, "lbo"),
    ({"comparable company", "comps", "ev/ebitda", "ev/revenue"}, "comps"),
    ({"3-statement", "three statement", "income statement", "balance sheet"}, "3-statement"),
    ({"competitive analysis", "competitive landscape", "moat assessment"}, "competitive-analysis"),
    ({"audit", "formula error", "circular reference"}, "audits"),
]


def _is_model_content(path: str, content: str) -> bool:
    """True si el archivo parece un output de modelo financiero."""
    combined = (path + " " + content[:800]).lower()
    return any(kw in combined for kw in MODEL_KEYWORDS)


def _detect_type(path: str, content: str) -> str:
    """Detecta el tipo de modelo para elegir subcarpeta."""
    combined = (path + " " + content[:800]).lower()
    for keywords, folder in TYPE_MAP:
        if any(kw in combined for kw in keywords):
            return folder
    return "general"


def _extract_ticker_or_name(path: str, content: str) -> str:
    """
    Intenta extraer ticker o nombre de empresa del path o contenido.
    Devuelve slug kebab-case seguro.
    """
    # 1. Ticker desde ruta tipo output/models/.../AAPL_...
    m = re.search(r"[/\\]([A-Z]{1,5})[_\-\s/\\]", path)
    if m:
        return m.group(1).upper()

    # 2. Patrón 'Ticker: AAPL' en el contenido
    m = re.search(r"\*{0,2}[Tt]icker\*{0,2}\s*[:\-]\s*([A-Z]{1,5})\b", content)
    if m:
        return m.group(1)

    # 3. Primer H1 del contenido
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        slug = re.sub(r"[^a-zA-Z0-9 ]", "", m.group(1)).strip().lower()
        return re.sub(r"\s+", "-", slug)[:60]

    # 4. Nombre de archivo sin extensión
    basename = os.path.splitext(os.path.basename(path))[0]
    if basename:
        return re.sub(r"[^a-zA-Z0-9_-]", "-", basename)[:60]

    return "model"


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if payload.get("tool_name") != "Write":
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    if not _is_model_content(file_path, content):
        sys.exit(0)

    # No re-guardar si ya está en output/models/
    if os.path.normpath("output/models") in os.path.normpath(file_path):
        sys.exit(0)

    output_type = _detect_type(file_path, content)
    name = _extract_ticker_or_name(file_path, content)
    today = date.today().strftime("%Y-%m-%d")

    dest_dir = os.path.join("output", "models", output_type)
    dest_path = os.path.join(dest_dir, f"{today}_{name}.md")

    os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[hook:save_model_output] Guardado: {dest_path}")


if __name__ == "__main__":
    main()
