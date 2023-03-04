from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_DB(DB_NAME):
    MONGO_URI = os.getenv('MONGO_URI')
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

accounts_db = get_DB('accounts')
admin_db = get_DB('admin')

user_collection = accounts_db["users"]
post_collection = accounts_db["posts"]
default = None