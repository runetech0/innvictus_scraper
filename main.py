import json
import multiprocessing as mp
import queue
from scrapers.invictus import InvictusNewProductsScraper, InvictusRestockMonitor
from scrapers.taf import TafNewProdsScraper, TafKeywordMonitor
from scrapers.liverpool import LiverPoolNewProdsScraper
from scrapers.alivemex import AliveMexNewProdScraper
from scrapers.jetstore import JetStoreScraper
from extensions.restock_helper import RestockHelper
from extensions.sender import Sender
from Cogs.bot import start_bot
import logging
import os
import time


logger = logging.getLogger()
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
formator = logging.Formatter(
    '[%(asctime)s] - [%(name)s] - %(levelname)s - %(message)s')
consoleHandler.setFormatter(formator)
if not os.path.exists('./logs'):
    os.mkdir('logs')
fileHandler = logging.FileHandler('logs/app.log')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formator)
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)

logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

# Kill existing chrome browser and Xvfb
# processes running because of low system memory.
# os.system('pkill chrom')
# os.system('pkill Xvfb')
psd = 10

# Products queue
products_queue = mp.Queue()

mp.Process(target=start_bot, args=(products_queue,)).start()
time.sleep(psd)

# All the processes are connected through queues

# Thread to scrape invictus new products and send to the sender thread
mon = InvictusNewProductsScraper(products_queue)
mp.Process(target=mon.start).start()
time.sleep(psd)

# Invictus Product Restock Monoitor

restock_queue = mp.Queue()

# helper = RestockHelper(restock_queue)
# mp.Process(target=helper.start).start()


# for i in range(5):
#     mon = InvictusRestockMonitor(products_queue, restock_queue)
#     mp.Process(target=mon.start).start()
#     time.sleep(2)
# time.sleep(psd)

# Start the taf threads
links = [
    'https://www.taf.com.mx/dunk',
    'https://www.taf.com.mx/jordan'
]
for link in links:
    mon = TafNewProdsScraper(products_queue, link)
    mp.Process(target=mon.start).start()
    time.sleep(3)
time.sleep(psd)


mon = LiverPoolNewProdsScraper(products_queue)
mp.Process(target=mon.start).start()
time.sleep(psd)

keywords = ['Nike dunk', 'lo', 'mi']
mon = TafKeywordMonitor(products_queue, keywords)
mp.Process(target=mon.start).start()
time.sleep(psd)

keywords = ['jordan hi', 'jordan 1', 'dun']
mon = TafKeywordMonitor(products_queue, keywords)
mp.Process(target=mon.start).start()
time.sleep(psd)

keywords = ["du" "low" "hi"]
mon = TafKeywordMonitor(products_queue, keywords)
mp.Process(target=mon.start).start()
time.sleep(psd)

keywords = ["high", "retro", "yeezy"]
mon = TafKeywordMonitor(products_queue, keywords)
mp.Process(target=mon.start).start()
time.sleep(psd)


mon = AliveMexNewProdScraper(products_queue)
mp.Process(target=mon.start).start()
time.sleep(psd)


mon = JetStoreScraper(products_queue)
mp.Process(target=mon.start).start()
time.sleep(psd)
