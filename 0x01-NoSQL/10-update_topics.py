#!/usr/bin/env python3
"""10. Change school topics"""
from typing import List
from pymongo import collection


def update_topics(mongo_collection: collection, name: str,
                  topics: List[str]) -> None:
    """function that changes all topics of a school document based on name"""
    mongo_collection.update_many({'name': name},
                                 {'$set': {'topics': topics}})