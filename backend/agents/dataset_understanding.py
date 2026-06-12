import os
import pandas as pd
from agents.state import GraphState
from agents.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate

def dataset_understanding_node(state: GraphState) -> GraphState:
    """
    Analyzes the dataset metadata and structure to provide a high-level summary.
    """
    settings = state.get("settings", {})
    metadata = state.get("metadata", {})
    
    # Get the user-selected LLM
    llm = get_llm(
        provider=settings.get("provider", "google"),
        model_name=settings.get("model_name", "gemini-2.5-flash"),
        temperature=settings.get("temperature", 0.2),
        max_tokens=settings.get("max_tokens", 1000)
    )
    
    # Sample the data to give the LLM more context
    dataset_id = state.get("dataset_id")
    dataset_path = None
    
    for ext in ['.csv', '.xlsx', '.xls']:
        potential_path = os.path.join("data", f"{dataset_id}{ext}")
        if os.path.exists(potential_path):
            dataset_path = potential_path
            break
            
    sample_data = ""
    if dataset_path:
        try:
            if dataset_path.endswith('.csv'):
                df_full = pd.read_csv(dataset_path)
            else:
                df_full = pd.read_excel(dataset_path)
                
            metadata['rows'] = df_full.shape[0]
            metadata['columns'] = df_full.shape[1]
            metadata['columns_list'] = df_full.columns.tolist()
            metadata['dtypes'] = {k: str(v) for k, v in df_full.dtypes.items()}
            
            sample_data = df_full.head(5).to_csv(index=False)
        except Exception as e:
            sample_data = f"Could not read sample data: {e}"
            
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Data Analyst. Your goal is to understand a new dataset and provide a high-level summary and potential analysis areas."),
        ("human", """
Here is the metadata for a dataset:
Rows: {rows}
Columns: {columns}
Fields: {fields}
Data Types: {dtypes}

Here is a sample of the first 5 rows:
{sample_data}

Please generate a Dataset Summary in markdown format. 
Include:
1. A brief overview of what this dataset appears to represent (max 2 sentences).
2. 3 Potential Analysis Areas (max 1 sentence each).
DO NOT be verbose. Be extremely brief.
        """)
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "rows": metadata.get('rows'),
        "columns": metadata.get('columns'),
        "fields": ', '.join(metadata.get('columns_list', [])),
        "dtypes": str(metadata.get('dtypes', {})),
        "sample_data": sample_data
    })
    
    # Update state
    state["understanding_summary"] = response.content
    return state
