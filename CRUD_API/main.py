from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel
import json

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

    with open("tasks.json", "r", encoding = "utf-8") as file:
        content = json.load(file)

# when there is nothing in the json file, get the biggest ID there is
        if content !=[]:
            id= max([i["id"] for i in content])
            
    nextId = id + 1
    nextTask={
        "id": nextId,
        "title": title,
        "done": False
    }

    content.append(nextTask)
    with open("tasks.json", "w", encoding="utf-8") as file:
        json.dump(content, file, indent=4)
    return newTask

@app.get("/tasks/{id}")
async def oneTask(id:int):
    task = next((t for t in tasks if t["id"] == id), None)
    
    if not task:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail={"error": f"Task {id} not found"}
       )
    return task
