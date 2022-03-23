import os 
from pymongo import MongoClient
from flask_pymongo import PyMongo

class Config:
    """
    Creates the configuration for the app to run.
    """
    WTF_CSRF_ENABLED = True
    
    MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
    MONGO_URI = os.environ.get("MONGO_URI")
    SECRET_KEY = os.environ.get("SECRET_KEY")

    DEBUG = True
