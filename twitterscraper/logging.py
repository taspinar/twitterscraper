import logging


logger = logging.getLogger('twitterscraper')

formatter = logging.Formatter('%(levelname)s: %(message)s')
logger.setFormatter(formatter)

level = logging.INFO
logger.setLevel(level)
