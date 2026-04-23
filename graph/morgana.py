from langgraph.graph import StateGraph, END
from agents.state import MorganaState
from agents.scout import scout_node
from agents.boss import boss_node


def build_graph():
    """Construye y compila el grafo LangGraph de Morgana (Semana 1)."""
    graph = StateGraph(MorganaState)

    graph.add_node("scout", scout_node)
    graph.add_node("boss", boss_node)

    graph.set_entry_point("scout")
    graph.add_edge("scout", "boss")
    graph.add_edge("boss", END)

    return graph.compile()
