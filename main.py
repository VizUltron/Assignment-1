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

@app.get("/tasks")
def get_tasks(search: str = None, done: bool = None):

    query = "SELECT * FROM tasks"
    params = []

    if search:
        query += " WHERE title LIKE ?"
        params.append(f"%{search}%")

    if done is not None:
        if search:
            query += " AND done = ?"
        else:
            query += " WHERE done = ?"
        params.append(int(done))

    query += " ORDER BY title"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": bool(row[2])
        }
        for row in rows
    ]

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

    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    # Validate title
    if not task_update.title or task_update.title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    # Update task
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (task_update.title, int(task_update.done), id)
    )
    conn.commit()

    # Return updated task
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }


@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):

    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    # Delete task
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()

    return

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