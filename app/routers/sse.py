from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter(prefix="/sse", tags=["Real-time Events"])

@router.get("/task-status/{task_id}")
async def stream_task_status(task_id: str):
    """Streams live Server-Sent Events for background AI/OCR processing status."""
    async def event_generator():
        # Simulated stream for progress updates
        for progress in [20, 50, 80, 100]:
            await asyncio.sleep(0.5)
            data = {
                "task_id": task_id,
                "progress": progress,
                "status": "COMPLETED" if progress == 100 else "PROCESSING"
            }
            yield f"data: {json.dumps(data)}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
