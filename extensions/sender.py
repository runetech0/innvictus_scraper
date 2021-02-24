import queue
import asyncio
from models.products import InvictusProduct
import json
import discord


class Sender:
    def __init__(self, bot, queue: queue.Queue):
        self.bot = bot
        self.config = json.load(open('config.json', 'r'))
        self.innvictus_channel_id = self.config.get("OUTPUT_CHANNEL_ID")
        self.queue = queue
        self.loop = self.bot.loop

    def start(self):
        self.loop.create_task(self.main())

    async def read_up(self):
        self.innvictus_channel = discord.utils.get(
            self.bot.guilds[0].channels, id=self.innvictus_channel_id)
        if self.innvictus_channel is None:
            print('[-] Could Not find Innvictus Channel.')
            return
        print('[+] Innvictus Channel found!')

    async def main(self):
        await self.read_up()
        print('[+] Sender is ready!')
        while True:
            while self.queue.empty():
                await asyncio.sleep(1)
            prod = self.queue.get(block=False)
            if isinstance(prod, InvictusProduct):
                await self.handle_invictus_prod(prod)

    async def handle_invictus_prod(self, prod:  InvictusProduct):
        embed = discord.Embed()
        embed.title = prod.prod_name
        embed.add_field(name='Product Link', value=prod.prod_link)
        embed.add_field(name='Price', value=prod.prod_price)
        embed.add_field(name='Product Type', value=prod.prod_gender)
        embed.set_image(url=prod.prod_img_link)
        if self.innvictus_channel is not None:
            await self.innvictus_channel.send(embed=embed)
