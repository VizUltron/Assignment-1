from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Task API",
    version="1.0.0"
)

tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Build CRUD API",
        "done": False
    },
    {
        "id": 3,
        "title": "Submit Assignment",
        "done": False
    }
]


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/")
def home():
    return {
        "name": app.title,
        "version": app.version,
        "endpoints": [
            "/health",
            "/tasks"
        ]
    }


@app.get("/health")
def health():
    return {
        "message": "OK"
    }


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": "Task not found"}
    )


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):

    if task.title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


@app.put("/tasks/{id}")
def update_task(id: int, task_update: TaskUpdate):

    if task_update.title is None and task_update.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )

    for task in tasks:

        if task["id"] == id:

            if task_update.title is not None:

                if task_update.title.strip() == "":
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Title is required"}
                    )

                task["title"] = task_update.title

            if task_update.done is not None:
                task["done"] = task_update.done

            return task

    return JSONResponse(
        status_code=404,
        content={"error": "Task not found"}
    )


@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):

    for task in tasks:

        if task["id"] == id:
            tasks.remove(task)
            return

    return JSONResponse(
        status_code=404,
        content={"error": "Task not found"}
    )