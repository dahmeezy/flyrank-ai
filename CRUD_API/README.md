# Task Flow API

A small to-do list API built with FastAPI for FlyRank assignment BE-01. You can create, read, update and delete tasks (full CRUD), and try everything out in Swagger UI.

Tasks are saved in a `tasks.json` file in the project folder.

## Install & run

You need Python 3.10+.

```bash
git clone https://github.com/dahmeezy/flyrank-ai
cd CRUD_API
python3 -m venv .venv
source .venv/bin/activate
pip install "fastapi[standard]"
```

Then start the server with this one command:

```bash
fastapi dev main.py
```

The API runs at http://127.0.0.1:8000 and the Swagger docs are at http://127.0.0.1:8000/docs.

## Endpoints

| Method | Path | What it does | Success | Errors |
|--------|------|--------------|---------|--------|
| GET | `/` | API name, version and endpoints | 200 | |
| GET | `/health` | Check the server is alive | 200 | |
| GET | `/tasks` | List all tasks | 200 | |
| GET | `/tasks/{id}` | Get one task | 200 | 404 unknown id |
| POST | `/tasks` | Create a task (`{"title": "Buy milk"}`) | 201 | 400 missing or empty title |
| PUT | `/tasks/{id}` | Update a task's `title` and/or `done` | 200 | 400 empty body or blank title, 404 unknown id |
| DELETE | `/tasks/{id}` | Delete a task | 204 (empty body) | 404 unknown id |

A task looks like this:

```json
{ "id": 1, "title": "Buy milk", "done": false }
```

## Example request

```bash
curl -i http://127.0.0.1:8000/tasks/1
```

```
HTTP/1.1 200 OK
date: Thu, 29 Oct 2026 14:31:05 GMT
server: uvicorn
content-length: 39
content-type: application/json

{"id":1,"title":"Exercise","done":true}
```

## Swagger UI

All five task endpoints show up at `/docs`, and "Try it out" works for the full CRUD cycle.

**Create**

![Create a task](docs/swagger-create.png)

**Read**

![Read tasks](docs/swagger-read.png)

**Update**

![Update a task](docs/swagger-update.png)

**Delete**

![Delete a task](docs/swagger-delete.png)