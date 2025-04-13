from flask import Flask
from .db import init_db
import os

def create_app():
    app = Flask(__name__, template_folder='../templates')

    #App configuration
    app.config.update(
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongos:27017"), # MongoDB connection URI
        MONGO_DB = os.getenv("MONGO_DB", "my_database") #Database name
    )

    #Database initialization
    init_db(app)

    #Registering blueprints
    from .routes import main_routes
    app.register_blueprint(main_routes)

    return app


