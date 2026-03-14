from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session
import uuid


from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.schemas import TaskCreate, TaskRead, EditTask, TaskComlite
from app.models import User, Task

router = APIRouter(
    tags=["Tasks"]
)


@router.post("/tasks", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not task.task.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be empty"
        )

    new_task = Task(
        user_id=current_user.id,
        task=task.task.strip(),
        comlite=False
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.put("/tasks/{task_id}/completed")
async def comlete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)

    task.comlite = not task.comlite

    db.commit()

    return {"completed": task.comlite}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id:int, db:Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    db.delete(task)
    db.commit()
    return {"complete": task}


@router.get("/users/{user_id}/tasks", response_model=list[TaskRead])
def get_user_posts(user_id: int, db:Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == user_id).all()

    return tasks

