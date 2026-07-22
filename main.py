from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    done INTEGER
    );
""")
conn.commit()



class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    
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
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    return rows

@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    rows = cursor.fetchall()
    if(len(rows) == 0):
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )
    return rows

@app.post("/tasks", status_code=201)
def create_task(title: str):

    if not title or title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title, 0)
    )
    conn.commit()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (cursor.lastrowid,)
    )

    row = cursor.fetchone()




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