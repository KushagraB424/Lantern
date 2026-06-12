from agents.state import GraphState
from agents.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate

def recommendation_generation_node(state: GraphState) -> GraphState:
    settings = state.get("settings", {})
    insights = state.get("insights", "")
    
    llm = get_llm(
        provider=settings.get("provider", "google"),
        model_name=settings.get("model_name", "gemini-2.5-flash"),
        temperature=0.4,
        max_tokens=settings.get("max_tokens", 2000)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a top-tier Business Consultant.
I will provide you with 'Key Insights' generated from a dataset.
Your task is to write a 'Recommendations' section in Markdown.
Suggest business actions, highlight risks, highlight opportunities, and suggest next analyses.
Be extremely concise (max 3-5 bullet points total).
"""),
        ("human", "Here are the Insights:\n{insights}\n\nPlease generate the Recommendations.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"insights": insights})
    
    state["recommendations"] = response.content
    return state
