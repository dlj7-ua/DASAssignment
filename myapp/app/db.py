from flask import current_app
from pymongo import MongoClient
from pathlib import Path
import json
from bson.codec_options import CodecOptions

def init_db(app):
    #MongoDB initialization
    client = MongoClient(app.config['MONGO_URI'])
    db = client[app.config['MONGO_DB']]
    app.db = db

    create_collections(app.db, app)

def create_collections(db, app):
    schemes = {
        "Lines": "lines.json",
        "Stations": "stations.json",
        "Arrivals": "arrivals.json",
        "Vehicles": "vehicles.json"
    }

    base_path = Path(__file__).parent / "schemes"

    for collection, scheme in schemes.items():
        if collection not in db.list_collection_names():
            route = base_path / scheme
            with open(route, "r", encoding='utf-8') as file:
                config = json.loads(file.read())
                
                # Loads the JSON schema
                validator = config.get("validator", {})
                
                db.create_collection(
                    collection,
                    validator=validator,
                    validationLevel="strict",
                    validationAction="error"
                )
                app.logger.info(f"Colección {collection} creada con validador: {validator}")
