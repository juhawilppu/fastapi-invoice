# FastAPI test

A simple project to test out how modern Python works with FastAPI.

## Run locally

Start services
```
docker compose up -d
```

## Start producer

```
cd fastapi-producer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Start consumer

```
cd consumer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python consumer.py
```

## Try it out

```
for i in {1..10}; do
  curl -X POST localhost:8000/events \
       -H "Content-Type: application/json" \
       -d "{\"id\": \"$i\", \"user_id\": \"test-event-$i\", \"amount\": 100, \"currency\": \"USD\", \"idempotency_key\": \"key-$i\"}"
  echo
done
```

## API docs

Once running, open: http://localhost:8000/docs