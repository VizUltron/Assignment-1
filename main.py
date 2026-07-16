from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    
tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Build Assignment",
        "done": True
    },
    {
        "id": 3,
        "title": "Submit Project",
        "done": False
    }
]
app = FastAPI()
@app.get("/")
def home():
    return { 
        "name" : app.title,
        "version" : app.version,
        "endpoints" : ["/tasks"]
    }
    
@app.get("/health")
def health():
    return {"message": "OK"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    return {"message": "Task not found"}

@app.post("/tasks", status_code=201)
def create_task(title: str):
    if title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )
    new_task = {
        "id": len(tasks) + 1,
        "title": title,
        "done": False
    }

    tasks.append(new_task)
    return new_task

from fastapi import HTTPException

@app.put("/tasks/{id}", status_code=200)
def update_task(id: int, task_update: TaskUpdate):
    # Empty body -> 400
    if task_update.title is None and task_update.done is None:
        raise HTTPException(
            status_code=400,
            detail="Request body cannot be empty"
        )

    for task in tasks:
        if task["id"] == id:
            if task_update.title is not None:
                task["title"] = task_update.title

            if task_update.done is not None:
                task["done"] = task_update.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )

@app.get("/stats")
def get_stats():
    total = len(tasks)
    done = sum(1 for task in tasks if task["done"])
    open_tasks = total - done

    return {
        "total": total,
        "done": done,
        "open": open_tasks
    }

@app.post("/reset")
def reset_tasks():
    global task

    task = [task.copy() for task in tasks]

    return {
        "message": "Tasks reset successfully",
        "tasks": task
    }