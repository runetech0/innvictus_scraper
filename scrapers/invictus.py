from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import json
from models.products import InvictusProduct
from scrapers.custom_driver import get_chromedriver


class InvictusNewProductsScraper:
    def __init__(self, queue):
        self.config = json.load(open('config.json', 'r'))
        self.queue = queue
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
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
        await self.create_cache()
        while True:
            all_prods = await self.get_all_prods()
            print(f'[+] Got {len(all_prods)} products')
            if all_prods is None:
                await asyncio.sleep(3)
                continue
            for p in all_prods:
                if p.prod_link not in self.cache:
                    self.queue.put(p)
            await asyncio.sleep(self.itter_time)

    async def create_cache(self):
        all_prods = await self.get_all_prods()
        for p in all_prods:
            self.cache.append(p.prod_link)

    async def get_all_prods(self):
        to_return = []
        for link in self.target_links:
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
                    print(
                        'Got exception in > invictus_scraper > get_all_prods > waiting for prods')
                    print(e)
                    print(f'Could not load page : {link}')
                    return []

            prod_list = prods.find_elements_by_class_name('is-pw__product')
            for prod in prod_list:
                p = InvictusProduct()
                p.prod_link = prod.find_element_by_class_name(
                    'js-gtm-product-click').get_attribute('href')
                p.prod_img_link = prod.find_element_by_tag_name(
                    'img').get_attribute('src')
                p.prod_name = prod.find_element_by_class_name(
                    'is-gridwallCard__item__name').text

                prod_gender = prod.find_element_by_css_selector(
                    'span.is-gridwallCard__item__gender').text
                if prod_gender == 'HOMBRES':
                    p.prod_gender = 'MEN'
                elif prod_gender == 'MUJERES':
                    p.prod_gender = 'WOMEN'
                p.prod_price = prod.find_element_by_class_name(
                    'price-int').text
                to_return.append(p)
            self.driver.quit()
        return to_return
