from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.nodes import (
    classify_intent, 
    select_tool, 
    execute_tool, 
    compile_response
)

def build_agent_graph():
    """Build the intelligent agent workflow"""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("select_tool", select_tool)
    graph.add_node("execute_tool", execute_tool)
    graph.add_node("compile_response", compile_response)
    
    # Add edges
    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "select_tool")
    graph.add_edge("select_tool", "execute_tool")
    graph.add_edge("execute_tool", "compile_response")
    graph.add_edge("compile_response", END)
    
    return graph.compile()

# Singleton instance
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent_graph()
    return _agent