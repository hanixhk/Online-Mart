import json
from aiokafka import AIOKafkaProducer
from .settings import BOOTSTRAP_SERVER, KAFKA_ORDER_TOPIC

async def publish_event(event: dict):
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        message = json.dumps(event,default=str).encode('utf-8')
        await producer.send_and_wait(KAFKA_ORDER_TOPIC, message)
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"Failed to publish event: {e}")
    finally:
        await producer.stop()
