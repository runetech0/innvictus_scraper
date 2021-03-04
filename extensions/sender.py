import queue
import asyncio
from models.products import InvictusProduct, TafProduct, LiverPoolProduct
import json
import discord
import configs.global_vars as global_vars
import logging


class Sender:
    def __init__(self, bot, queue: queue.Queue):
        self.bot = bot
        self.config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))
        self.innvictus_channel_id = self.config.get("INNVICTUS_CHANNEL_ID")
        self.taf_channel_id = self.config.get("TAF_CHANNEL_ID")
        self.queue = queue
        self.loop = self.bot.loop
        self.log = logging.getLogger(' Sender ').info

    def start(self):
        self.loop.create_task(self.main())

    async def read_up(self):
        self.innvictus_channel = discord.utils.get(
            self.bot.guilds[0].channels, id=self.innvictus_channel_id)
        if self.innvictus_channel is None:
            self.log('[-] Could Not find Output Channel for innvictus')
            return
        self.log('[+] Innvictus Channel found!')

        self.taf_channel = discord.utils.get(
            self.bot.guilds[0].channels, id=self.taf_channel_id)
        if self.innvictus_channel is None:
            self.log('[-] Could Not find Output Channel for taf')
            return
        self.log('[+] Taf Channel found!')

    async def main(self):
        print("Sender main")
        await self.read_up()
        self.log('[+] Sender is ready!')
        while True:
            while self.queue.empty():
                await asyncio.sleep(1)
            prod = self.queue.get(block=False)
            if isinstance(prod, InvictusProduct):
                await self.handle_invictus_prod(prod)
            elif isinstance(prod, TafProduct):
                self.log('Got taf prod')
                await self.handle_taf_prod(prod)

    async def handle_invictus_prod(self, prod:  InvictusProduct):
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
        if self.innvictus_channel is not None:
            await self.innvictus_channel.send(embed=embed)

    async def handle_taf_prod(self, prod:  TafProduct):
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
        if self.taf_channel is not None:
            await self.taf_channel.send(embed=embed)
