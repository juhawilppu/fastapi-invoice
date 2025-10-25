# fastkafka-lab

A small project to explore Kafka and event-driven architecture.

## 🧩 Architecture
- `fastapi-producer` – exposes `/events` endpoint and publishes to Kafka
- `consumer` - reads and processes events
- `docker-compose.yml` - runs Kafka and ZooKeeper services

## 🚀 Run locally

Start Kafka and ZooKeeper
```
docker compose up -d
```

### Producer

```
cd fastapi-producer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Consumer

```
cd consumer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python consumer.py
```

## 🧪 Try it out

This will submit 100 events to the queue.

```
```
for i in {1..100}; do
  curl -X POST localhost:8000/events \
       -H "Content-Type: application/json" \
       -d "{\"id\": \"$i\", \"user_id\": \"test-event-$i\", \"amount\": 100, \"currency\": \"USD\", \"idempotency_key\": \"key-$i\"}"
  echo
done
```

```

## 📘 API docs

http://localhost:8000/docs

## 🧠 Goal

I've worked with queues such as RabbitMQ and AWS SQS, but Kafka always felt mysterious. This project was my attempt to finally understand what Kafka does.