from selenium import webdriver
import asyncio
import json


class AgentsScraper:
    def __init__(self):
        self.config = json.load(open('config.json', 'r'))
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.driver = webdriver.Chrome(
            executable_path=webdriver_path, options=options)
        self.loop = asyncio.new_event_loop()
        self.target_link = 'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/mac-os-x/'
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/windows/'
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/linux/'

    def start(self):
        self.loop.run_until_complete(self.main())

    async def main(self):
        all_agents = []
        config = {}
        for i in range(11):
            url = f'{self.target_link}{i+1}'
            print(f'Target Link : {url}')
            agents = await self.get_all_agents(url)
            all_agents.extend(agents)
            await asyncio.sleep(10)

        config['PROXIES'] = all_agents
        with open('mac_agents.json', 'w') as f:
            json.dump(config, f, indent=4)
        print("Done!")

    async def get_all_agents(self, url):
        self.driver.get(url)
        table = self.driver.find_element_by_tag_name('tbody')
        rows = table.find_elements_by_tag_name('tr')
        agents = []
        for row in rows:
            agent = row.find_element_by_tag_name('a').text
            agents.append(agent)
        return agents


if __name__ == '__main__':
    ags = AgentsScraper()
    ags.start()
