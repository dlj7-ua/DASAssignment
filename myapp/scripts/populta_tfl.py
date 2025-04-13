import requests
import os
from pymongo import MongoClient
from datetime import datetime
import time
import logging
from urllib.parse import quote_plus
from bson import ObjectId

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tfl_population.log')
    ]
)
logger = logging.getLogger(__name__)

# Constantes
MODES = ["tube", "bus", "tram", "dlr", "overground", "river-bus"]
TFL_API_URL = "https://api.tfl.gov.uk"
DIRECTIONS = ["inbound", "outbound"]
VEHICLE_STATUSES = ["In Service", "Out of Service", "Delayed"]

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongos:27017")
MONGO_DB = os.getenv("MONGO_DB", "my_database")

def get_mongo_connection():
    """Crea conexión validada a MongoDB"""
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
        logger.critical(f"Error de conexión a MongoDB: {str(e)}")
        raise

def fetch_tfl_data(endpoint):
    """Obtiene datos de la API de TfL con manejo robusto de errores"""
    url = f"{TFL_API_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener {url}: {str(e)}")
        return None

def safe_object_id(id_str):
    """Convierte string a ObjectId de forma segura"""
    try:
        return ObjectId(id_str) if id_str else None
    except:
        return None

def populate_lines(db):
    """Pobla la colección Lines cumpliendo el validador"""
    logger.info("Poblando líneas de transporte...")

    for mode in MODES:
        data = fetch_tfl_data(f"/Line/Mode/{mode}")
        if not data:
            logger.warning(f"No se obtuvieron datos para modo {mode}")
            continue

        for line in data:
            try:
                # Procesar status y disruptions
                statuses = line.get("lineStatuses", [])
                status = "Unknown"
                disruptions = []
                
                if statuses:
                    status = statuses[0].get("statusSeverityDescription", "Unknown")
                    disruptions = [s.get("reason") for s in statuses if s.get("reason")]

                line_data = {
                    "lineId": ObjectId(),  # Nuevo ObjectId para el validador
                    "name": line["name"],
                    "mode": mode,
                    "status": status,
                    "disruptions": disruptions,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now()
                }

                # Insertar o actualizar
                db.Lines.update_one(
                    {"name": line["name"], "mode": mode},
                    {"$set": line_data},
                    upsert=True
                )

            except Exception as e:
                logger.error(f"Error procesando línea {line.get('id')}: {str(e)}")
                continue

        logger.info(f"Procesadas {len(data)} líneas para modo {mode}")
        time.sleep(1.5)

def populate_stations(db):
    """Pobla la colección Stations cumpliendo el validador"""
    logger.info("Poblando estaciones...")

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

                    # Primero verificar si la estación ya existe
                    existing_station = db.Stations.find_one({"name": station.get("commonName", station.get("name", "Unknown"))})
                    
                    if existing_station:
                        # Si existe, solo actualizamos las líneas
                        db.Stations.update_one(
                            {"_id": existing_station["_id"]},
                            {"$addToSet": {"lines": line_id}}
                        )
                    else:
                        # Si no existe, creamos la estación completa
                        station_data = {
                            "naptanId": ObjectId(),
                            "name": station.get("commonName", station.get("name", "Unknown")),
                            "mode": line.get("mode", "Unknown"),
                            "lines": [line_id],
                            "createdAt": datetime.now(),
                            "updatedAt": datetime.now()
                        }

                        # Añadir datos opcionales si existen
                        if "zone" in station:
                            station_data["zone"] = station["zone"]
                        if "lat" in station and "lon" in station:
                            station_data["location"] = {
                                "type": "Point",
                                "coordinates": [station["lon"], station["lat"]]
                            }

                        db.Stations.insert_one(station_data)

                except Exception as e:
                    logger.error(f"Error procesando estación: {str(e)}")
                    continue

            logger.info(f"Procesadas estaciones para línea {line_name}")
            time.sleep(0.7)

        except Exception as e:
            logger.error(f"Error procesando línea {line_name}: {str(e)}")
            continue

def populate_arrivals_and_vehicles(db):
    """Pobla Arrivals y Vehicles usando Naptan IDs"""
    logger.info("Poblando llegadas y vehículos...")

    for station in db.Stations.find().limit(30):  # Limitar para pruebas
        try:
            naptan_id = station.get("naptanId")
            if not naptan_id:
                logger.warning(f"Estación {station.get('name')} no tiene Naptan ID")
                continue

            # Usar el Naptan ID en lugar del nombre
            arrivals_data = fetch_tfl_data(f"/StopPoint/{naptan_id}/Arrivals")
            if not arrivals_data:
                logger.info(f"No hay llegadas para estación {station.get('name')} (Naptan ID: {naptan_id})")
                continue

            for arrival in arrivals_data:
                try:
                    # Procesar vehículo
                    vehicle_id = arrival.get("vehicleId")
                    if vehicle_id:
                        vehicle_data = {
                            "vehicleId": ObjectId(),
                            "lineId": safe_object_id(arrival.get("lineId")) or ObjectId(),
                            "currentLocation": arrival.get("currentLocation", "Unknown"),
                            "status": "In Service",
                            "createdAt": datetime.now(),
                            "updatedAt": datetime.now()
                        }

                        db.Vehicles.update_one(
                            {"currentLocation": vehicle_data["currentLocation"]},
                            {"$set": vehicle_data},
                            upsert=True
                        )
                        vehicle_id = vehicle_data["vehicleId"]

                    # Procesar llegada
                    direction = arrival.get("direction", "").lower()
                    direction = direction if direction in DIRECTIONS else "inbound"

                    arrival_data = {
                        "vehicleId": vehicle_id,
                        "lineId": safe_object_id(arrival.get("lineId")) or ObjectId(),
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

                    db.Arrivals.insert_one(arrival_data)

                except Exception as e:
                    logger.error(f"Error procesando llegada: {str(e)}")
                    continue

            logger.info(f"Procesadas {len(arrivals_data)} llegadas para {station['name']} (ID: {naptan_id})")
            time.sleep(2)  # Pausa generosa para rate limiting

        except Exception as e:
            logger.error(f"Error procesando estación {station.get('name')}: {str(e)}")
            continue
def main():
    """Función principal ejecutable desde CLI"""
    try:
        logger.info("Conectando a MongoDB...")
        db = get_mongo_connection()
        
        logger.info("Iniciando población de base de datos TfL...")
        
        populate_lines(db)
        populate_stations(db)
        populate_arrivals_and_vehicles(db)
        
        logger.info("¡Base de datos poblada exitosamente!")
        return True
    except Exception as e:
        logger.critical(f"Error durante la población: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if main():
        exit(0)
    else:
        exit(1)
