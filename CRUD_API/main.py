from fastapi import FastAPI, HTTPException,status


app = FastAPI(
    version="1.0.0",
    title="Task flow",
    description="Crud operations"
)

tasks=[
    {
        "id":1,
        "title":"Read 2 pages of `Let's Go`",
        "done":False
    },
    {
            "id":2,
            "title":"Do flyrank assignment",
            "done":True
        },
    {
                "id":3,
                "title":"Resolve 10 github issues",
                "done":False
            },
]
@app.get("/")
async def root():
    return {"name": "Task API", "version":"1.0", "endpoints":["/tasks"]}

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.get("/tasks")
async def task():
    return tasks

@app.get("/tasks/{id}")
async def oneTask(id:int):
    task = next((t for t in tasks if t["id"] == id), None)
    
    if not task:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail={"error": f"Task {id} not found"}
       )
    return task