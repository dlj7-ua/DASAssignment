import requests
import os
from pymongo import MongoClient
from datetime import datetime
import time
import logging
from urllib.parse import quote_plus
from bson import ObjectId

# Logging set up
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tfl_population.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
MODES = ["tube", "bus", "tram", "dlr", "overground", "river-bus"]
TFL_API_URL = "https://api.tfl.gov.uk"
DIRECTIONS = ["inbound", "outbound"]
VEHICLE_STATUSES = ["In Service", "Out of Service", "Delayed"]

# MongoDB set up
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongos:27017")
MONGO_DB = os.getenv("MONGO_DB", "my_database")

def get_mongo_connection():
    """Creates MongoDB connection"""
    try:
        client = MongoClient(
            MONGO_URI,
            connectTimeoutMS=5000,
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=5000
        )
        client.server_info()  # Valida la conexión
        return client[MONGO_DB]
    except Exception as e:
        logger.critical(f"Error when trying to connect to MongoDB database: {str(e)}")
        raise

def fetch_tfl_data(endpoint):
    """Fectches data from TFL API"""
    url = f"{TFL_API_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener {url}: {str(e)}")
        return None

def safe_object_id(id_str):
    """Converts ObjectId to String safely"""
    try:
        return ObjectId(id_str) if id_str else None
    except:
        return None

def populate_lines(db):
    """Populates Lines with data from TFL API"""
    logger.info("Populateing transport Lines...")

    for mode in MODES:
        data = fetch_tfl_data(f"/Line/Mode/{mode}")
        if not data:
            logger.warning(f"No data found for mode: {mode}")
            continue

        for line in data:
            try:
                # Process line data and disruptions
                statuses = line.get("lineStatuses", [])
                status = "Unknown"
                disruptions = []
                
                if statuses:
                    status = statuses[0].get("statusSeverityDescription", "Unknown")
                    disruptions = [s.get("reason") for s in statuses if s.get("reason")]

                line_data = {
                    "lineId": ObjectId(),
                    "name": line["name"],
                    "mode": mode,
                    "status": status,
                    "disruptions": disruptions,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now()
                }

                # Insert or update line in MongoDB
                db.Lines.update_one(
                    {"name": line["name"], "mode": mode},
                    {"$set": line_data},
                    upsert=True
                )

            except Exception as e:
                logger.error(f"Error processing line: {line.get('id')}: {str(e)}")
                continue

        logger.info(f"Processed {len(data)} lines for mode {mode}")
        time.sleep(1.5)

def populate_stations(db):
    """Populates Stations with data from TFL API"""
    logger.info("Populating Stations...")

    for line in db.Lines.find():
        try:
            line_id = line["_id"]
            line_name = line["name"]
            data = fetch_tfl_data(f"/Line/{line_name}/StopPoints")
            if not data:
                continue

            for station in data:
                try:
                    naptan_id = station.get("naptanId")
                    if not naptan_id:
                        continue

                    # First check if the station already exists
                    existing_station = db.Stations.find_one({"name": station.get("commonName", station.get("name", "Unknown"))})
                    
                    if existing_station:
                        # If it exists, we update the station with the new line
                        db.Stations.update_one(
                            {"_id": existing_station["_id"]},
                            {"$addToSet": {"lines": line_id}}
                        )
                    else:
                        # If it doesn't exist, we create a new station
                        station_data = {
                            "naptanId": ObjectId(),
                            "name": station.get("commonName", station.get("name", "Unknown")),
                            "mode": line.get("mode", "Unknown"),
                            "lines": [line_id],
                            "createdAt": datetime.now(),
                            "updatedAt": datetime.now()
                        }

                        # Add optional fields if they exist
                        if "zone" in station:
                            station_data["zone"] = station["zone"]
                        if "lat" in station and "lon" in station:
                            station_data["location"] = {
                                "type": "Point",
                                "coordinates": [station["lon"], station["lat"]]
                            }

                        db.Stations.insert_one(station_data)

                except Exception as e:
                    logger.error(f"Error processing station: {str(e)}")
                    continue

            logger.info(f"Processed Stations for line: {line_name}")
            time.sleep(0.7)

        except Exception as e:
            logger.error(f"Error processing line: {line_name}: {str(e)}")
            continue

def fetch_mode_arrivals(mode):
    """Fetches arrivals for a specific mode of transport"""
    try:
        url = f"{TFL_API_URL}/Mode/{mode}/Arrivals"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching arrivals for mode {mode}: {str(e)}")
        return None

def populate_arrivals_and_vehicles(db):
    """Populates Arrivals and Vehicles with data from TFL API"""
    logger.info("Populating Vehicles and Arrivals for a given mode...")
    
    vehicles_cache = {}  # Cache para evitar duplicados de vehículos
    
    for mode in MODES:
        try:
            arrivals_data = fetch_mode_arrivals(mode)
            if not arrivals_data:
                continue

            arrivals_to_insert = []
            vehicles_to_insert = []

            for arrival in arrivals_data:
                try:
                    # Verify if the vehicle is already in the cache
                    vehicle_id = arrival.get("vehicleId")
                    if vehicle_id and vehicle_id not in vehicles_cache:
                        vehicle_data = {
                            "vehicleId": ObjectId(),
                            "lineId": db.Lines.find_one({"name": arrival.get("lineName")}, {"_id": 1})["_id"],
                            "currentLocation": arrival.get("currentLocation", "Unknown"),
                            "status": "In Service",
                            "createdAt": datetime.now(),
                            "updatedAt": datetime.now()
                        }
                        vehicles_to_insert.append(vehicle_data)
                        vehicles_cache[vehicle_id] = vehicle_data["vehicleId"]

                    #Processing arrival data
                    station = db.Stations.find_one({"name": arrival.get("stationName")}, {"_id": 1})
                    if not station:
                        continue

                    direction = arrival.get("direction", "").lower()
                    direction = direction if direction in DIRECTIONS else "inbound"

                    arrival_data = {
                        "vehicleId": vehicles_cache.get(vehicle_id, ObjectId()),
                        "lineId": db.Lines.find_one({"name": arrival.get("lineName")}, {"_id": 1})["_id"],
                        "stationId": station["_id"],
                        "destination": arrival.get("destinationName", "Unknown"),
                        "expectedArrival": datetime.strptime(
                            arrival["expectedArrival"], 
                            "%Y-%m-%dT%H:%M:%SZ"
                        ) if arrival.get("expectedArrival") else datetime.now(),
                        "timeToStation": int(arrival.get("timeToStation", 0)),
                        "direction": direction,
                        "createdAt": datetime.now()
                    }
                    arrivals_to_insert.append(arrival_data)

                except Exception as e:
                    logger.error(f"Error processing arrival: {str(e)}")
                    continue

            # Insert or update vehicles and arrivals in MongoDB
            if vehicles_to_insert:
                db.Vehicles.insert_many(vehicles_to_insert, ordered=False)
            if arrivals_to_insert:
                db.Arrivals.insert_many(arrivals_to_insert, ordered=False)

            logger.info(f"Processed {len(arrivals_data)} Arrivals for mode {mode}")
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"Error processing mode {mode}: {str(e)}")
            continue

def main():
    """Main function to populate the database"""
    try:
        logger.info("Connecting to MongoDB...")
        db = get_mongo_connection()
        
        logger.info("Initiating database population...")
        
        # Populate lines and stations first
        populate_lines(db)
        populate_stations(db)
        
        # Populate arrivals and vehicles
        populate_arrivals_and_vehicles(db)
        
        logger.info("Database Sucessfully populated!")
        return True
    except Exception as e:
        logger.critical(f"Error during the population: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if main():
        exit(0)
    else:
        exit(1)
