import sys
import logging
from logging.handlers import RotatingFileHandler


def get_logger(filename, method_name, level=logging.INFO, print_console=False):
    stress_logger = logging.getLogger(method_name)
    stress_logger.setLevel(level)
    azure_logger = logging.getLogger("azure.eventhub")
    azure_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    if print_console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(formatter)
        if not azure_logger.handlers:
            azure_logger.addHandler(console_handler)
        if not uamqp_logger.handlers:
            uamqp_logger.addHandler(console_handler)
        if not stress_logger.handlers:
            stress_logger.addHandler(console_handler)

    if filename:
        file_handler = RotatingFileHandler(filename, maxBytes=20*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        azure_logger.addHandler(file_handler)
        uamqp_logger.addHandler(file_handler)
        stress_logger.addHandler(file_handler)

    return stress_logger