"""
Hook PostToolUse — guarda outputs PE en output/pe/[TIPO]/[FECHA]_[nombre].md

Detecta: IC memos, DD checklists, DD prep, returns analysis, unit economics,
         deal screening, portfolio monitoring, value creation plans.

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

PE_KEYWORDS = {
    "ic memo", "investment committee", "due diligence", "dd checklist",
    "returns analysis", "irr", "moic", "unit economics", "ltv/cac",
    "deal screening", "value creation", "portfolio monitoring",
    "lbo", "ebitda bridge", "100-day plan",
}

TYPE_MAP = [
    ({"ic memo", "investment committee"}, "ic-memos"),
    ({"due diligence", "dd checklist", "dd prep"}, "dd-reports"),
    ({"returns analysis", "irr", "moic", "lbo"}, "returns"),
    ({"unit economics", "ltv/cac", "arr cohort"}, "unit-economics"),
    ({"deal screening", "deal screen"}, "screening"),
    ({"value creation", "ebitda bridge", "100-day plan"}, "value-creation"),
    ({"portfolio monitoring", "portfolio review"}, "portfolio"),
]


def _is_pe_content(path: str, content: str) -> bool:
    """True si el archivo parece un output PE."""
    path_lower = path.lower()
    content_preview = content[:800].lower()
    combined = path_lower + " " + content_preview
    return any(kw in combined for kw in PE_KEYWORDS)


def _detect_type(path: str, content: str) -> str:
    """Detecta el tipo de output PE para elegir subcarpeta."""
    combined = (path + " " + content[:800]).lower()
    for keywords, folder in TYPE_MAP:
        if any(kw in combined for kw in keywords):
            return folder
    return "general"


def _extract_name(path: str, content: str) -> str:
    """
    Extrae nombre del reporte desde la ruta o primer H1 del contenido.
    Devuelve un slug kebab-case seguro para nombre de archivo.
    """
    # 1. Desde la ruta: último segmento sin extensión
    basename = os.path.splitext(os.path.basename(path))[0]
    if basename and basename not in ("untitled", "output", "report"):
        return re.sub(r"[^a-zA-Z0-9_-]", "-", basename)[:60]

    # 2. Primer H1 del contenido
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        slug = re.sub(r"[^a-zA-Z0-9 ]", "", m.group(1)).strip().lower()
        return re.sub(r"\s+", "-", slug)[:60]

    return "report"


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

    if not _is_pe_content(file_path, content):
        sys.exit(0)

    # No re-guardar si ya está en output/pe/
    if os.path.normpath("output/pe") in os.path.normpath(file_path):
        sys.exit(0)

    output_type = _detect_type(file_path, content)
    name = _extract_name(file_path, content)
    today = date.today().strftime("%Y-%m-%d")

    dest_dir = os.path.join("output", "pe", output_type)
    dest_path = os.path.join(dest_dir, f"{today}_{name}.md")

    os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[hook:save_pe_output] Guardado: {dest_path}")


if __name__ == "__main__":
    main()
