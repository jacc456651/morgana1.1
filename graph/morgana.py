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
