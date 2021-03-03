from discord.ext import commands
import json
import threading
import multiprocessing
import queue
from scrapers.invictus import InvictusNewProductsScraper, InvictusRestockMonitor, start_new_prod_mon
from scrapers.taf import TafNewProdsScraper, TafKeywordMonitor
from extensions.sender import Sender
import configs.global_vars as global_vars
import logging
import os
import discord
import time
from Cogs.bot import start_bot


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

config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))


os.system('pkill chrom')
os.system('pkill Xvfb')

# Products queue
products_queue = multiprocessing.Queue()

multiprocessing.Process(target=start_bot, args=(products_queue,)).start()

# All the processes are connected through queues

# Thread to scrape invictus new products and send to the sender thread
mon = InvictusNewProductsScraper(products_queue)
multiprocessing.Process(target=mon.start).start()
time.sleep(3)

# Invictus Product Restock Monoitor
mon = InvictusRestockMonitor(products_queue)
multiprocessing.Process(target=mon.start).start()
time.sleep(3)

# Start the taf threads
mon = TafNewProdsScraper(products_queue)
multiprocessing.Process(target=mon.start).start()
time.sleep(3)

keywords = ['Dunk']
for keyword in keywords:
    mon = TafKeywordMonitor(products_queue, keyword)
    multiprocessing.Process(target=mon.start).start()
    time.sleep(3)


# bot.run(BOT_TOKEN)
