import os
from fastapi import FastAPI, APIRouter
from models import UserEvent, PaymentEvent, MovieEvent
from kafka_handler import app as faststream_app, publish_user_event, publish_payment_event, publish_movie_event, broker
import uvicorn

app = FastAPI(title="Events Service")
router = APIRouter(prefix="/api/events")


@router.get("/health")
async def health_check():
    return {"status": True}


@router.post("/user", status_code=201)
async def create_user_event(event: UserEvent):
    await publish_user_event(event)
    return {"status": "success"}


@router.post("/payment", status_code=201)
async def create_payment_event(event: PaymentEvent):
    await publish_payment_event(event)
    return {"status": "success"}


@router.post("/movie", status_code=201)
async def create_movie_event(event: MovieEvent):
    await publish_movie_event(event)
    return {"status": "success"}


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    await broker.start()  # Explicitly connect the Kafka broker


@app.on_event("shutdown")
async def shutdown_event():
    await broker.close()  # Cleanly disconnect the Kafka broker


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8082))
    uvicorn.run(app, host="0.0.0.0", port=port)
