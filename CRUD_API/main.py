from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel
import json
import os

app = FastAPI(
    version="1.0.0",
    title="Task flow",
    description="Crud operations"
)


class TaskCreate(BaseModel):
    title: str | None=None

class TaskUpdate(BaseModel):
     title:str | None = None
     done:bool | None = None
    


@app.get("/")
async def root():
    return {"name": "Task API", "version":"1.0", "endpoints":["/tasks"]}

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.get("/tasks")
async def task():
    tasks=load_tasks()
    return tasks

@app.post("/tasks", status_code=status.HTTP_201_CREATED,summary="Creates a new task.")
async def newTask(body:TaskCreate):

    # user has to enter task title
    if body.title is None or not body.title.strip():
        raise HTTPException(
                   status_code=status.HTTP_400_BAD_REQUEST,
                   detail={"error": "task has no title!"}
               )
    
    id = 0

    tasks=load_tasks()

# when there is nothing in the json file, get the biggest ID there is
    if tasks !=[]:
        id= max([i["id"] for i in tasks])
            
    nextId = id + 1
    nextTask={
        "id": nextId,
        "title": body.title,
        "done": False
    }

    tasks.append(nextTask)
    save_tasks(tasks)
    return nextTask

@app.get("/tasks/{id}", summary="Displays a task with the specified ID.")
async def oneTask(id:int):
    tasks=load_tasks()

    task = next((t for t in tasks if t["id"] == id), None)
    
    if task is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail={"error": f"Task {id} not found"}
       )
    return task

@app.put("/tasks/{id}", summary="Updates a task.") 
async def updateTask(id:int, body:TaskUpdate):
    tasks=load_tasks()

    task = next((t for t in tasks if t["id"] == id), None)

    if task is None:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail={"error": f"Task {id} not found"}
           )

    if body.title is None and body.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"Send a title update or status update for task {id}"}
        )

    if body.title is not None and not body.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "title cannot be empty"}
        )
    
    if body.title is not None:
         task["title"]=body.title

    if body.done is not None:
        task["done"] = body.done
        
    
         
    save_tasks(tasks)
    return task

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletes a task.")
async def deleteTask(id:int):
    tasks=load_tasks()
    task = next((t for t in tasks if t["id"] == id), None)

    if task is None:
               raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND,
                   detail={"error": f"Task {id} not found"}
               )
    # Delete the task by keeping everything else
    updated_tasks = [t for t in tasks if t["id"] != id]
    save_tasks(updated_tasks)
    return


#helper functions

def load_tasks(filepath="tasks.json"):
     if not os.path.exists(filepath):
          return[]
     with open(filepath,"r") as file:
          return json.load(file)

def save_tasks(tasks, filepath="tasks.json"):
    with open(filepath, "w") as file:
        json.dump(tasks, file, indent=4)