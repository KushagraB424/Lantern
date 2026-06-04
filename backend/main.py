from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, analysis, search, observability

app = FastAPI(
    title="Lantern API",
    description="API for the Lantern AI Data Analyst SaaS",
    version="0.1.0"
)

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(observability.router, prefix="/api/observability", tags=["Observability"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Lantern API"}
