import asyncio, logging, os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import uvicorn
from processor.engine import VideoProcessingEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
active_jobs: Dict[str, asyncio.Task] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    for task in active_jobs.values():
        task.cancel()

app = FastAPI(title="Video Processor", lifespan=lifespan)

class ProcessRequest(BaseModel):
    game_id: str
    source_type: str
    source: str

@app.post("/process")
async def start_processing(request: ProcessRequest):
    if request.game_id in active_jobs:
        return {"message": "Already processing"}
    engine = VideoProcessingEngine(request.game_id, request.source_type, request.source)
    task = asyncio.create_task(engine.run())
    active_jobs[request.game_id] = task
    task.add_done_callback(lambda t: active_jobs.pop(request.game_id, None))
    return {"message": "Processing started", "game_id": request.game_id}

@app.post("/stop")
async def stop_processing(game_id: str):
    if game_id in active_jobs:
        active_jobs[game_id].cancel()
        return {"message": "Stopped"}
    return {"message": "No active job"}

@app.get("/health")
async def health():
    return {"status": "ok", "active_jobs": list(active_jobs.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
