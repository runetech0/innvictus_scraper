from discord.ext import commands
import json
import threading
import queue
from scrapers.invictus import InvictusNewProductsScraper
from extensions.sender import Sender

config = json.load(open('config.json', 'r'))

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

    # Thread to send the output messages to the channels
    sender = Sender(bot, products_queue)
    threading.Thread(target=sender.start).start()


bot.run(BOT_TOKEN)
