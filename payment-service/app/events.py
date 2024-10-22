import json
from aiokafka import AIOKafkaProducer
from .settings import BOOTSTRAP_SERVER, KAFKA_PAYMENT_TOPIC

async def publish_event(event: dict):
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        message = json.dumps(event,default=str).encode('utf-8')
        await producer.send_and_wait(KAFKA_PAYMENT_TOPIC, message)
    finally:
        await producer.stop()
