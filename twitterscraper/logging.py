import logging


logger = logging.getLogger('twitterscraper')

formatter = logging.Formatter('%(levelname)s: %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

level = logging.INFO
logger.setLevel(level)
