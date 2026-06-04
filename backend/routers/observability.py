from fastapi import APIRouter, HTTPException
from agents.graph import analysis_graph

router = APIRouter()

@router.get("/graph")
async def get_graph_structure():
    """
    Returns the static node and edge structure of the LangGraph.
    """
    return {
        "status": "success",
        "nodes": [
            {"id": "dataset_understanding", "label": "Dataset Understanding"},
            {"id": "data_quality", "label": "Data Quality Review"},
            {"id": "analysis_planning", "label": "Analysis Planning"},
            {"id": "analysis_execution", "label": "Code Execution"},
            {"id": "visualization", "label": "Visualization Generation"},
            {"id": "insight_generation", "label": "Insight Generation"},
            {"id": "recommendation_generation", "label": "Recommendation Generation"},
            {"id": "report_generation", "label": "Report Generation"}
        ],
        "edges": [
            {"source": "START", "target": "dataset_understanding"},
            {"source": "dataset_understanding", "target": "data_quality"},
            {"source": "data_quality", "target": "analysis_planning"},
            {"source": "analysis_planning", "target": "analysis_execution"},
            {"source": "analysis_execution", "target": "visualization"},
            {"source": "visualization", "target": "insight_generation"},
            {"source": "insight_generation", "target": "recommendation_generation"},
            {"source": "recommendation_generation", "target": "report_generation"},
            {"source": "report_generation", "target": "END"}
        ]
    }

@router.get("/{thread_id}/trace")
async def get_thread_trace(thread_id: str):
    """
    Retrieves the historical trace of a thread from the checkpointer.
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        
        history = list(analysis_graph.get_state_history(config))
        history.reverse() 
        
        trace = []
        for i, snapshot in enumerate(history):
            trace.append({
                "step": i,
                "node": snapshot.next[0] if snapshot.next else "END",
                "timestamp": snapshot.created_at.isoformat() if hasattr(snapshot, "created_at") else None,
                "state_keys_updated": list(snapshot.values.keys()) 
            })
            
        return {
            "status": "success",
            "thread_id": thread_id,
            "trace": trace
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
