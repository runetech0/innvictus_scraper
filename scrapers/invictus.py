from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import json
from models.products import InvictusProduct
from scrapers.custom_driver import get_chromedriver, get_proxy
from pyvirtualdisplay import Display
from extensions.db import DB
from bs4 import BeautifulSoup
from queue import Queue
import configs.global_vars as global_vars
import logging
from models.cache import ListCache
import multiprocessing


class InvictusNewProductsScraper:
    def __init__(self, queue):
        self.config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))
        self.keywords_config = json.load(open(
            global_vars.FILTRATION_KEYWORDS_FILE_LOCATION))
        self.fitration_keywords = list(self.keywords_config.get(
            "INNVICTUS_KEYWORDS"))
        self.queue = queue
        self.driver = None
        self.options = webdriver.ChromeOptions()
        self.webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.loop = asyncio.new_event_loop()
        self.log = logging.getLogger(' InnvicutsNewProdMon ').info
        self.itter_time = 10
        self.target_links = [
            'https://www.innvictus.com/mujeres/c/mujeres',
            'https://www.innvictus.com/jordan/c/jordan',
            'https://www.innvictus.com/ninos/c/ninos',
            'https://www.innvictus.com/hombres/c/hombres'
        ]

    def start(self):
        self.cache = ListCache('InvictusScraper')
        self.loop.run_until_complete(self.main())

    async def main(self):
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        self.log('[+] Invictus monitor started!')
        await self.create_cache()
        while True:
            self.log('[+] Invictus New Prod Monitor Checking for new prods')
            try:
                all_prods = await self.get_all_prod_links()
                self.log(f'[+] Got {len(all_prods)} products')
                if all_prods is None:
                    await asyncio.sleep(3)
                    continue
                for link in all_prods:
                    if not self.cache.has_item(link):
                        prod = await self.get_prod_details(link)
                        self.cache.add_item(link)
                        for keyword in self.fitration_keywords:
                            if keyword in prod.prod_name.lower():
                                self.queue.put(prod)
                                break
                await asyncio.sleep(self.itter_time)
            except Exception as e:
                self.log('Blind exception in invictus new prod')
                self.log(e)
                await asyncio.sleep(3)

    async def create_cache(self):
        self.log('[+] Creating cache for the products ..')
        all_prods = await self.get_all_prod_links()
        self.cache.replace_cache(all_prods)
        self.log('[+] Created cache for the products!')

    async def get_all_prod_links(self) -> list:
        to_return = []
        for link in self.target_links:
            tries = 0
            while True:
                await self.load_prod_page(link)
                try:
                    prods = WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, 'is-pw__products-list'))
                    )
                    break
                except Exception as e:
                    tries += 1
                    if tries >= 5:
                        raise e
                    self.log(
                        f'[-] Could not load page in try {tries} : {link}')
                    self.log(e)

            prod_list = prods.find_elements_by_class_name('is-pw__product')
            for prod in prod_list:
                prod_link = prod.find_element_by_class_name(
                    'js-gtm-product-click').get_attribute('href')
                to_return.append(prod_link)
        return to_return

    async def load_prod_page(self, link):
        ip, port, username, password = get_proxy()
        options = {
            'proxy': {
                'http': f'http://{username}:{password}@{ip}:{port}',
                'https': f'https://{username}:{password}@{ip}:{port}',
                'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
            }
        }
        self.quit_browser()
        self.driver = webdriver.Chrome(
            chrome_options=self.options, seleniumwire_options=options, executable_path=self.webdriver_path)
        self.driver.implicitly_wait(10)
        self.driver.get(link)

    async def get_prod_details(self, link):
        while True:
            try:
                await self.load_prod_page(link)
                break
            except Exception as e:
                self.log('[-] Failed to load driver')
                self.log(e)
                continue
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(
                    (By.ID, 'productName'))
            )
        except Exception as e:
            self.log(e)
            return await self.get_prod_details(link)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        prod = InvictusProduct()
        prod.prod_name = soup.select('#productName')[0].text
        prod.prod_link = link
        img_slider = self.driver.find_element_by_class_name('slider-main')
        prod.prod_img_link = img_slider.find_element_by_tag_name(
            'img').get_attribute('src')
        prod.prod_model = self.driver.find_element_by_id('productModel').text
        size_list = self.driver.find_element_by_class_name(
            'product-size__list')
        price_html = self.driver.find_element_by_id(
            'currentPrice').get_attribute('innerHTML')
        bs = BeautifulSoup(price_html, 'html.parser')
        prod.prod_price = bs.select('#pdpCurrent_wholePart')[
            0].text.replace(',', '').replace('.', '')
        sizes = size_list.find_elements_by_tag_name('a')
        for size in sizes:
            size_number = size.text
            classes = size.get_attribute('class')
            oos_class_name = 'product-size__option--no-stock'
            if oos_class_name in classes:
                prod.out_of_stock_sizes.append(size_number)
                continue
            prod.in_stock_sizes.append(size_number)
        return prod

    def quit_browser(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None


class InvictusRestockMonitor(InvictusNewProductsScraper):
    def __init__(self, queue, restock_queue):
        super().__init__(queue)
        self.restock_queue = restock_queue
        self.log = logging.getLogger(' InvictusRestockMonitor ').info

    def start(self):
        self.loop.run_until_complete(self.main())
        self.itter_time = 1

    async def main(self):
        self.db = DB()
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        self.log('[+] Restock monitor is ready!')
        # self.log('[+] Invictus Restock Checking for restock')
        while True:
            try:
                while self.restock_queue.empty():
                    await asyncio.sleep(1)
                link = self.restock_queue.get()
                if await self.prod_in_stock(link):
                    self.log(f'[+] Got restock : {link}')
                    prod = await self.get_prod_details(link)
                    self.queue.put(prod)
                    await self.db.remove_inn_rs_list(link)
                    await asyncio.sleep(1)
                await asyncio.sleep(self.itter_time)
            except Exception as e:
                self.log('Blind exception in invictus restock')
                self.log(e)

    async def prod_in_stock(self, link):
        await self.load_prod_page(link)
        target_id = 'js-stock-notification-container'
        try:
            in_stock = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.ID, target_id))
            )
            in_stock = self.driver.find_element_by_id(
                target_id)
            classes = in_stock.get_attribute('class')
            if 'hidden' in classes:
                return True
            else:
                # self.log(f'{link} is out of stock 1')
                return False
        except exceptions.NoSuchElementException:
            try:
                self.driver.find_elements_by_class_name('product-slider')
                self.log('In stock')
                return True
            except exceptions.NoSuchElementException:
                # self.log(f'{link} is out of stock 2')
                return False
        except exceptions.TimeoutException:
            # self.log(f'{link} is out of stock 3')
            return False
