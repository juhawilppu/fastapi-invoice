from fastapi import APIRouter
from pydantic import BaseModel
from kafka import KafkaProducer
from typing import Optional
import json
import os
import uuid


class Event(BaseModel):
    idempotency_key: Optional[str] = None
    user_id: str
    amount: int
    currency: str


router = APIRouter()


@router.post("/events")
def submit_event(event: Event):
    producer = KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: str(k).encode("utf-8"),
    )
    topic = os.getenv("KAFKA_TOPIC", "invoice-events")

    try:
        idempotency_key = event.idempotency_key or str(uuid.uuid4())
        payload = event.dict()
        payload["_idempotency_key"] = idempotency_key

        # send the idempotency key as the Kafka message key (affects partitioning and works with log compaction)
        future = producer.send(topic, key=idempotency_key, value=payload)
        future.get(timeout=10)
    finally:
        producer.flush()
        producer.close()

    return {"message": "Event submitted successfully"}