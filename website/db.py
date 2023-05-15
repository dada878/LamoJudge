import pymongo
from pymongo import MongoClient

with open("mongoDB.txt", "r", encoding="UTF8") as f:
    url = f.read()

cluster = pymongo.MongoClient(url)

db = cluster['lmaojudge']