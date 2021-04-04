import asyncio
from multiprocessing import Queue
from extensions.db import DB
import psutil
import os


class RestockHelper:
    def __init__(self, invictus_queue: Queue):
        self.invictus_queue = invictus_queue
        self.loop = asyncio.new_event_loop()
        self.db = DB()

    def start(self):
        self.loop.run_until_complete(self.main())

    async def main(self):
        while True:
            # await self.uasge_control()
            if self.invictus_queue.empty():
                restock_list = await self.db.get_inn_rs_list()
                for link in restock_list:
                    self.invictus_queue.put(link)
            await asyncio.sleep(5)

    async def uasge_control(self):
        if int(psutil.virtual_memory()[2]) >= 80:
            os.system('pkill chrom')
            await asyncio.sleep(5)
        if int(psutil.cpu_percent()) >= 80:
            os.system('pkill chrom')
            await asyncio.sleep(5)
