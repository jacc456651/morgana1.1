#!/usr/bin/env python3
"""
MORGANA — Sistema de Inversion Growth Institucional
Uso:
  py morgana.py analiza TICKER    — Análisis completo
  py morgana.py chequea TICKER    — Ver historial + re-análisis rápido
"""
import sys
import io
import logging
from pathlib import Path

# Fix encoding en consola Windows (cp1252 no soporta todos los caracteres Unicode)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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
