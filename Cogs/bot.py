from discord.ext import commands
import discord
from configs import global_vars
import json
from extensions.sender import Sender
import threading
import asyncio
from models.products import InvictusProduct, TafProduct
import logging


config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))
prefix = config.get('COMMAND_PREFIX')
bot = commands.Bot(command_prefix=prefix)

BOT_TOKEN = config.get("BOT_TOKEN")

log = logging.getLogger('DiscordBot').info


@bot.event
async def on_ready():
    print('[+] We have logged in as {0.user}'.format(bot))
    print('[+] Loading extensions ...')
    channel_id = config.get("INNVICTUS_CHANNEL_ID")
    innvictus_channel = discord.utils.get(
        bot.guilds[0].channels, id=channel_id)
    await innvictus_channel.send('Now online!')
    extensions = ['innvictus_commands']
    for ext in extensions:
        try:
            bot.load_extension(f'Cogs.{ext}')
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            pass


async def create_innvictus_embed(prod:  InvictusProduct):
    embed = discord.Embed()
    embed.title = prod.prod_name
    embed.add_field(
        name='Price', value=f'${prod.prod_price}', inline=False)
    embed.set_image(url=prod.prod_img_link)
    embed.url = prod.prod_link
    desc = '**Available Sizes**'
    for size in prod.in_stock_sizes:
        desc = f'{desc}\n{size}'
    desc = f'{desc}\n**Un Available Sizes**'
    for size in prod.out_of_stock_sizes:
        desc = f'{desc}\n{size}'
    embed.description = desc
    return embed


async def create_taf_embed(prod:  TafProduct):
    embed = discord.Embed()
    embed.title = prod.title
    embed.add_field(
        name='Price', value=f'${prod.price}', inline=False)
    embed.add_field(
        name='Product Model', value=prod.model, inline=False)
    embed.set_image(url=prod.img_link)
    embed.url = prod.link
    desc = '**Available Sizes**'
    for size in prod.in_stock_sizes:
        desc = f'{desc}\n[{size.size_number}]({size.atc})'
    desc = f'{desc}\n**Un Available Sizes**'
    for size in prod.out_of_stock_sizes:
        desc = f'{desc}\n{size.size_number}'
    embed.description = desc
    return embed


async def after_ready(products_queue):
    while not bot.is_ready():
        await asyncio.sleep(1)
    innvictus_ch_id = config.get("INNVICTUS_CHANNEL_ID")
    taf_channel_id = config.get("TAF_CHANNEL_ID")
    innvictus_channel = discord.utils.get(
        bot.guilds[0].channels, id=innvictus_ch_id)
    taf_channel = discord.utils.get(
        bot.guilds[0].channels, id=taf_channel_id)
    if innvictus_channel:
        log('[+] Innvictus channel found!')
    if taf_channel:
        log('[+] Taf channel found!')

    while True:
        while products_queue.empty():
            await asyncio.sleep(1)
        prod = products_queue.get(block=False)
        if isinstance(prod, InvictusProduct):
            embed = await create_innvictus_embed(prod)
            await innvictus_channel.send(embed=embed)
        elif isinstance(prod, TafProduct):
            embed = await create_taf_embed(prod)
            await taf_channel.send(embed=embed)

    # Thread to send the output messages to the channels
    # sender = Sender(bot, products_queue)
    # t = threading.Thread(target=sender.start)
    # t.start()
    # t.join()


def start_bot(products_queue):
    bot.loop.create_task(after_ready(products_queue))
    bot.run(BOT_TOKEN)
