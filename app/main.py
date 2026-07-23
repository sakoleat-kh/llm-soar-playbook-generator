from fastapi import FastAPI
from app.routers import webhook, techniques, shuffle
from app.models.database import Base, engine

# Import models so metadata knows about them
from app.models.alert import Alert
from app.models.playbook import Playbook
from app.models.playbook_db import Playbook

app = FastAPI(title="Alert Webhook API")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(webhook.router)
app.include_router(techniques.router)
app.include_router(shuffle.router)