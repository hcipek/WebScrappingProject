import logging

from service.scrapping import start_scrapping

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
start_scrapping()
