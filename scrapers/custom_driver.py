import os
import zipfile
import time
import json
from random import randrange
from selenium import webdriver


def get_proxy():
    proxies_file = 'proxies.json'
    with open(proxies_file) as f:
        config = json.load(f)
    proxies = config.get("PROXIES")
    index = randrange(len(proxies))
    proxy = proxies[index]
    ip = proxy.split(':')[0]
    port = int(proxy.split(':')[1])
    username = config.get("USERNAME")
    password = config.get("PASSWORD")
    return ip, port, username, password


def get_user_agent():
    agents_file = 'user_agents.json'
    with open(agents_file) as f:
        config = json.load(f)
    agents = config.get("USER_AGENTS")
    rand_index = randrange(len(agents))
    return agents[rand_index]


def get_chromedriver(use_proxy=False, chrome_options=None, executable_path=None):
    PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = get_proxy()
    user_agent = get_user_agent()

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
    # path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument('--headless')
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    driver = webdriver.Chrome(executable_path=executable_path,
                              chrome_options=chrome_options)
    return driver


def main():
    # driver = get_chromedriver(use_proxy=True)
    # # driver.get('https://www.google.com/search?q=my+ip+address')
    # driver.get('https://httpbin.org/ip')
    # time.sleep(30)
    print(get_proxy())


if __name__ == '__main__':
    main()
