from fastapi import FastAPI
from app.routers import invoices

app = FastAPI()


@app.get("/hello")
def read_root():
    return {"message": "Hello, world"}


app.include_router(invoices.router)
