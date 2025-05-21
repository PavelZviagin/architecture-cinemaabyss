import os
import logging
from faststream import FastStream, Logger
from faststream.kafka import KafkaBroker
from pydantic import BaseModel
from models import UserEvent, PaymentEvent, MovieEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

broker = KafkaBroker(os.getenv("KAFKA_BROKERS", "kafka:9092"))
app = FastStream(broker)


class KafkaEvent(BaseModel):
    event_type: str
    data: dict


async def publish_user_event(event: UserEvent):
    kafka_event = KafkaEvent(event_type="user", data=event.dict())
    await broker.publish(kafka_event.dict(), topic="user-events")


async def publish_payment_event(event: PaymentEvent):
    kafka_event = KafkaEvent(event_type="payment", data=event.dict())
    await broker.publish(kafka_event.dict(), topic="payment-events")


async def publish_movie_event(event: MovieEvent):
    kafka_event = KafkaEvent(event_type="movie", data=event.dict())
    await broker.publish(kafka_event.dict(), topic="movie-events")

@app.broker.subscriber("user-events")
async def handle_user_event(event: KafkaEvent, logger: Logger):
    logger.info(f"Consumed user event: {event.dict()}")


@app.broker.subscriber("payment-events")
async def handle_payment_event(event: KafkaEvent, logger: Logger):
    logger.info(f"Consumed payment event: {event.dict()}")


@app.broker.subscriber("movie-events")
async def handle_movie_event(event: KafkaEvent, logger: Logger):
    logger.info(f"Consumed movie event: {event.dict()}")
