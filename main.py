import json
import multiprocessing as mp
import queue
from scrapers.invictus import InvictusNewProductsScraper, InvictusRestockMonitor, start_new_prod_mon
from scrapers.taf import TafNewProdsScraper, TafKeywordMonitor
from scrapers.liverpool import LiverPoolNewProdsScraper
from scrapers.alivemex import AliveMexNewProdScraper
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

# Kill existing chrome browser and Xvfb
# processes running because of low system memory.
os.system('pkill chrom')
os.system('pkill Xvfb')
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
mon = InvictusRestockMonitor(products_queue)
mp.Process(target=mon.start).start()
time.sleep(psd)

# Start the taf threads
mon = TafNewProdsScraper(products_queue)
mp.Process(target=mon.start).start()
time.sleep(psd)


mon = LiverPoolNewProdsScraper(products_queue)
mp.Process(target=mon.start).start()
time.sleep(psd)

keywords = ['Nike dunk', 'jordan lo', 'jordan mi']
mon = TafKeywordMonitor(products_queue, keywords)
mp.Process(target=mon.start).start()
time.sleep(psd)

mon = AliveMexNewProdScraper(products_queue)
mon = TafKeywordMonitor(products_queue, keywords)
mp.Process(target=mon.start).start()
