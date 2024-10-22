from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=str)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str, default="broker:19092")
KAFKA_INVENTORY_TOPIC = config("KAFKA_INVENTORY_TOPIC", cast=str, default="inventory-topic")
KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY = config("KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY", cast=str, default="inventory-service-group")

TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=str)



# from starlette.config import Config
# from starlette.datastructures import Secret

# try:
#     config = Config(".env")
# except FileNotFoundError:
#     config = Config()

# DATABASE_URL = config("DATABASE_URL", cast=Secret)
# KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)

# BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)

# KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)
# TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)
