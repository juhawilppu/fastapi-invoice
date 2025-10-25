from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.invoices import Invoice
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import os


class InvoiceRow(BaseModel):
    id: str
    name: str
    quantity: int
    unit_price: float


class InvoiceCreate(BaseModel):
    order_id: str
    customer_id: str
    rows: list[InvoiceRow]


router = APIRouter()


@router.get("/invoices")
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    return invoices


@router.post("/invoices")
def create_invoice(invoice: InvoiceCreate):
    producer = KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: str(k).encode("utf-8"),
    )
    topic = os.getenv("KAFKA_TOPIC", "invoice-events")

    try:
        idempotency_key = invoice.order_id
        payload = invoice.dict()
        payload["_idempotency_key"] = idempotency_key

        future = producer.send(topic, key=idempotency_key, value=payload)
        future.get(timeout=10)
    finally:
        producer.flush()
        producer.close()

    return {"message": "Invoice submitted successfully"}