from selenium import webdriver
from selenium.common import exceptions
import asyncio
import json
from models.cache import ListCache
import logging
from models.products import JetStoreProduct


class JetStoreScraper:
    def __init__(self, queue):
        self.config = json.load(open('config.json', 'r'))
        self.queue = queue
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('start-maximized')
        self.options.add_argument('disable-infobars')
        # self.options.add_argument('--headless')
        webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.driver = webdriver.Chrome(
            executable_path=webdriver_path, options=self.options)
        self.loop = asyncio.new_event_loop()
        self.target_url = 'https://drops.jetstore.com.mx/'
        self.log = logging.getLogger('JetStore').info
        self.itter_time = 120

    def start(self):
        self.cache = ListCache('jetstore')
        self.loop.run_until_complete(self.main())

    async def main(self):
        await self.create_cache()
        while True:
            links = await self.get_all_prod_link()
            for link in links:
                if self.cache.has_item(link):
                    continue
                prod = await self.get_prod_details(link)
                self.queue.put(prod)
            await asyncio.sleep(self.itter_time)

    async def create_cache(self):
        self.log('[+] Creating cache for jetstore')
        links = await self.get_all_prod_link()
        self.cache.replace_cache(links)
        self.log('[+] Cache Created for jetstore')

    async def get_all_prod_link(self):
        self.driver.get(self.target_url)
        elements = self.driver.find_elements_by_class_name(
            'entry-content')
        links = []
        for element in elements:
            try:
                link = element.find_element_by_class_name(
                    'wp-block-button__link').get_attribute('href')
                links.append(link)
            except exceptions.NoSuchElementException:
                continue
        return links

    async def get_prod_details(self, link):
        self.driver.get(link)
        prod = JetStoreProduct()
        prod.price = self.driver.find_element_by_class_name(
            'woocommerce-Price-amount').text.replace('$', '').replace(',', '')
        prod.name = self.driver.find_element_by_class_name('entry-title').text
        sizes = self.driver.find_elements_by_class_name('swatch')
        for size in sizes:
            text = size.get_attribute('data-value').upper()
            prod.sizes.append(text)
        prod.img_link = self.driver.find_element_by_class_name(
            'zoomImg').get_attribute('src')
        prod.link = link
        return prod
