import logging

# Get a logger
logging.basicConfig(
    format='[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%SZ',
    level=logging.INFO
)
logger = logging.getLogger()
