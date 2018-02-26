import configparser
from logging.config import fileConfig

LOG_LEVEL_KEY = "LOG_LEVEL"
MAIN_SECTION = "main"

cfg = configparser.ConfigParser()
cfg.read("config.ini")

fileConfig("logging.ini", defaults=None, disable_existing_loggers=True)
