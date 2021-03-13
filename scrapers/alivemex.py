from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import json
from models.cache import ListCache
from models.products import AliveMexProduct
import logging
from configs.global_vars import MAIN_CONFIG_FILE_LOCATION


class AliveMexNewProdScraper:
    def __init__(self, queue):
        self.config = json.load(open(MAIN_CONFIG_FILE_LOCATION))
        self.queue = queue
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('start-maximized')
        self.options.add_argument('disable-infobars')
        self.webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.loop = asyncio.new_event_loop()
        self.URL = 'https://www.alivemexico.com/'
        self.log = logging.getLogger('AliveMex').info
        self.itter_time = 120

    def start(self):
        self.cache = ListCache('AliveMexNewProdScraper')
        self.loop.run_until_complete(self.main())

    async def start_driver(self):
        self.quit_browser()
        self.driver = webdriver.Chrome(
            executable_path=self.webdriver_path, options=self.options)
        self.driver.implicitly_wait(10)

    async def main(self):
        self.log('[+] AliveMex Scraper is up!')
        await self.create_cache()
        while True:
            self.log('[+] Checking for new prods')
            try:
                prod_links = await self.get_all_prod_links()
                self.log(f'[+] Got {len(prod_links)} prod links')
                for link in prod_links:
                    if not self.cache.has_item(link):
                        prod_details = await self.get_prod_details(link)
                        self.queue.put(prod_details)
                        self.cache.add_item(link)
                await asyncio.sleep(self.itter_time)
            except Exception as e:
                self.log(e)
                self.quit_browser()
                await asyncio.sleep(3)

    async def create_cache(self):
        self.log('[+] Creating cache for the prod links')
        prod_links = await self.get_all_prod_links()
        self.cache.replace_cache(prod_links)
        self.log('[+] Cache created for the prod links')

    async def get_all_prod_links(self):
        self.log('[+] Getting all the prod links ...')
        await self.start_driver()
        self.driver.get(self.URL)
        target_class = 'product-miniature'
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, target_class))
            )
        except Exception as e:
            self.log(e)
        prods = self.driver.find_elements_by_xpath(
            '//article[@class="product-miniature js-product-miniature"]')
        prod_links = list()
        for prod in prods:
            prod_link = prod.find_element_by_tag_name(
                'a').get_attribute('href')
            prod_links.append(prod_link)

        self.quit_browser()
        return prod_links

    async def get_prod_details(self, link):
        await self.start_driver()
        self.driver.get(link)
        details = AliveMexProduct()
        details.link = link
        details.name = self.driver.find_element_by_class_name(
            'namne_details').text
        details.img_link = self.driver.find_element_by_xpath(
            '//img[@class="js-qv-product-cover"]').get_attribute('src')
        details.price = self.driver.find_element_by_class_name(
            'current-price').text.replace('$', '').replace(',', '')

        self.quit_browser()
        return details

    def quit_browser(self):
        if self.driver is not None:
            self.driver.quit()
            del self.driver
            self.driver = None
