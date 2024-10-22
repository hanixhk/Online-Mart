from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=str)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str, default="kafka:9092")
KAFKA_NOTIFICATION_TOPIC = config("KAFKA_NOTIFICATION_TOPIC", cast=str, default="notification-topic")
KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION = config("KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION", cast=str, default="notification-service-group")

SMTP_SERVER = config("SMTP_SERVER", cast=str)
SMTP_PORT = config("SMTP_PORT", cast=int, default=587)
SMTP_USERNAME = config("SMTP_USERNAME", cast=str)
SMTP_PASSWORD = config("SMTP_PASSWORD", cast=str)

TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", cast=str)
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", cast=str)
TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER", cast=str)

TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=str)
