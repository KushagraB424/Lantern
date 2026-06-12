import os
import pandas as pd
from agents.state import GraphState
from agents.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate

def data_quality_node(state: GraphState) -> GraphState:
    """
    Evaluates data quality (missing values, duplicates, etc.) and assigns a score.
    """
    settings = state.get("settings", {})
    dataset_id = state.get("dataset_id")
    
    # Get the user-selected LLM
    llm = get_llm(
        provider=settings.get("provider", "google"),
        model_name=settings.get("model_name", "gemini-2.5-flash"),
        temperature=settings.get("temperature", 0.2),
        max_tokens=settings.get("max_tokens", 1000)
    )
    
    # Read dataset
    dataset_path = None
    for ext in ['.csv', '.xlsx', '.xls']:
        potential_path = os.path.join("data", f"{dataset_id}{ext}")
        if os.path.exists(potential_path):
            dataset_path = potential_path
            break
            
    quality_issues = []
    quality_score = 100
    
    if dataset_path:
        try:
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            else:
                df = pd.read_excel(dataset_path)
                
            # Perform basic programmatic quality checks
            missing_count = int(df.isnull().sum().sum())
            duplicate_count = int(df.duplicated().sum())
            
            if missing_count > 0:
                quality_issues.append(f"- Found {missing_count} missing values across the dataset.")
                quality_score -= min(missing_count, 30)  # Deduct up to 30 points
                
            if duplicate_count > 0:
                quality_issues.append(f"- Found {duplicate_count} duplicate rows.")
                quality_score -= min(duplicate_count * 2, 20)
                
            quality_score = max(0, quality_score)
            
        except Exception as e:
            quality_issues.append(f"- Error processing dataset for quality checks: {e}")
            quality_score = 0
            
    # Use LLM to format the issues nicely
    issues_text = "\n".join(quality_issues) if quality_issues else "No major issues found."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Data Quality Analyst."),
        ("human", """
I have evaluated a dataset. The programmatic quality score is {quality_score}/100.
Here are the issues found:
{issues_text}

Please generate a short, professional Data Quality Review report in markdown.
Include the score prominently and summarize the issues in max 2 bullet points.
Be extremely concise.
        """)
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "quality_score": quality_score,
        "issues_text": issues_text
    })
    
    state["quality_score"] = int(quality_score)
    state["quality_issues"] = response.content
    return state
