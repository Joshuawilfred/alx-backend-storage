#!/usr/bin/env python3
"""Module to fetch and cache web pages using Redis."""

import requests
import redis
from typing import Callable, Optional
from functools import wraps

# Initialize Redis client
redis_client = redis.Redis()

def cache_and_track(url: str) -> Callable:
    """Decorator to cache the result of a function and track access counts."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Increment the access count for the URL
            count_key = f"count:{url}"
            redis_client.incr(count_key)

            # Check if the result is already cached
            cache_key = f"cache:{url}"
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return cached_result.decode('utf-8')

            # If not cached, call the function and cache the result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, 10, result)  # Cache for 10 seconds
            return result
        return wrapper
    return decorator

def get_page(url: str) -> str:
    """Fetch the HTML content of a URL and cache it with a 10-second expiration."""
    @cache_and_track(url)
    def fetch_content(url: str) -> str:
        """Fetch the HTML content of the URL."""
        response = requests.get(url)
        return response.text

    return fetch_content(url)

# Example usage
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
