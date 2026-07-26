from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from db import conn, cursor

app = FastAPI(
    title="Task API",
    version="1.0.0"
)

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
    cursor.execute("SELECT id, title, done FROM tasks ORDER BY id")
    rows = cursor.fetchall()
    return [{"id": row[0], "title": row[1], "done": row[2]} for row in rows]

@app.get("/tasks/{id}")
def get_task(id: int):
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (id,))
    row = cursor.fetchone()
    if row:
        return {"id": row[0], "title": row[1], "done": row[2]}
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

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
        (task.title, False)
    )
    row = cursor.fetchone()
    conn.commit()

    return {"id": row[0], "title": row[1], "done": row[2]}

@app.put("/tasks/{id}")
def update_task(id: int, task_update: TaskUpdate):
    if task_update.title is None and task_update.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )

    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (id,))
    row = cursor.fetchone()

    if not row:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    current_title = row[1]
    current_done = row[2]

    new_title = task_update.title if task_update.title is not None else current_title
    if new_title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    new_done = task_update.done if task_update.done is not None else current_done

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
        (new_title, new_done, id)
    )
    updated_row = cursor.fetchone()
    conn.commit()

    return {"id": updated_row[0], "title": updated_row[1], "done": updated_row[2]}

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (id,))
    deleted = cursor.fetchone()
    if deleted:
        conn.commit()
        return
    return JSONResponse(
        status_code=404,
        content={"error": "Task not found"}
    )