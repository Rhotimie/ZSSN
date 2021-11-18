import os, logging
from config.settings import BASEDIR


def log_handler(file_name, info=False):
    log_file = 'time.log' if info else 'process.log'
    log_file_path = os.path.join(BASEDIR, 'log', log_file)
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s==>%(message)s:%(asctime)s') if info else logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(lineno)d:%(message)s')
    
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if info: return logger

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger



