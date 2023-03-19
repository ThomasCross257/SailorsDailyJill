from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_DB(DB_NAME):
    MONGO_URI = os.environ.get('MONGO_URI')
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

mailServer = os.environ.get('MAIL_SERVER')
mailPort = os.environ.get('MAIL_PORT')
mailUseSSL = os.environ.get('MAIL_USE_SSL')
mailUsername = os.environ.get('EMAILUSERNAME')
mailPassword = os.environ.get('EMAILPASS')
mailDefaultSender = os.environ.get('EMAILDEFAULT')

accounts_db = get_DB('accounts')
admin_db = get_DB('admin')

user_collection = accounts_db["users"]
post_collection = accounts_db["posts"]
follow_collection = accounts_db["follows"]
default = None
