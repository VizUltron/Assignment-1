from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Project Milestone API",
    version="1.0.0"
)

sample_milestones = [
    {
        "id": 1,
        "name": "Project Requirements Finalized",
        "completed": True
    },
    {
        "id": 2,
        "name": "Backend API Implemented",
        "completed": False
    },
    {
        "id": 3,
        "name": "Frontend Integration",
        "completed": False
    }
]

milestones = [m.copy() for m in sample_milestones]


class MilestoneCreate(BaseModel):
    name: str


class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    completed: Optional[bool] = None


@app.get("/")
def root():
    return {
        "name": app.title,
        "version": app.version,
        "endpoints": [
            "/health",
            "/milestones"
        ]
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/milestones")
def get_all_milestones():
    return milestones


@app.get("/milestones/{milestone_id}")
def get_milestone(milestone_id: int):
    for milestone in milestones:
        if milestone["id"] == milestone_id:
            return milestone

    return JSONResponse(
        status_code=404,
        content={
            "error": f"Milestone {milestone_id} not found"
        }
    )


@app.post("/milestones", status_code=201)
def create_milestone(data: MilestoneCreate):
    if data.name.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Milestone name cannot be empty"
        )

    milestone = {
        "id": len(milestones) + 1,
        "name": data.name,
        "completed": False
    }

    milestones.append(milestone)

    return milestone


@app.put("/milestones/{milestone_id}")
def update_milestone(
    milestone_id: int,
    update: MilestoneUpdate
):
    if update.name is None and update.completed is None:
        raise HTTPException(
            status_code=400,
            detail="Request body cannot be empty"
        )

    for milestone in milestones:
        if milestone["id"] == milestone_id:

            if update.name is not None:
                milestone["name"] = update.name

            if update.completed is not None:
                milestone["completed"] = update.completed

            return milestone

    raise HTTPException(
        status_code=404,
        detail="Milestone not found"
    )


@app.delete("/milestones/{milestone_id}", status_code=204)
def delete_milestone(milestone_id: int):
    for milestone in milestones:
        if milestone["id"] == milestone_id:
            milestones.remove(milestone)
            return

    raise HTTPException(
        status_code=404,
        detail="Milestone not found"
    )