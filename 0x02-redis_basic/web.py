#!/usr/bin/env python3
"""
Module for fetching web pages with caching and tracking using Redis.
"""

import redis
import requests
from typing import Callable
from functools import wraps


def track_access(method: Callable) -> Callable:
    """Decorator to track URL access count in Redis."""
    @wraps(method)
    def wrapper(*args, **kwargs):
        url = args[0]  # Assuming the first argument is the URL
        cache_key = f"count:{url}"
        redis_client = wrapper.redis
        redis_client.incr(cache_key)
        return method(*args, **kwargs)
    # Store a Redis instance in the wrapper for later use
    wrapper.redis = redis.Redis()
    return wrapper


@track_access
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL, caching the result with a 10-second expiration.
    
    Args:
        url (str): The URL to fetch.
    
    Returns:
        str: The HTML content of the URL.
    """
    cache_key = f"cache:{url}"
    redis_client = get_page.redis

    # Check if the result is already cached
    cached_content = redis_client.get(cache_key)
    if cached_content:
        return cached_content.decode("utf-8")

    # Fetch the content and cache it with a 10-second expiration
    response = requests.get(url)
    redis_client.setex(cache_key, 10, response.text)
    return response.text


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))  # Example usage
    access_count = get_page.redis.get(f"count:{url}")
    print(f"Access count for {url}: {access_count.decode('utf-8') if access_count else 0}")

