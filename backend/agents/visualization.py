import json
from agents.state import GraphState
from agents.llm_provider import get_llm
from langchain_core.prompts import ChatPromptTemplate
from agents.execution import extract_python_code
from agents.sandbox import execute_python

def visualization_node(state: GraphState) -> GraphState:
    """
    Generates Plotly visualizations based on the structured analysis artifact.
    """
    settings = state.get("settings", {})
    artifact = state.get("analysis_artifact", {})
    
    if "error" in artifact or not artifact:
        state["visualizations"] = []
        return state
        
    llm = get_llm(
        provider=settings.get("provider", "google"),
        model_name=settings.get("model_name", "gemini-2.5-flash"),
        temperature=0.1,
        max_tokens=settings.get("max_tokens", 2000)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Data Visualization Specialist.
I have a structured JSON artifact containing tables and aggregations.
Your task is to write Python code using `plotly.express` or `plotly.graph_objects` to generate useful interactive charts based on this data.

CRITICAL REQUIREMENTS:
1. The JSON data is provided as a variable `ARTIFACT_JSON_STR`. You must `json.loads` it and create pandas DataFrames.
2. For each chart you create, serialize it to JSON using `fig.to_json()`.
3. Put all serialized charts into a list.
4. Your script MUST output ONLY the final list of serialized chart JSON strings by printing a JSON array to stdout: `print(json.dumps(chart_json_list))`
5. Write ONLY the python code in a ```python ... ``` block. BE EXTREMELY CONCISE. Do not include markdown headers, explanations, or long comments, as you have a strict token limit and your code will get truncated.
6. IMPORTANT: Use modern Pandas methods. `df.append` is removed in Pandas 2.0, use `pd.concat` instead.
"""),
        ("human", "Here is the structure of the JSON artifact:\n{artifact_summary}\n\nPlease generate the Python code. Keep it brief to save tokens.")
    ])
    
    artifact_summary = {}
    if "tables" in artifact:
        artifact_summary["tables"] = {k: v[:2] for k, v in artifact["tables"].items() if isinstance(v, list)}
    if "aggregations" in artifact:
        artifact_summary["aggregations"] = artifact["aggregations"]
        
    max_retries = 3
    attempt = 0
    code = ""
    sandbox_result = None
    error_message = ""
    
    chain = prompt | llm
    
    while attempt < max_retries:
        try:
            if attempt == 0:
                response = chain.invoke({"artifact_summary": json.dumps(artifact_summary, indent=2)})
            else:
                correction_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an expert Data Visualization Specialist."),
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
        actual_json_str = json.dumps(artifact).replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        executable_code = f"import json\nimport pandas as pd\nimport plotly.express as px\nimport plotly.graph_objects as go\nARTIFACT_JSON_STR = '{actual_json_str}'\n" + code
        
        sandbox_result = execute_python(executable_code, dataset_path="")
        
        if sandbox_result["status"] == "success":
            break
            
        error_message = sandbox_result["stderr"]
        attempt += 1

    if sandbox_result["status"] == "success":
        try:
            stdout = sandbox_result["stdout"]
            json_start = stdout.find('[')
            json_end = stdout.rfind(']') + 1
            if json_start != -1 and json_end != 0:
                charts_json = json.loads(stdout[json_start:json_end])
                state["visualizations"] = [json.loads(c) for c in charts_json if isinstance(c, str)]
            else:
                state["visualizations"] = []
        except Exception as e:
            print("Failed to parse visual output:", e)
            state["visualizations"] = []
    else:
        print("Visualization code failed:", sandbox_result["stderr"])
        state["visualizations"] = []
        
    return state
