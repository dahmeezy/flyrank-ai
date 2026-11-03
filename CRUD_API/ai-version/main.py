from typing import Optional

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# App + docs metadata
# ---------------------------------------------------------------------------
tags_metadata = [
    {"name": "Root", "description": "Health check / list of all tasks."},
    {"name": "Tasks", "description": "Create, read, update and delete tasks."},
]

app = FastAPI(
    title="Tasks API",
    description=(
        "A simple in-memory CRUD API for recording tasks.\n\n"
        "**Error format:** every error returns JSON like "
        '`{"error": "Task 99 not found"}`.'
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class TaskIn(BaseModel):
    title: str = Field(..., min_length=1, description="Short title of the task", examples=["Buy groceries"])
    description: Optional[str] = Field(None, description="Optional details", examples=["Milk, eggs, bread"])
    completed: bool = Field(False, description="Whether the task is done")


class Task(TaskIn):
    id: int = Field(..., description="Unique task id", examples=[1])


class ErrorResponse(BaseModel):
    error: str = Field(..., examples=["Task 99 not found"])


# ---------------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------------
tasks: dict[int, Task] = {}
next_id = 1


class TaskNotFound(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.exception_handler(TaskNotFound)
async def task_not_found_handler(request: Request, exc: TaskNotFound):
    return JSONResponse(status_code=404, content={"error": f"Task {exc.task_id} not found"})


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    # FastAPI defaults to 422; the spec wants 400 for empty/invalid bodies.
    parts = []
    for e in exc.errors():
        loc = ".".join(str(p) for p in e["loc"] if p != "body")
        parts.append(f"{loc}: {e['msg']}" if loc else e["msg"])
    return JSONResponse(status_code=400, content={"error": "Invalid request: " + "; ".join(parts)})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get(
    "/",
    tags=["Root"],
    summary="List all tasks",
    description="Returns every task currently stored. Returns an empty list if there are none.",
    response_model=list[Task],
)
def list_tasks():
    return list(tasks.values())


@app.post(
    "/tasks",
    tags=["Tasks"],
    summary="Create a task",
    description="Creates a new task and returns it with its generated `id`. `title` is required.",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse, "description": "Empty or invalid request body"}},
)
def create_task(body: TaskIn):
    global next_id
    task = Task(id=next_id, **body.model_dump())
    tasks[next_id] = task
    next_id += 1
    return task


@app.get(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Get one task",
    description="Fetch a single task by its id.",
    response_model=Task,
    responses={404: {"model": ErrorResponse, "description": "No task with that id"}},
)
def get_task(task_id: int):
    if task_id not in tasks:
        raise TaskNotFound(task_id)
    return tasks[task_id]


@app.put(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Update a task",
    description="Replaces the task's fields with the body provided and returns the updated task.",
    response_model=Task,
    responses={
        400: {"model": ErrorResponse, "description": "Empty or invalid request body"},
        404: {"model": ErrorResponse, "description": "No task with that id"},
    },
)
def update_task(task_id: int, body: TaskIn):
    if task_id not in tasks:
        raise TaskNotFound(task_id)
    updated = Task(id=task_id, **body.model_dump())
    tasks[task_id] = updated
    return updated


@app.delete(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Delete a task",
    description="Deletes the task. Returns `204 No Content` with an empty body on success.",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={404: {"model": ErrorResponse, "description": "No task with that id"}},
)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise TaskNotFound(task_id)
    del tasks[task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Hide FastAPI's auto-generated 422 from Swagger (we return 400 instead)
# ---------------------------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
    )
    for path in schema["paths"].values():
        for op in path.values():
            op.get("responses", {}).pop("422", None)
    schema.get("components", {}).get("schemas", {}).pop("HTTPValidationError", None)
    schema.get("components", {}).get("schemas", {}).pop("ValidationError", None)
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi