from pymongo import MongoClient

import logging


class DB:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.scraper_db
        self.innvictus_data = self.db.innvictus_data
        self.innvictus_data_title = 'Innvictus'
        self.log = logging.getLogger(' Database ').info

    async def link_in_inn_rsl(self, link):
        doc = self.innvictus_data.find_one(
            {'title': self.innvictus_data_title})
        if not doc:
            return False
        if link in doc['rs_list']:
            return True
        return False

    async def get_inn_rs_list(self):
        doc = self.innvictus_data.find_one(
            {'title': self.innvictus_data_title})
        return doc['rs_list'] if doc else []

    async def add_inn_rs_list(self, new_link):
        doc = self.innvictus_data.find_one(
            {'title': self.innvictus_data_title})
        if doc:
            # Create new doc because it does not exist already
            self.innvictus_data.find_one_and_update({
                'title': self.innvictus_data_title
            }, {
                '$push': {'rs_list': new_link}
            })
            return
        # Create the new document.
        self.innvictus_data.insert_one({
            'title': self.innvictus_data_title,
            'rs_list': [new_link]
        })

    async def remove_inn_rs_list(self, link_to_remove):
        self.innvictus_data.update_one({
            'title': self.innvictus_data_title
        }, {
            '$pull': {'rs_list': link_to_remove}
        })
