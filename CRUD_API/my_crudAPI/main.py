from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel
import sqlite3
import json
import os

# Database

def create_task_table():
     conn =sqlite3.connect("tasks.db")
     cur = conn.cursor()
     cur.execute(create_table_query)
     conn.commit()
     conn.close()

def seed_tasks_if_empty():
     conn = sqlite3.connect("tasks.db")
     cur = conn.cursor()
     cur.execute("SELECT COUNT(*) FROM tasks")
     count = cur.fetchone()[0]
     if count == 0:
          sql ="INSERT INTO tasks (id, title, done) VALUES (:id, :title, :done)"
          cur.executemany(sql,SEED_TASKS)
     conn.commit()
     conn.close()

def get_all_tasks():
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()
    cur.execute("SELECT id, title, done FROM tasks")
    columns = cur.fetchall()
    conn.close()

    tasks =[]

    for column in columns:
         tasks.append({"id":column[0], "title":column[1], "done":bool(column[2])})
    return tasks


def get_one_task(id:int):
     conn = sqlite3.connect("tasks.db")
     cur = conn.cursor()
     cur.execute("SELECT id, title,done FROM tasks WHERE id=?",(id,))
     column = cur.fetchone()
     conn.close()

     if column is None:
          return None         
     return {"id":column[0], "title":column[1],"done":bool(column[2])}


def add_task(title:str):
     conn =sqlite3.connect("tasks.db")
     cur = conn.cursor()
     cur.execute("INSERT INTO tasks (title, done) VALUES (?,?)",(title,False))
     lastId=cur.lastrowid
     conn.commit()
     conn.close()

     return {"id":lastId,"title":title, "done":False}

     


# create table
create_table_query ="""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN)"""

app = FastAPI(
    version="1.0.0",
    title="Task flow",
    description="Crud operations"
)

SEED_TASKS = [
     {
        "id": 1,
        "title": "Exercise",
        "done": True
    },
    {
        "id": 2,
        "title": "Build a CRUD API",
        "done": True
    },
    
    {
        "id": 3,
        "title": "Read 'Let's go' by Alex Edward",
        "done": False
    }
]



class TaskCreate(BaseModel):
    title: str | None=None

class TaskUpdate(BaseModel):
     title:str | None = None
     done:bool | None = None
    
#helper functions

def load_tasks(filepath="tasks.json"):
     if not os.path.exists(filepath):
          return[]
     with open(filepath,"r") as file:
          return json.load(file)

def save_tasks(tasks, filepath="tasks.json"):
    with open(filepath, "w") as file:
        json.dump(tasks, file, indent=4)


create_task_table()
seed_tasks_if_empty()

@app.get("/", summary="Describes my API.")
async def root():
    return {"name": "Task API", "version":"1.0", "endpoints":["/tasks"]}

@app.get("/health", summary="Checks that server.")
async def health():
    return {"status":"ok"}

@app.get("/tasks",summary="Displays all recorded tasks.")
async def task(done: bool | None = None, search: str | None = None):
    tasks=get_all_tasks()
    result =tasks

    if done is not None:
        result =[t for t in result if t["done"] == done]
    if search is not None:
        result = [t for t in result if search.lower() in t["title"].lower() ]
    return result

    

@app.post("/tasks", status_code=status.HTTP_201_CREATED,summary="Creates a new task.")
async def newTask(body:TaskCreate):

    # user has to enter task title
    if body.title is None or not body.title.strip():
        raise HTTPException(
                   status_code=status.HTTP_400_BAD_REQUEST,
                   detail={"error": "task has no title!"}
               )
    
    # id = 0

    tasks=add_task(body.title)

# when there is nothing in the json file, get the biggest ID there is
    # if tasks !=[]:
    #     id= max([i["id"] for i in tasks])
            
    # nextId = id + 1
    # nextTask={
    #     "id": nextId,
    #     "title": body.title,
    #     "done": False
    # }

    # tasks.append(nextTask)
    # save_tasks(tasks)
    return tasks

@app.get("/tasks/{id}", summary="Displays a task with the specified ID.")
async def oneTask(id:int):
    tasks=get_one_task(id)
    
    if tasks is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail={"error": f"Task {id} not found"}
       )
    return tasks

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

@app.get("/stats", summary="Gives a stat of the total number of tasks, pending one and completed ones.")
async def stat():
     tasks=load_tasks()
     total=len(tasks)
     done =[t for t in tasks if t["done"]==True]
     donee = len(done)
     pending = total-donee
     print(tasks)
     return {"total":total,
             "done":donee,
             "open":pending}

@app.post("/reset", summary="Restores the seed tasks.")
async def reset():
     save_tasks(SEED_TASKS)
     return SEED_TASKS