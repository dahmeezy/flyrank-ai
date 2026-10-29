from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel
import json
import os

app = FastAPI(
    version="1.0.0",
    title="Task flow",
    description="Crud operations"
)

tasks=[
    # {
    #     "id":1,
    #     "title":"Read 2 pages of `Let's Go`",
    #     "done":False
    # },
    # {
    #     "id":2,
    #     "title":"Do flyrank assignment",
    #     "done":True
    # },
    # {
    #     "id":3,
    #     "title":"Resolve 10 github issues",
    #     "done":False
    # },
]

class Item(BaseModel):
    id: int | None = None
    title: str
    done: bool | None = None

    def __init__(self, id, title, done):
        self.id = id
        self.title = title
        self.done = done



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

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def newTask(title:str):

    # user has to enter task title
    if title == "":
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
        "title": title,
        "done": False
    }

    tasks.append(nextTask)
    save_tasks(tasks)
    return newTask

@app.get("/tasks/{id}")
async def oneTask(id:int):
    tasks=load_tasks()

    task = next((t for t in tasks if t["id"] == id), None)
    
    if not task:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail={"error": f"Task {id} not found"}
       )
    return task

@app.put("/tasks/{id}") 
async def updateTask(id:int, title:str|None=None, done:bool|None=None ):
    tasks=load_tasks()

    task = next((t for t in tasks if t["id"] == id), None)

    if not task:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail={"error": f"Task {id} not found"}
           )
    if title is None and done is None:
        raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail={"error": f"Send a title update or status update for task {id}"}
        )
    
    if title is not None:
         task["title"]=title

    if done is not None:
        task["done"] = done
        
    
         
    save_tasks(tasks)
    return task

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteTask(id:int):
    tasks=load_tasks()
    task = next((t for t in tasks if t["id"] == id), None)

    if not task:
               raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND,
                   detail={"error": f"Task {id} not found"}
               )
    else:
         # Delete the task by keeping everything else
        updated_tasks = [t for t in tasks if t["id"] != id]
        save_tasks(updated_tasks)
    return f"Task {id} deleted."


#helper functions

def load_tasks(filepath="tasks.json"):
     if not os.path.exists(filepath):
          return[]
     with open(filepath,"r") as file:
          return json.load(file)

def save_tasks(tasks, filepath="tasks.json"):
    with open(filepath, "w") as file:
        json.dump(tasks, file, indent=4)