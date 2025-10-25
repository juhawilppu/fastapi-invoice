from fastapi import FastAPI
from app.routers import invoices
from app.routers import events

app = FastAPI()


@app.get("/hello")
def read_root():
    return {"message": "Hello, world"}


app.include_router(invoices.router)
app.include_router(events.router)