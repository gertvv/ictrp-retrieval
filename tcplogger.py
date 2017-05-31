import logging
import logging.handlers

def makeLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.handlers.SocketHandler('localhost',
                  logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    logger.handlers = []
    logger.addHandler(handler)
    return logger
