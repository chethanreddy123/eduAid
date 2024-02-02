from pymongo import MongoClient
from dotenv import load_dotenv
from typing import Optional
import os

load_dotenv()


class MongoDBConnection:
    def __init__(self, sub_collection : str,
                connection_string: Optional[str] = os.getenv("MONGO_KEY"), 
                database_name : Optional[str] = "EduAid"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.sub_collection = sub_collection

    def connect(self):
        try:
            client = MongoClient(self.connection_string)
            db = client[self.database_name]
            sub_collection = db[self.sub_collection]
            print(f"Connected to MongoDB. Using sub-collection: {self.sub_collection}")
            return sub_collection
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise


