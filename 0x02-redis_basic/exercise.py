#!/usr/bin/env python3
"""Python with Redis"""
import redis
import uuid
from typing import Union, Optional, Callable, Tuple, Dict
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator that takes callable args and count how many times
    the Cache class are called
    """
    @wraps(method)
    def wrapper(self, *args: Tuple, **kwargs: Dict) -> Callable:
        """wrapped function """
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and
    outputs for a particular function.
    """
    @wraps(method)
    def wrapper(self, *args: Tuple, **kwargs: Dict):
        """Wrapper Function"""
        keys = method(self, *args, **kwargs)
        self._redis.rpush(f'{method.__qualname__}:inputs', str(args))
        self._redis.rpush(f'{method.__qualname__}:outputs', keys)
        return keys
    return wrapper


def replay(fn: Callable) -> None:
    """Function to display the history of calls of a particular function."""
    client = redis.Redis()

    method_name = fn.__qualname__
    input_list_name = f'{method_name}:inputs'
    output_list_name = f'{method_name}:outputs'

    calls_count = client.get(method_name).decode('utf-8')

    inputs = [input.decode('utf-8') for input in
              client.lrange(input_list_name, 0, -1)]

    outputs = [output.decode('utf-8') for output in
               client.lrange(output_list_name, 0, -1)]

    print(f'{method_name} was called {calls_count} times:')
    for input, output in zip(inputs, outputs):
        print(f'{method_name}(*{input}) -> {output}')


class Cache:
    """Cache Class for redis connection"""

    def __init__(self) -> None:
        """Init redis connection"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Function that generate a random key"""
        key: str = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> str:
        """Get the value of the entered key"""
        value = self._redis.get(key)

        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Convert entered key to string"""
        return self.get(key, lambda data: data.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Convert the entered key to integer"""
        return int(key)
