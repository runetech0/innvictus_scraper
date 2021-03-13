from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import json
import logging
from bs4 import BeautifulSoup
from models.products import TafProduct, TafSize
from configs import global_vars
from models.cache import ListCache


class TafNewProdsScraper:
    def __init__(self, queue):
        self.config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))
        self.queue = queue
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('start-maximized')
        self.options.add_argument('disable-infobars')
        self.webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.driver = None
        self.URL = 'https://www.taf.com.mx/jordan'
        self.log = logging.getLogger(' TafNewProducts ').info
        self.itter_time = 120

    def start(self):
        self.cache = ListCache('TafNewScraper')
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.main())

    async def start_driver(self):
        self.quit_browser()
        self.driver = webdriver.Chrome(
            executable_path=self.webdriver_path, options=self.options)
        self.driver.implicitly_wait(10)

    async def main(self):
        self.log('[+] Taf New Prods Scraper is up!')
        await self.create_cache()
        while True:
            try:
                links = await self.get_all_prods_links()
                self.log(f'[+] Got {len(links)} prod links')
                for link in links:
                    if not self.cache.has_item(link):
                        prod_details = await self.get_prod_details(link)
                        self.queue.put(prod_details)
                        self.cache.add_item(link)
                await asyncio.sleep(self.itter_time)
            except Exception as e:
                self.log(e)
                await asyncio.sleep(3)

    async def create_cache(self):
        self.log('[+] Creating cache ..')
        links = await self.get_all_prods_links()
        self.cache.replace_cache(links)
        self.log('[+] Created cache for prods')

    async def get_all_prods_links(self):
        await self.start_driver()
        self.driver.get(self.URL)
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'product-item'))
            )
        except Exception as e:
            self.log(e)
        prods = self.driver.find_elements_by_class_name('product-item')
        links = []
        for prod in prods:
            prod_link = prod.find_element_by_tag_name(
                'a').get_attribute('href')
            links.append(prod_link)
        return links

    async def get_prod_details(self, link):
        await self.start_driver()
        self.driver.get(link)
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'skuReference'))
            )
        except Exception as e:
            self.log(e)
        info_html = self.driver.find_element_by_class_name(
            'product-detail').get_attribute('innerHTML')
        soup = BeautifulSoup(info_html, 'html.parser')
        p = TafProduct()
        p.title = soup.select_one('.product-detail__name').text
        p.link = link
        p.price = soup.select_one(
            '.price-best-price').text.split(':')[-1].strip()
        p.model = soup.select_one(
            '.product-detail__model').text.split(':')[-1].strip()
        p.img_link = self.driver.find_element_by_class_name(
            'product-detail__zoom-wrapper').find_element_by_tag_name('a').get_attribute('href')
        sku_list = self.driver.find_element_by_class_name('skuList')
        all_skus = sku_list.find_elements_by_tag_name('label')
        for sku in all_skus:
            size = TafSize()
            size.size_number = sku.text
            classes = sku.get_attribute('class')
            if 'item_unavailable' in classes:
                p.out_of_stock_sizes.append(size)
                continue
            sku.click()
            size.atc = self.driver.find_element_by_class_name(
                'buy-in-page-button').get_attribute('href').replace('redirect=false', 'redirect=true')
            p.in_stock_sizes.append(size)
        return p

    def quit_browser(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None


class TafKeywordMonitor(TafNewProdsScraper):
    def __init__(self, queue, keywords):
        super().__init__(queue)
        self.keywords = keywords
        self.base_URL = f'https://www.taf.com.mx'
        self.log = logging.getLogger(' TafKeywordMon ').info
        self.itter_time = 120

    async def main(self):
        self.cache = ListCache(f'TafKeyWordsMonitor')
        self.log(f'[+] Started Taf keyword monitor')
        await self.create_cache()
        while True:
            try:
                for keyword in self.keywords:
                    target_link = f'{self.base_URL}/{keyword}'
                    if not await self.has_prods(target_link):
                        await asyncio.sleep(3)
                        continue
                    self.URL = target_link
                    prod_links = await self.get_all_prods_links()
                    self.log(f'[+] Got {len(prod_links)} prod links')
                    for link in prod_links:
                        if not self.cache.has_item(link):
                            prod_details = await self.get_prod_details(link)
                            self.queue.put(prod_details)
                            self.cache.add_item(link)
                await asyncio.sleep(self.itter_time)
            except Exception as e:
                self.log(e)
                await asyncio.sleep(3)

    async def create_cache(self):
        self.log('[+] Creating cache...')
        await self.start_driver()
        for keyword in self.keywords:
            target_link = f'{self.base_URL}/{keyword}'
            if not await self.has_prods(target_link):
                continue
            self.URL = target_link
            prod_links = await self.get_all_prods_links()
            for link in prod_links:
                self.cache.add_item(link)
        self.log('[+] Cache created!')

    async def has_prods(self, link):
        await self.start_driver()
        self.driver.get(link)
        try:
            self.driver.find_element_by_class_name('head-tittle')
            return False
        except exceptions.NoSuchElementException:
            return True
