import os
import shelve
import enum


class DictCache:
    def __init__(self, cache_name):
        self.db_dir = './Cache'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)
        self.db = self.db_dir + f'/cache_{cache_name}'

    def cache_key_exists(self, key):
        with shelve.open(self.db) as f:
            if key in f.keys():
                return True
            return False

    def cache_exists(self, value):
        with shelve.open(self.db) as f:
            if value in f.values():
                return True
            return False

    def get_cache(self, key):
        with shelve.open(self.db) as f:
            return f.get(key, default=None)

    def cache_keys(self):
        with shelve.open(self.db) as f:
            return list(f.keys())

    def cache_values(self):
        with shelve.open(self.db) as f:
            return list(f.values())

    def add_cache(self, key, value):
        with shelve.open(self.db) as f:
            f[key] = value

    def remove_cache(self, key):
        with shelve.open(self.db) as f:
            f.pop(key, None)

    def replace_cache(self, new_cache: dict):
        with shelve.open(self.db) as f:
            for k in f.keys():
                f.pop(k, None)
            f.update(new_cache)

    def update_cache(self, update):
        with shelve.open(self.db) as f:
            f.update(update)


class ListCache:
    def __init__(self, cache_name, cache_size=200,
                 control_size=False):
        self.db_dir = './Cache'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)
        self.db = self.db_dir + f'/cache_{cache_name}'
        self.cache_name = cache_name
        self.cache_size = cache_size
        self.control_size = control_size
        if not os.path.exists(self.db):
            with shelve.open(self.db) as f:
                f[self.cache_name] = []

    def in_cache(self, item):
        with shelve.open(self.db) as f:
            if item in f.get(self.cache_name):
                return True
            return False

    def add_cache(self, item):
        with shelve.open(self.db) as f:
            f.get(self.cache_name).append(item)
            self.vaildate_size()

    def remove_cache(self, item):
        with shelve.open(self.db) as f:
            f.get(self.cache_name).remove(item)

    def replace_cache(self, new_cache: list):
        with shelve.open(self.db) as f:
            f[self.cache_name] = new_cache
            self.vaildate_size()

    def vaildate_size(self):
        if self.control_size:
            with shelve.open(self.db) as f:
                f[self.cache_name] = f[self.cache_name][-self.cache_size:]
