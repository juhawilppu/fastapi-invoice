from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.invoices import Invoice
from pydantic import BaseModel


class InvoiceCreate(BaseModel):
    status: str
    amount: int
    currency: str


router = APIRouter()


@router.get("/invoices")
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    return invoices


@router.post("/invoices")
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = Invoice(**invoice.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice
