import json
from agents.state import GraphState
from agents.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate

def insight_generation_node(state: GraphState) -> GraphState:
    settings = state.get("settings", {})
    artifact = state.get("analysis_artifact", {})
    
    if "error" in artifact or not artifact:
        state["insights"] = "Could not generate insights due to execution errors."
        return state
        
    llm = get_llm(
        provider=settings.get("provider", "google"),
        model_name=settings.get("model_name", "gemini-2.5-flash"),
        temperature=0.3,
        max_tokens=settings.get("max_tokens", 2000)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Data Analyst.
I have a structured JSON artifact containing tables and aggregations from a recent dataset execution.
Your task is to write a brief 'Key Insights' section in Markdown.
Explain findings, trends, anomalies, and relationships in the data. Do NOT provide business recommendations yet.
Keep it extremely concise (max 3-5 bullet points total).
"""),
        ("human", "Here is the JSON artifact:\n{artifact}\n\nPlease generate the Insights.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"artifact": json.dumps(artifact, indent=2)})
    
    state["insights"] = response.content
    return state
