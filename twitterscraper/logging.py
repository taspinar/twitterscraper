import logging


logger = logging.getLogger('twitterscraper')
handler = logging.Handler(format='%(levelname)s: %(message)s', level=logging.INFO)
logger.addHandler(handler)
