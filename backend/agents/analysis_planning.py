from agents.state import GraphState
from agents.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate

def analysis_planning_node(state: GraphState) -> GraphState:
    """
    Generates a structured plan for data analysis based on dataset understanding and quality.
    """
    settings = state.get("settings", {})
    understanding = state.get("understanding_summary", "")
    quality_score = state.get("quality_score", 100)
    quality_issues = state.get("quality_issues", "")
    
    # If a plan already exists and is approved, skip (this happens on resume)
    if state.get("plan_approved", False):
        return state
        
    llm = get_llm(
        provider=settings.get("provider", "google"),
        model_name=settings.get("model_name", "gemini-2.5-flash"),
        temperature=0.2, # Keep temperature low for structured planning
        max_tokens=settings.get("max_tokens", 1000)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI Analysis Planner. Based on the dataset summary and data quality, create a structured step-by-step analysis plan."),
        ("human", """
Dataset Summary:
{understanding}

Data Quality (Score: {quality_score}/100):
{quality_issues}

Please generate an Analysis Plan. Format it as a markdown list of clear steps.
The plan should adapt to any data quality issues (e.g. recommend dropping missing values if prevalent) and suggest meaningful aggregations/visualizations.
        """)
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "understanding": understanding,
        "quality_score": quality_score,
        "quality_issues": quality_issues
    })
    
    state["analysis_plan"] = response.content
    state["plan_approved"] = False # explicitly false until user approves
    return state
