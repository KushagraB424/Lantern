import os
import json
from agents.state import GraphState
from agents.llm_provider import get_llm
from agents.sandbox import execute_python
from langchain_core.prompts import ChatPromptTemplate
import re

def extract_python_code(text: str) -> str:
    pattern = r"```(?:python|py)?\s*(.*?)\s*```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1]
        
    # Fallback: if no backticks, try to strip conversational text before the first import
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            return '\n'.join(lines[i:])
            
    return text

def analysis_execution_node(state: GraphState) -> GraphState:
    """
    Writes and executes Pandas code to fulfill the analysis plan.
    """
    settings = state.get("settings", {})
    plan = state.get("analysis_plan", "")
    dataset_id = state.get("dataset_id")
    
    llm = get_llm(
        provider=settings.get("provider", "google"),
        model_name=settings.get("model_name", "gemini-2.5-flash"),
        temperature=0.1,
        max_tokens=settings.get("max_tokens", 2000)
    )
    
    dataset_path = None
    for ext in ['.csv', '.xlsx', '.xls']:
        potential_path = os.path.join("data", f"{dataset_id}{ext}")
        if os.path.exists(potential_path):
            dataset_path = os.path.abspath(potential_path)
            break
            
    if not dataset_path:
        state["execution_logs"] = "Dataset file not found."
        return state
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Python Data Scientist.
Your task is to write Python code using `pandas` to execute the provided Analysis Plan.

CRITICAL REQUIREMENTS:
1. The dataset path is ALREADY provided as the global variable `DATASET_PATH`. You MUST use it exactly like this: `df = pd.read_csv(DATASET_PATH, encoding_errors='replace')`. Do NOT use placeholders like 'data.csv'.
2. Your code MUST output its final results as a single structured JSON object printed to stdout using `print(json.dumps(...))`. Do not print anything else.
3. The JSON must have the following schema:
{{
  "tables": {{ "table_name": [ {{ "col1": "val1" }} ] }},
  "aggregations": {{ "metric_name": "value" }}
}}
4. Write ONLY the python code in a ```python ... ``` block. BE EXTREMELY CONCISE. Do not include markdown headers, explanations, or long comments, as you have a strict token limit and your code will get truncated. Do NOT use print() for debugging.
5. IMPORTANT: Use modern Pandas methods. `df.append` is removed in Pandas 2.0, use `pd.concat` instead.
"""),
        ("human", "Analysis Plan:\n{plan}\n\nPlease generate the Python code. Keep it brief to save tokens.")
    ])
    
    max_retries = 3
    attempt = 0
    code = ""
    sandbox_result = None
    error_message = ""
    
    chain = prompt | llm
    
    while attempt < max_retries:
        try:
            if attempt == 0:
                response = chain.invoke({"plan": plan})
            else:
                correction_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an expert Python Data Scientist."),
                    ("human", "The following python code failed to execute:\n```python\n{code}\n```\n\nError:\n{error_message}\n\nPlease fix the code and return only the corrected python code block.")
                ])
                correction_chain = correction_prompt | llm
                response = correction_chain.invoke({
                    "code": code,
                    "error_message": error_message
                })
                
            code = extract_python_code(response.content)
        except Exception as e:
            error_message = f"LLM Error: {str(e)}"
            attempt += 1
            continue
        sandbox_result = execute_python(code, dataset_path=dataset_path)
        
        if sandbox_result["status"] == "success":
            break
            
        error_message = sandbox_result["stderr"]
        attempt += 1
        
    state["generated_code"] = code
    state["execution_logs"] = sandbox_result["stderr"] if sandbox_result["status"] == "error" else sandbox_result["stdout"]
    
    try:
        stdout = sandbox_result["stdout"]
        json_start = stdout.find('{')
        json_end = stdout.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            artifact_str = stdout[json_start:json_end]
            state["analysis_artifact"] = json.loads(artifact_str)
        else:
            state["analysis_artifact"] = {"error": "Could not parse JSON artifact"}
    except Exception as e:
        state["analysis_artifact"] = {"error": str(e)}
        
    return state
