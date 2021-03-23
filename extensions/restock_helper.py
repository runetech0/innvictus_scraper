import asyncio
from multiprocessing import Queue
from extensions.db import DB


class RestockHelper:
    def __init__(self, invictus_queue: Queue):
        self.invictus_queue = invictus_queue
        self.loop = asyncio.new_event_loop()
        self.db = DB()

    def start(self):
        self.loop.run_until_complete(self.main())

    async def main(self):
        while True:
            if self.invictus_queue.empty():
                print('Refilling ..')
                restock_list = await self.db.get_inn_rs_list()
                # restock_list = [
                #     'https://www.innvictus.com/hombres/basket/ropa/nike/playera-jordan-x-a-ma-maniere/p/000000000000204985',
                #     'https://www.innvictus.com/hombres/basket/tenis/jordan/tenis-air-jordan-6-retro-og-carmine-2021/p/000000000000188146'
                # ]
                for link in restock_list:
                    self.invictus_queue.put(link)
            await asyncio.sleep(5)
