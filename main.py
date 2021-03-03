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
from concurrent.futures import ProcessPoolExecutor


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

executor = ProcessPoolExecutor()


@bot.event
async def on_ready():
    print('[+] We have logged in as {0.user}'.format(bot))
    print('[+] Loading extensions ...')
    channel_id = config.get("INNVICTUS_CHANNEL_ID")
    innvictus_channel = discord.utils.get(
        bot.guilds[0].channels, id=channel_id)
    # await innvictus_channel.send('Now online!')
    extensions = ['innvictus_commands']
    for ext in extensions:
        bot.load_extension(f'Cogs.{ext}')

    # Thread to send the output messages to the channels
    sender = Sender(bot, products_queue)
    threading.Thread(target=sender.start).start()

os.system('pkill chrom')
os.system('pkill Xvfb')

# Products queue
products_queue = multiprocessing.Queue()

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


bot.run(BOT_TOKEN)
