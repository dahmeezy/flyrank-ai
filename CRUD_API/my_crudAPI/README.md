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
| GET | `/stats` | Gives a stat of recorded tasks | 200 | |
| POST | `/tasks` | Create a task (`{"title": "Buy milk"}`) | 201 | 400 missing or empty title |
| POST | `/reset` | Restores the seed tasks  | 200 | |
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

#### Observation

I got all the tasks from before after restarting the server. The server has a persistent storage. I used a JSON file as it database and it gets loaded before any of the handlers handles any route.


### AI vs me

#### my prompt

I need you to build a CRUD API for recording tasks in python using fastapi,  with endpoints :get /, post /tasks, post /tasks/:id f no task has that id, return status 404 with a JSON error: `{ "error": "Task 99 not found" } `, put /tasks/:id Returns the updated task. Unknown id → `404` . Empty/invalid body → `400`, delete /tasks/:id Return status 204 ("No Content" — success, nothing to say) with an empty body. Unknown id → `404` . make it so that the swagger UI clearly describes the endpoints that were built.



- Claude's description of the endpoints on swagger UI is cleaner. It handled errors and status code different than I thought. It does not persist and i idont understand its version.

- It silently ignores the json error that i specified for it to output when a task that someone is trying to retrieve does not exist.

- I forgot to specify that it should do it in the simplest/basic way. I think it assumed I'm already good at this and did it the standard way.