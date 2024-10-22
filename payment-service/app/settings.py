from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=str)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str, default="broker:19092")
KAFKA_PAYMENT_TOPIC = config("KAFKA_PAYMENT_TOPIC", cast=str, default="payment-topic")
KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT", cast=str, default="payment-service-group")

# PAYFAST_API_KEY = config("PAYFAST_API_KEY", cast=str, default="your_payfast_api_key")
STRIPE_API_KEY = config("STRIPE_API_KEY", cast=str, default="your_stripe_api_key")
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=str)