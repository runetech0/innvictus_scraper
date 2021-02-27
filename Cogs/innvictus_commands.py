from discord.ext import commands
from extensions.db import DB
import logging


class InnvictusCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DB()
        self.log = logging.getLogger(' Innvictus Commands ').info

    @commands.command(name='add_innvictus_rs_link')
    async def add_to_innvitcus_restock_list(self, ctx, *, link):
        if await self.db.link_in_inn_rsl(link):
            await ctx.send('Link is already being monitored!')
            return
        await self.db.add_inn_rs_list(link)
        await ctx.send('Link added to restock monitor list!')

    @commands.command(name='remove_innvictus_rs_link')
    async def remove_inn_rs_list(self, ctx, *, link):
        if not await self.db.link_in_inn_rsl(link):
            await ctx.send('Link is not being monitored by the bot!')
            return

        await self.db.remove_inn_rs_list(link)
        await ctx.send('Link removed from restock monitor!')

    @commands.command(name='list_innvictus_rs_links')
    async def list_innvictus_rs_link(self, ctx):
        rs_list = await self.db.get_inn_rs_list()
        message = '**Links List**'
        for link in rs_list:
            message = f'{message}\n{link}'

        await ctx.send(message)


def setup(bot):
    bot.add_cog(InnvictusCommands(bot))
    print('[+] Innvictus Commands has been loaded!')
