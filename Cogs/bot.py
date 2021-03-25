from discord.ext import commands
import discord
from configs import global_vars
import json
from extensions.sender import Sender
import threading
import asyncio
from models.products import (
    InvictusProduct,
    TafProduct,
    LiverPoolProduct,
    AliveMexProduct,
    JetStoreProduct
)
import logging
from datetime import datetime as dt
from datetime import timedelta


config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))
prefix = config.get('COMMAND_PREFIX')
bot = commands.Bot(command_prefix=prefix, heartbeat_timeout=600.0)

BOT_TOKEN = config.get("BOT_TOKEN")

log = logging.getLogger('DiscordBot').info

EMBEDS_COLOR = int('0xff3700', 16)


@bot.event
async def on_ready():
    log('[+] We have logged in as {0.user}'.format(bot))
    log('[+] Loading extensions ...')
    extensions = ['innvictus_commands']
    for ext in extensions:
        try:
            bot.load_extension(f'Cogs.{ext}')
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            pass


@bot.event
async def on_error(error):
    log('Got error in on_error')
    log(error)


def get_timestamp():
    time_format = '%Y-%m-%d %R'
    t = dt.utcnow() - timedelta(hours=6)
    time = t.strftime(time_format).split('.')[0]
    return time


async def create_innvictus_embed(prod:  InvictusProduct):
    embed = discord.Embed(color=EMBEDS_COLOR)
    embed.title = prod.prod_name
    embed.add_field(
        name='Price', value=f'${prod.prod_price}', inline=False)
    embed.set_thumbnail(url=prod.prod_img_link)
    embed.url = prod.prod_link
    desc = '**In-Stock Sizes**'
    for size in prod.in_stock_sizes:
        desc = f'{desc}\n{size}'
    desc = f'{desc}\n**Out-of-Stock Sizes**'
    for size in prod.out_of_stock_sizes:
        desc = f'{desc}\n{size}'
    embed.description = desc
    footer_text = f'Chefsitos MX | {get_timestamp()}'
    embed.set_footer(text=footer_text)
    return embed


async def create_taf_embed(prod:  TafProduct):
    embed = discord.Embed(color=EMBEDS_COLOR)
    embed.title = prod.title
    embed.add_field(
        name='Price', value=f'${prod.price}', inline=False)
    embed.add_field(
        name='Product Model', value=prod.model, inline=False)
    embed.set_thumbnail(url=prod.img_link)
    embed.url = prod.link
    desc = '**In-Stock Sizes**'
    for size in prod.in_stock_sizes:
        desc = f'{desc}\n[{size.size_number}]({size.atc})'
    desc = f'{desc}\n**Out-of-Stock Sizes**'
    for size in prod.out_of_stock_sizes:
        desc = f'{desc}\n{size.size_number}'
    embed.description = desc
    footer_text = f'Chefsitos MX | {get_timestamp()}'
    embed.set_footer(text=footer_text)
    return embed


async def create_liverpool_embed(prod: LiverPoolProduct):
    embed = discord.Embed(color=EMBEDS_COLOR)
    embed.title = prod.name
    embed.add_field(name='Price', value=f'${prod.price}', inline=False)
    embed.url = prod.link
    embed.set_thumbnail(url=prod.img_link)
    embed.add_field(name='Prod Color', value=prod.color, inline=False)
    desc = '**In-Stock Sizes**'
    for size in prod.in_stock_sizes:
        desc = f'{desc}\n{size}'
    desc = f'{desc}\n**Out-of-Stock Sizes**'
    for size in prod.out_of_stock_sizes:
        desc = f'{desc}\n{size}'
    embed.description = desc
    footer_text = f'Chefsitos MX | {get_timestamp()}'
    embed.set_footer(text=footer_text)
    return embed


async def create_alivemex_embed(prod: LiverPoolProduct):
    embed = discord.Embed(color=EMBEDS_COLOR)
    embed.title = prod.name
    embed.add_field(name='Price', value=f'${prod.price}', inline=False)
    embed.url = prod.link
    embed.set_thumbnail(url=prod.img_link)
    footer_text = f'Chefsitos MX | {get_timestamp()}'
    embed.set_footer(text=footer_text)
    return embed


async def create_jetstore_embed(prod: JetStoreProduct):
    embed = discord.Embed(color=EMBEDS_COLOR)
    embed.title = prod.name
    embed.add_field(name='Price', value=f'${prod.price}', inline=False)
    embed.url = prod.link
    desc = '**Sizes**\n'
    for size in prod.sizes:
        desc = f'{desc}\t{size}'
    embed.description = desc
    embed.set_thumbnail(url=prod.img_link)
    footer_text = f'Chefsitos MX | {get_timestamp()}'
    embed.set_footer(text=footer_text)
    return embed


async def after_ready(products_queue):
    while not bot.is_ready():
        await asyncio.sleep(1)
    innvictus_ch_id = config.get("INNVICTUS_CHANNEL_ID")
    taf_channel_id = config.get("TAF_CHANNEL_ID")
    liverpool_channel_id = config.get("LIVERPOOL_CHANNEL_ID")
    alivemex_channel_id = config.get("ALIVEMEX_CHANNEL_ID")
    jetstore_channel_id = config.get("JETSTORE_CHANNEL_ID")
    innvictus_channel = discord.utils.get(
        bot.guilds[0].channels, id=innvictus_ch_id)
    taf_channel = discord.utils.get(
        bot.guilds[0].channels, id=taf_channel_id)
    liverpool_channel = discord.utils.get(
        bot.guilds[0].channels, id=liverpool_channel_id)
    alivemex_channel = discord.utils.get(
        bot.guilds[0].channels, id=alivemex_channel_id)
    jetstore_channel = discord.utils.get(
        bot.guilds[0].channels, id=jetstore_channel_id)
    if innvictus_channel:
        log('[+] Innvictus channel found!')
    if taf_channel:
        log('[+] Taf channel found!')
    if liverpool_channel:
        log('[+] Liverpool Channel found!')
    if alivemex_channel:
        log('[+] AliveMex Channel found!')
    if jetstore_channel:
        log('[+] JetStore Channel found!')

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
        elif isinstance(prod, LiverPoolProduct):
            embed = await create_liverpool_embed(prod)
            await liverpool_channel.send(embed=embed)
        elif isinstance(prod, AliveMexProduct):
            embed = await create_alivemex_embed(prod)
            await alivemex_channel.send(embed=embed)
        elif isinstance(prod, JetStoreProduct):
            embed = await create_jetstore_embed(prod)
            await jetstore_channel.send(embed=embed)


def start_bot(products_queue):
    try:
        bot.loop.create_task(after_ready(products_queue))
        bot.run(BOT_TOKEN)
    except discord.errors.ConnectionClosed:
        print('WS Connection closed!')
        bot.connect(reconnect=True)
