#!/usr/bin/env python3
"""
MORGANA — Sistema de Inversion Growth Institucional
Uso: py morgana.py analiza TICKER
"""
import sys
import logging
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s %(name)s — %(message)s"
)

COMMANDS = {"analiza"}

HELP = """
MORGANA — Inversion Growth Institucional

Comandos disponibles:
  py morgana.py analiza TICKER    Analisis completo 5 pilares

Ejemplos:
  py morgana.py analiza AAPL
  py morgana.py analiza MNDY
"""


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in COMMANDS:
        print(HELP)
        sys.exit(0)

    command = sys.argv[1]
    ticker = sys.argv[2].upper()

    print(f"\nAnalizando {ticker}...\n")
    print("   [Scout] Recolectando datos de EDGAR, Yahoo Finance, Finviz, StockAnalysis...")

    from graph.morgana import build_graph
    from agents.state import initial_state

    graph = build_graph()
    state = initial_state(ticker, command)

    try:
        result = graph.invoke(state)
    except Exception as exc:
        print(f"\nError ejecutando analisis: {exc}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(result.get("reporte", "No se genero reporte."))
    print("=" * 60)

    if result.get("errors"):
        print(f"\nAdvertencias ({len(result['errors'])}):")
        for err in result["errors"]:
            print(f"   - {err}")

    print(f"\nDecision final: {result.get('decision', 'N/A')}")


if __name__ == "__main__":
    main()
