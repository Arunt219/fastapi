from fastapi import FastAPI
from app.core.config import settings
from app.routers import products

app = FastAPI(title=settings.app_name)
app.include_router(products.router)

@app.get("/")
async def root():
    return "Welcome to the FastAPI application"
    #return {"status": "ok", "service": settings.app_name}

# Debug: shows which DB URL was loaded
@app.get("/_debug/dburl")
async def _debug_dburl():
    from app.core.config import settings as s
    return {"database_url": s.database_url}
