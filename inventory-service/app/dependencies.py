from sqlmodel import Session, create_engine
from app import settings

# Explicitly cast DATABASE_URL to string
DATABASE_URL = str(settings.DATABASE_URL)

# Create the engine without additional connect_args since sslmode is disabled in the URL
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "disable"})

def get_session():
    with Session(engine) as session:
        yield session




# from aiokafka import AIOKafkaProducer
# from sqlmodel import Session
# from app.db_engine import engine

# # Kafka Producer as a dependency
# async def get_kafka_producer():
#     producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
#     await producer.start()
#     try:
#         yield producer
#     finally:
#         await producer.stop()

# def get_session():
#     with Session(engine) as session:
#         yield session

