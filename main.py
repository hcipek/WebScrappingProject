import logging

import google.cloud.logging

from service.scrapping import start_scrapping

# Instantiates a client
client = google.cloud.logging.Client()
client.setup_logging()

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

start_scrapping()
