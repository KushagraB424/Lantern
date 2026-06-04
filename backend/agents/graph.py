from langgraph.graph import StateGraph, START, END
from agents.state import GraphState
from agents.dataset_understanding import dataset_understanding_node
from agents.data_quality import data_quality_node
from agents.analysis_planning import analysis_planning_node
from agents.execution import analysis_execution_node
from agents.visualization import visualization_node
from agents.insights import insight_generation_node
from agents.recommendations import recommendation_generation_node
from agents.reporting import report_generation_node
from agents.checkpoint import get_checkpointer

def build_graph():
    """
    Constructs the LangGraph StateGraph.
    """
    workflow = StateGraph(GraphState)
    
    # Add Nodes
    workflow.add_node("dataset_understanding", dataset_understanding_node)
    workflow.add_node("data_quality", data_quality_node)
    workflow.add_node("analysis_planning", analysis_planning_node)
    workflow.add_node("analysis_execution", analysis_execution_node)
    workflow.add_node("visualization", visualization_node)
    workflow.add_node("insight_generation", insight_generation_node)
    workflow.add_node("recommendation_generation", recommendation_generation_node)
    workflow.add_node("report_generation", report_generation_node)
    
    # Define Edges
    workflow.add_edge(START, "dataset_understanding")
    workflow.add_edge("dataset_understanding", "data_quality")
    workflow.add_edge("data_quality", "analysis_planning")
    workflow.add_edge("analysis_planning", "analysis_execution")
    workflow.add_edge("analysis_execution", "visualization")
    workflow.add_edge("visualization", "insight_generation")
    workflow.add_edge("insight_generation", "recommendation_generation")
    workflow.add_edge("recommendation_generation", "report_generation")
    workflow.add_edge("report_generation", END)
    
    # Compile
    checkpointer = get_checkpointer()
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["analysis_execution"]
    )

# Instantiate a global graph object
analysis_graph = build_graph()
