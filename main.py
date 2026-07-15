from fastapi import FastAPI, HTTPException
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