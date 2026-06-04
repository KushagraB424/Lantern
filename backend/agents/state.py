from typing import TypedDict, Any, Dict, List

class GraphState(TypedDict, total=False):
    """
    Represents the state of our LangGraph workflow.
    """
    dataset_id: str
    settings: Dict[str, Any]  # model_name, provider, temperature, max_tokens
    
    # Upload metadata
    metadata: Dict[str, Any]
    
    # Outputs from Dataset Understanding Agent
    understanding_summary: str
    
    # Outputs from Data Quality Agent
    quality_score: int
    quality_issues: str
    
    # Outputs from Analysis Planning Agent
    analysis_plan: str
    plan_approved: bool
    
    # Outputs from Execution Agent
    generated_code: str
    execution_logs: str
    analysis_artifact: Dict[str, Any]
    
    # Phase 7: Insights & Reporting
    insights: str
    recommendations: str
    
    # Generated Visualizations & Reports
    visualizations: List[Any]
    final_report: str
