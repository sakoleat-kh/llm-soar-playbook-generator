from fastapi import FastAPI
from app.routers import webhook

app = FastAPI(title="Alert Webhook API")

app.include_router(webhook.router)

