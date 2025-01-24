#!/usr/bin/env python3
"""11. Where can I learn Python?"""
from typing import List
from pymongo import collection


def schools_by_topic(mongo_collection, topic):
    """function that returns the list of school having a specific topic"""
    return mongo_collection.find({'topics': topic})
