from discord.ext import commands
import json
import threading
import queue
from scrapers.invictus import InvictusNewProductsScraper, InvictusRestockMonitor
from scrapers.taf import TafNewProdsScraper, TafKeywordMonitor
from extensions.sender import Sender
import configs.global_vars as global_vars
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

config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))

prefix = config.get('COMMAND_PREFIX')
bot = commands.Bot(command_prefix=prefix)

BOT_TOKEN = config.get("BOT_TOKEN")


@bot.event
async def on_ready():
    print('[+] We have logged in as {0.user}'.format(bot))
    print('[+] Loading extensions ...')
    extensions = ['innvictus_commands']
    for ext in extensions:
        bot.load_extension(f'Cogs.{ext}')

    # All the threads are connected through queues

    # Products queue
    products_queue = queue.Queue()

    # Thread to scrape invictus new products and send to the sender thread
    invictus = InvictusNewProductsScraper(products_queue)
    threading.Thread(target=invictus.start).start()
    time.sleep(3)

    # Invictus Product Restock Monoitor
    mon = InvictusRestockMonitor(products_queue)
    threading.Thread(target=mon.start).start()
    time.sleep(3)

    # Start the taf threads
    mon = TafNewProdsScraper(products_queue)
    threading.Thread(target=mon.start).start()
    time.sleep(3)

    keywords = ['Dunk']
    for keyword in keywords:
        mon = TafKeywordMonitor(products_queue, keyword)
        threading.Thread(target=mon.start).start()
        time.sleep(3)

    # Thread to send the output messages to the channels
    sender = Sender(bot, products_queue)
    threading.Thread(target=sender.start).start()


bot.run(BOT_TOKEN)
