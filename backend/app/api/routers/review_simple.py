import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from pathlib import Path
from app.services.task_service_memory import TaskService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store tasks in memory
task_service = TaskService()

@router.post("/review")
async def upload_and_review(file: UploadFile = File(...)):
    """
    Upload a file and start the review process
    """
    try:
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        logger.info(f"Starting review task with ID: {task_id}")
        
        # Save uploaded file
        file_path = Path(f"uploads/{task_id}_{file.filename}")
        logger.info(f"Attempting to save file to: {file_path}")
        
        # Ensure uploads directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Uploads directory created/verified")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        logger.info(f"File saved successfully to: {file_path}")
            
        # Start review task
        await task_service.start_review_task(task_id, str(file_path))
        logger.info(f"Review task started for task ID: {task_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "task_id": task_id,
                "message": "File uploaded successfully. Review started."
            }
        )
    except PermissionError as e:
        logger.error(f"Permission error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Permission denied: {str(e)}")
    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Directory not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/review/{task_id}")
async def get_review_result(task_id: str):
    """
    Get the result of a review task
    """
    try:
        logger.info(f"Getting review result for task ID: {task_id}")
        result = await task_service.get_task_result(task_id)
        if result is None:
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Returning result for task {task_id}: {result['status']}")
        return JSONResponse(status_code=200, content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting review result for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))