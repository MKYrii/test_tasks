from fastapi import FastAPI
from app.api import router as api_router
from app.database import create_database_tables
from app.task_manager import task_manager
import uvicorn

app = FastAPI(title="Task queue service", version="1.0.0")

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    await create_database_tables()
    await task_manager.start()

@app.on_event("shutdown")
async def shutdown_event():
    await task_manager.stop()

@app.get("/")
async def root():
    return {"message": "Task queue service is running!"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)