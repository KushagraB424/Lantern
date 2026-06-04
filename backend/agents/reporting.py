from agents.state import GraphState
from agents.memory import save_report_to_memory

def report_generation_node(state: GraphState) -> GraphState:
    """
    Compiles all parts into a final Markdown report.
    """
    understanding = state.get("understanding_summary", "No summary available.")
    quality_score = state.get("quality_score", 0)
    quality_issues = state.get("quality_issues", "No quality issues found.")
    plan = state.get("analysis_plan", "No plan available.")
    insights = state.get("insights", "No insights available.")
    recommendations = state.get("recommendations", "No recommendations available.")
    
    report = f"""# Executive Data Analysis Report

## 1. Executive Summary
This report provides an in-depth analysis of the provided dataset, evaluating data quality, uncovering key insights, and recommending strategic business actions.

## 2. Dataset Overview
{understanding}

## 3. Data Quality Findings
**Quality Score: {quality_score}/100**

{quality_issues}

## 4. Analysis Plan
{plan}

## 5. Key Insights
{insights}

## 6. Recommendations
{recommendations}

## 7. Visualizations
*(Interactive visualizations are available in the dashboard)*

## 8. Conclusion
The data presents clear opportunities for optimization. By following the recommended actions, stakeholders can leverage these insights for measurable impact.
"""
    
    state["final_report"] = report
    
    try:
        dataset_id = state.get("dataset_id", "unknown")
        summary_intro = understanding.split('\n')[0] if understanding else "Analysis report"
        save_report_to_memory(
            dataset_id=dataset_id,
            report_text=report,
            summary=summary_intro,
            quality_score=quality_score
        )
    except Exception as e:
        print(f"Failed to save memory: {e}")
        
    return state
