# app/events.py

import json
from aiokafka import AIOKafkaProducer
from .settings import BOOTSTRAP_SERVER,KAFKA_USER_TOPIC
import asyncio
import logging

logger = logging.getLogger(__name__)

producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)

async def init_producer():
    if not producer.started:
        await producer.start()
        logger.info("Kafka producer started.")

async def close_producer():
    if producer and producer.started:
        await producer.stop()
        logger.info("Kafka producer stopped.")

async def publish_event(event: dict):
    try:
        await init_producer()
        # Serialize with default=str to handle datetime objects
        message = json.dumps(event, default=str).encode('utf-8')
        await producer.send_and_wait(KAFKA_USER_TOPIC, message)
        logger.info(f"Published event to Kafka: {event}")
    except Exception as e:
        logger.error(f"Failed to publish event: {e}", exc_info=True)
