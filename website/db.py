import pymongo
from pymongo import MongoClient

cluster = pymongo.MongoClient("mongodb+srv://admin:IXMzXfgEFKaGqZGy@judgedb.580rhfp.mongodb.net/?retryWrites=true&w=majority")

db = cluster['lmaojudge']