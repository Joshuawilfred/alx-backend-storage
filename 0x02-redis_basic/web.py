#!/usr/bin/env python3
"""Module to fetch and cache web pages using Redis."""

import requests
import redis
from typing import Callable
from functools import wraps
import time

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


# Example usage and testing
if __name__ == "__main__":
    url = "http://google.com"

    # Test caching and count increment
    print(get_page(url))  # Fetch and cache the page
    count_key = f"count:{url}"
    cache_key = f"cache:{url}"

    # Check if the count is incremented
    count = redis_client.get(count_key)
    print(f"Access count for {url}: {count.decode('utf-8')}")

    # Check if the cache is set
    cached_result = redis_client.get(cache_key)
    print(f"Cached result for {url}: {cached_result is not None}")

    # Wait for 10 seconds and check if the cache is cleared
    time.sleep(10)
    cached_result = redis_client.get(cache_key)
    print(f"Cached result after 10 seconds: {cached_result is not None}")
