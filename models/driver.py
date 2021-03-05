from selenium import webdriver
import json
import configs.global_vars as global_vars
from threading import Lock
import asyncio


class Driver:
    def __init__(self):
        self.config = json.load(open(global_vars.MAIN_CONFIG_FILE_LOCATION))
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('start-maximized')
        self.options.add_argument('disable-infobars')
        self.webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.lock = Lock()

    async def get_driver_when_when_available(self):
        if not hasattr(self, 'driver'):
            self.driver = webdriver.Chrome(
                executable_path=self.webdriver_path, options=self.options)
        while self.lock.locked():
            await asyncio.sleep(0.2)
        self.lock.acquire()
        return self.driver
