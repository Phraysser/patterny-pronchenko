import copy
import time
from level_loader import LevelLoader


class LevelLoaderProxy:
    def __init__(self):
        self._real_loader = None
        self._cache = {}
        self._load_count = 0
        self._cache_hits = 0
        self._total_load_time = 0.0

    def _get_real_loader(self):
        if self._real_loader is None:
            self._real_loader = LevelLoader()
        return self._real_loader

    def load_level(self, file_path):
        if file_path in self._cache:
            self._cache_hits += 1
            return copy.deepcopy(self._cache[file_path])

        loader = self._get_real_loader()

        start_time = time.time()
        level_data = loader.load_level(file_path)
        load_time = time.time() - start_time

        self._total_load_time += load_time
        self._load_count += 1

        self._cache[file_path] = level_data

        return copy.deepcopy(level_data)

    def get_cache_size(self):
        return len(self._cache)

    def get_cache_keys(self):
        return list(self._cache.keys())

    def clear_cache(self):
        self._cache.clear()

    def get_stats(self):
        return {
            'load_count': self._load_count,
            'cache_hits': self._cache_hits,
            'cache_size': len(self._cache),
            'total_load_time': self._total_load_time,
            'cached_levels': list(self._cache.keys())
        }

    def is_cached(self, file_path):
        return file_path in self._cache