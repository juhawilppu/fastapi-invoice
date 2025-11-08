from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.invoices import Invoice
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import os
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from minio import Minio


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


@router.get("/invoices/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: str, db: Session = Depends(get_db)):

    #invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    #if not invoice:
    #    raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Initialize MinIO client
    minio_client = Minio(
        os.getenv("MINIO_HOST", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=False  # Set to True if using HTTPS
    )
    
    bucket_name = os.getenv("MINIO_BUCKET", "invoices")
    object_name = f"invoice_{invoice_id}.pdf"

    try:
        # Create a temporary file to store the PDF
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            # Get object data from MinIO
            data = minio_client.get_object(bucket_name, object_name)
            # Write to temporary file
            for d in data.stream(32*1024):
                tmp.write(d)
            
            return FileResponse(
                path=tmp.name,
                filename=f"invoice_{invoice_id}.pdf",
                media_type="application/pdf"
            )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"PDF not found: {str(e)}")
    

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