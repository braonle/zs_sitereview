# pylint: disable=R0913,R0903
"""
    Implement caching for IP lookup
"""

import json.decoder
import os
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

DEFAULT_CACHE_FILE = "zsr_cache.json"
CACHE_TIMEOUT_DAYS = 14


class JsonFields:
    """
        Class, describing cache JSON fields
    """
    THREAT = "threatname"
    CATEGORIES = "categories"
    CREATED = "created"


class ZSRCache():
    """
        Implements file-based caching to avoid redundant lookups by Site Review
    """
    # { CIDR : { attr: value } }
    cache: dict[str, dict[str, str | list[str]]] = {}

    def __init__(self, cache_file: str = DEFAULT_CACHE_FILE):
        """
            Load existing cache file, if present
        """
        if os.path.isfile(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as cachedata:
                    self.cache = json.load(cachedata)

            except json.decoder.JSONDecodeError as e:
                logging.error("Error with loading %s - Ensure this file is not corrupted\n%s",
                              cache_file,
                              str(e))
                return

            stale_keys = []
            now = datetime.now()
            time_window = relativedelta(days=+CACHE_TIMEOUT_DAYS)
            for key, value in self.cache.items():
                str_date = value.get(JsonFields.CREATED)
                if str_date is None:
                    stale_keys.append(key)
                    continue

                expiry_date = datetime.fromisoformat(str_date) + time_window
                if expiry_date <= now:
                    stale_keys.append(key)

            for key in stale_keys:
                del self.cache[key]

    def save_cache(self, cache_file: str = DEFAULT_CACHE_FILE) -> None:
        """
            Persist cache to disk

            :param str cache_file: path to cache file; optional
        """
        with open(cache_file, "w", encoding="utf-8") as file_obj:
            json.dump(self.cache, file_obj, indent=4)

    def set(self, url: str, threat_name: str, categories: list[str]) -> None:
        """
            Add an entry to the cache in-memory

            :param str url: URL, used as key in cache
            :param str threat_name: name of the threat, received from Site Review
            :param list[str] categories: presumably list of pre-defined ZIA URL categories
        """
        self.cache[url] = {
            JsonFields.THREAT: threat_name,
            JsonFields.CATEGORIES: categories,
            JsonFields.CREATED: datetime.now().isoformat()
        }

    def get(self, url: str) -> dict[str,str] | None:
        """
            Get network data from cache by CIDR as JSON

            :param str url: value to be looked up in Site Review

            :return dict[str,str]: dict, corresponding to JSON entry in cache
        """
        entry = self.cache.get(url)

        if entry is not None:
            entry = entry.copy()
            del entry[JsonFields.CREATED]

        return entry
