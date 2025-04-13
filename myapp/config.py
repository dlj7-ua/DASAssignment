# App configuration
import os

class Config:
    # MongoDB connection URI
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    #Database name
    MONGO_DB = os.getenv("MONGO_DB", "my_database")
