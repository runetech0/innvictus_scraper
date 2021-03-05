from selenium import webdriver
import asyncio
import json
from models.cache import ListCache
from models.products import LiverPoolProduct
from configs import global_vars
import logging


class LiverPoolNewProdsScraper:
    def __init__(self, queue):
        self.config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))
        self.queue = queue
        self.cache = ListCache('LiverPoolCache')
        self.log = logging.getLogger(' LiverpoolMonitor ').info
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.loop = asyncio.new_event_loop()
        self.URLs = [
            'https://www.liverpool.com.mx/tienda/zapatos/catst1105210',
            'https://www.liverpool.com.mx/tienda/zapatos/catst1010801',
            'https://www.liverpool.com.mx/tienda/zapatos/catst1011086'
        ]

    def start(self):
        self.loop.run_until_complete(self.main())
        # asyncio.run(self.main())

    async def main(self):
        await self.create_cache()
        while True:
            all_links = await self.get_all_prod_links()
            self.log(f'[+] Got {len(all_links)} prod links!')
            for link in all_links:
                if not self.cache.in_cache(link):
                    prod = await self.get_prod_details(link)
                    self.queue.put(prod)

    async def create_cache(self):
        self.log('[+] Creating cache ..')
        links = await self.get_all_prod_links()
        self.cache.replace_cache(links)
        self.log('[+] Created cache for prods')

    async def get_all_prod_links(self):
        self.log('[+] Getting all the prod links ...')
        self.driver = webdriver.Chrome(
            executable_path=self.webdriver_path, options=self.options)
        self.driver.implicitly_wait(10)
        links = []
        for url in self.URLs:
            self.driver.get(url)
            prods_list = self.driver.find_elements_by_xpath(
                '//li[@class="m-product__card card-masonry"]')
            for prod in prods_list:
                link = prod.find_element_by_tag_name('a').get_attribute('href')
                links.append(link)
        self.driver.quit()
        return links

    async def get_prod_details(self, link):
        self.driver = webdriver.Chrome(
            executable_path=self.webdriver_path, options=self.options)
        self.driver.implicitly_wait(10)
        self.driver.get(link)
        prod = LiverPoolProduct()
        prod.name = self.driver.find_element_by_xpath(
            '//h1[@class="a-product__information--title"]').text
        prod.link = link
        out_of_stock_sizes = self.driver.find_elements_by_xpath(
            '//button[@class="a-btn a-btn--actionpdp -disabled"]')
        for size in out_of_stock_sizes:
            prod.out_of_stock_sizes.append(size.text)
        in_stock_sizes = self.driver.find_elements_by_xpath(
            '//button[@class="a-btn a-btn--actionpdp"]')
        for size in in_stock_sizes:
            prod.in_stock_sizes.append(size.text)
        prod.img_link = self.driver.find_element_by_xpath(
            '//img[@id="image-real"]').get_attribute('src')
        prod.color = self.driver.find_element_by_xpath(
            '//p[@class="a-product__paragraphColor m-0 mt-2 mb-1"]').text.split(':')[-1].strip()
        prod.price = self.driver.find_element_by_xpath(
            '//p[@class="a-product__paragraphDiscountPrice m-0 d-inline "]').text.split('\n')[0].replace(',', '').replace('$', '')

        self.driver.quit()
        return prod
