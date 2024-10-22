from starlette.config import Config
from starlette.datastructures import Secret


try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()


DATABASE_URL = config("DATABASE_URL", cast=Secret)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str, default="user-topic")
KAFKA_CONSUMER_GROUP_ID_FOR_USER = config("KAFKA_CONSUMER_GROUP_ID_FOR_USER", cast=str, default="user-service-group")

TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=str)
