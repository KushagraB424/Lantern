from fastapi import APIRouter, Query
from agents.memory import semantic_search_reports

router = APIRouter()

@router.get("/")
async def search_reports(q: str = Query(..., min_length=1)):
    results = semantic_search_reports(q)
    return {"status": "success", "results": results}
