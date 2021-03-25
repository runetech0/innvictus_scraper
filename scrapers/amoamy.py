from selenium import webdriver
import asyncio
import json
from models.cache import ListCache


class InvictusScraper:
    def __init__(self, queue):
        self.config = json.load(open('config.json', 'r'))
        self.queue = queue
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.driver = webdriver.Chrome(
            executable_path=webdriver_path, options=options)
        self.loop = asyncio.new_event_loop()
        self.target_url = 'https://launches.amoamy.com/'

    def start(self):
        self.cache = ListCache('amoamy')
        self.loop.run_until_complete(self.main())

    async def main(self):
        while True:
            pass
