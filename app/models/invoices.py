from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..database import Base


class Invoice(Base):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, unique=True, index=True)
    amount = Column(Integer)
    currency = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Invoice {self.id}>"

    def __str__(self):
        return f"<Invoice {self.id}>"
