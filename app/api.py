from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Task, TaskStatus
from app.task_manager import task_manager
from app.schemas import TaskCreateResponse, TaskStatusResponse, ErrorResponse

router = APIRouter()


@router.post(
    "/tasks",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Task created successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_task(db: AsyncSession = Depends(get_db)):
    """
    Создает новую задачу и добавляет ее в очередь на выполнение

    Returns:
        TaskCreateResponse: ID созданной задачи
    """
    try:
        task = Task(status=TaskStatus.IN_QUEUE.value, create_time=datetime.utcnow())
        db.add(task)
        await db.commit()
        await db.refresh(task)

        print(f"Создана задача ID: {task.id}, статус: {task.status}")

        # добавляем задачу в очередь на выполнение
        await task_manager.add_task(task.id)

        return TaskCreateResponse(task_id=task.id)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    responses={
        200: {"description": "Task status retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_task_status(task_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает статус задачи по её ID

    Args:
        task_id (int): ID задачи

    Returns:
        TaskStatusResponse: Статус и временные метки задачи
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )

        response_data = task.to_response()
        print(f"Запрос статуса задачи {task_id}: {response_data['status']}")
        return TaskStatusResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )
