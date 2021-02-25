from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import json
from models.products import InvictusProduct
from scrapers.custom_driver import get_chromedriver
from pyvirtualdisplay import Display
from extensions.db import DB
from bs4 import BeautifulSoup
from queue import Queue


class InvictusNewProductsScraper:
    def __init__(self, queue):
        self.config = json.load(open('config.json', 'r'))
        self.queue = queue
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        self.options = webdriver.ChromeOptions()
        self.webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.loop = asyncio.new_event_loop()
        self.cache = []
        self.itter_time = 300
        self.target_links = [
            'https://www.innvictus.com/mujeres/c/mujeres',
            'https://www.innvictus.com/jordan/c/jordan',
            'https://www.innvictus.com/ninos/c/ninos',
            'https://www.innvictus.com/hombres/c/hombres'
        ]

    def start(self):
        self.loop.run_until_complete(self.main())

    async def main(self):
        print('[+] Invictus monitor started!')
        # await self.create_cache()
        while True:
            all_prods = await self.get_all_prod_links()
            print(f'[+] Got {len(all_prods)} products')
            if all_prods is None:
                await asyncio.sleep(3)
                continue
            for link in all_prods:
                if link not in self.cache:
                    prod = await self.get_prod_details(link)
                    self.queue.put(prod)
            await asyncio.sleep(self.itter_time)

    async def create_cache(self):
        print('[+] Creating cache for the products ..')
        all_prods = await self.get_all_prod_links()
        for link in all_prods:
            self.cache.append(link)
        print('[+] Created cache for the products!')

    async def get_all_prod_links(self):
        to_return = []
        for link in self.target_links:
            print(f'[+] Getting products from {link}')
            tries = 0
            while True:
                self.driver = get_chromedriver(
                    chrome_options=self.options, use_proxy=True,
                    executable_path=self.webdriver_path)
                self.driver.get(link)
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
                    print(
                        'Got exception in > invictus_scraper > get_all_prods > waiting for prods')
                    print(f'[-] Could not load page in try {tries} : {link}')
                    print(e)

            prod_list = prods.find_elements_by_class_name('is-pw__product')
            for prod in prod_list:
                prod_link = prod.find_element_by_class_name(
                    'js-gtm-product-click').get_attribute('href')
                to_return.append(prod_link)
            self.driver.quit()
        return to_return

    async def load_prod_page(self, link):
        self.driver = get_chromedriver(
            chrome_options=self.options, use_proxy=True,
            executable_path=self.webdriver_path)
        self.driver.get(link)

    async def get_prod_details(self, link):
        await self.load_prod_page(link)
        prod = InvictusProduct()
        prod.prod_name = self.driver.find_element_by_id('productName').text
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
        sizes = size_list.find_elements_by_tag_name('li')
        for size in sizes:
            size_number = size.text
            classes = size.get_attribute('class')
            oos_class_name = 'product-size__option--no-stock"'
            if oos_class_name in classes:
                prod.out_of_stock_sizes.append(size_number)
                continue
            prod.in_stock_sizes.append(size_number)
        self.driver.quit()
        return prod


class InvictusRestockMonitor(InvictusNewProductsScraper):
    def __init__(self, queue):
        InvictusNewProductsScraper.__init__(self, queue)
        self.db = DB()

    def start(self):
        self.loop.run_until_complete(self.main())

    async def main(self):
        while True:
            restock_list = self.db.get_inn_rs_list()
            for link in restock_list:
                if await self.prod_in_stock(link):
                    prod = await self.get_prod_details(link)
                    self.queue.put(prod)

    async def prod_in_stock(self, link):
        in_stock = self.driver.find_element_by_id(
            'js-stock-notification-container').text
        if in_stock == '':
            return False
        return True


if __name__ == '__main__':
    InvictusRestockMonitor(Queue())
