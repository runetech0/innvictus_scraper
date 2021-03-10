from pymongo import MongoClient


class ListCache:
    def __init__(self, cache_name):
        self.cache_name = cache_name.replace(' ', '')
        self._client = MongoClient()
        self._db = self._client.cache_db
        self.cache = self._db.cache_col
        self._doc_id = cache_name
        self._cache_id = '_cache_id'
        self.list_key = 'CacheList'

    def _create_if_not(self):
        doc = self.cache.find_one({self._doc_id: self._doc_id})
        if not doc:
            self.cache.insert_one({
                self.list_key: [],
                self._cache_id: self._cache_id
            })

    def add_item(self, new_item):
        self._create_if_not()
        self.cache.find_one_and_update({
            self._cache_id: self._cache_id
        }, {
            '$push': {self.list_key: new_item}
        })

    def has_item(self, item):
        self._create_if_not()
        res = self.cache.find_one({self._cache_id: self._cache_id})
        return item in list(res[self.list_key])

    def remove_item(self, item):
        self._create_if_not()
        self.cache.find_one_and_update({
            self._cache_id: self._cache_id
        }, {
            '$pull': {self.list_key: item}
        })

    def get_all_items(self):
        self._create_if_not()
        res = self.cache.find_one({self._cache_id: self._cache_id})
        return res[self.list_key]

    def invalidate_cache(self):
        self.cache.update_one({
            self._cache_id: self._cache_id
        }, {
            '$set': {
                self.list_key: [],
            }
        })

    def replace_cache(self, new_cache):
        self._create_if_not()
        self.cache.update_one({
            self._cache_id: self._cache_id
        }, {
            '$set': {
                self.list_key: new_cache,
            }
        })


if __name__ == '__main__':
    cache = ListCache('cache')
    link = 'https://www.innvictus.com/p/0000000000000188152'
    cache.add_item(link)
    print(cache.has_item(link))
