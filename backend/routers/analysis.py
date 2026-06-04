import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
from agents.graph import analysis_graph
from agents.state import GraphState
from langchain_core.runnables import RunnableConfig

router = APIRouter()

class AnalysisRequest(BaseModel):
    dataset_id: str
    settings: Dict[str, Any]

class ResumeRequest(BaseModel):
    action: str  # "approve" or "edit"
    updated_plan: Optional[str] = None

@router.post("/start")
async def start_analysis(request: AnalysisRequest):
    try:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state = {
            "dataset_id": request.dataset_id,
            "settings": request.settings,
            "metadata": {} 
        }
        
        # Run graph until interrupt
        for event in analysis_graph.stream(initial_state, config=config):
            pass 
            
        # Get the interrupted state
        state_dict = analysis_graph.get_state(config)
        current_state = state_dict.values
        
        return {
            "status": "waiting_for_approval",
            "thread_id": thread_id,
            "plan": current_state.get("analysis_plan", ""),
            "understanding": current_state.get("understanding_summary", ""),
            "quality_score": current_state.get("quality_score", 100)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/resume")
async def resume_analysis(thread_id: str, request: ResumeRequest):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state_snapshot = analysis_graph.get_state(config)
        
        if not state_snapshot.next:
            return {"status": "completed_or_not_found"}
            
        current_state = state_snapshot.values
        
        if request.action == "approve":
            # Update the state in the graph, pretending it came from the planning node
            # so the graph knows to continue to analysis_execution
            analysis_graph.update_state(
                config, 
                {"plan_approved": True, "analysis_plan": request.updated_plan or current_state.get("analysis_plan")},
                as_node="analysis_planning"
            )
            
            # Resume graph execution
            for event in analysis_graph.stream(None, config=config):
                pass
                
            final_state = analysis_graph.get_state(config).values
            return {
                "status": "success",
                "message": "Analysis execution completed",
                "plan": final_state.get("analysis_plan"),
                "generated_code": final_state.get("generated_code"),
                "execution_logs": final_state.get("execution_logs"),
                "analysis_artifact": final_state.get("analysis_artifact"),
                "visualizations": final_state.get("visualizations"),
                "final_report": final_state.get("final_report")
            }
            
        return {"status": "error", "message": "Invalid action"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{thread_id}/status")
async def get_analysis_status(thread_id: str):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state_snapshot = analysis_graph.get_state(config)
        
        if not state_snapshot:
            raise HTTPException(status_code=404, detail="Thread not found")
            
        current_state = state_snapshot.values
        
        return {
            "status": "success",
            "is_completed": not state_snapshot.next,
            "result": {
                "final_report": current_state.get("final_report"),
                "visualizations": current_state.get("visualizations"),
                "generated_code": current_state.get("generated_code"),
                "execution_logs": current_state.get("execution_logs")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

