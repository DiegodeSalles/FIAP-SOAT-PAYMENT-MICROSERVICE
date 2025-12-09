from fastapi import FastAPI
from src.infrastructure.api.routers import router_payment
from src.infrastructure.api.webhook_router import router_webhook

app = FastAPI(title="Payment Service", version="1.0.0")

app.include_router(router_payment, prefix="/api/v1")
app.include_router(router_webhook, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}