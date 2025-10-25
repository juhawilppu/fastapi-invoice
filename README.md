# FastAPI test

A simple project to test out how modern Python works with FastAPI.

## Run locally

Start services
```
docker compose up -d
```

```
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn alembic psycopg2
alembic upgrade head
uvicorn app.main:app --reload
```

## Try it out

```
curl localhost:8000/hello
```

## API docs

Once running, open: http://localhost:8000/docs