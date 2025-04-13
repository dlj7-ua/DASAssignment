from bson import ObjectId
from datetime import datetime

class CRUD:
    def __init__(self, db):
        self.db = db

    # CRUD Lines
    def insert_line(self, line_id, name, mode, status, disruptions=[]):
        self.db.Lines.insert_one({
            "lineId": ObjectId(line_id),
            "name": name,
            "mode": mode,
            "status": status,
            "disruptions": disruptions,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        })

    def find_line_by_id(self, line_id):
        return self.db.Lines.find_one({"lineId": line_id})

    def find_all_lines(self):
        return self.db.Lines.find()

    def update_line(self, line_id, name, mode, status, disruptions=[]):
        self.db.Lines.update_one(
            {"lineId": line_id},
            {"$set": 
                {
                    "name": name,
                    "mode": mode,
                    "status": status, 
                    "disruptions": disruptions,
                    "updatedAt": datetime.now()
                }
             }
        )

    def delete_line(self, line_id):
        self.db.Lines.delete_one({"lineId": line_id})

    # CRUD Arrivals
    def insert_arrival(self, vehicle_id, line_id, station_id, destination, expected_arrival, time_to_station, current_location, direction):
        self.db.Arrivals.insert_one({
            "vehicleId": ObjectId(vehicle_id),
            "lineId": ObjectId(line_id),
            "stationId": ObjectId(station_id),
            "destination": destination,
            "expectedArrival": expected_arrival,
            "timeToStation": time_to_station,
            "currentLocation": current_location,
            "direction": direction,
            "createdAt": datetime.now()
        })

    def find_arrival_by_id(self, vehicle_id):
        return self.db.Arrivals.find_one({"vehicleId": vehicle_id})

    def find_all_arrivals(self):
        return self.db.Arrivals.find()

    def update_arrival(self, vehicle_id, line_id, station_id, destination, expected_arrival, time_to_station, current_location, direction):
        self.db.Arrivals.update_one(
            {"vehicleId": vehicle_id},
            {"$set": 
                {
                    "lineId": ObjectId(line_id),
                    "stationId": ObjectId(station_id),
                    "destination": destination,
                    "expectedArrival": expected_arrival,
                    "timeToStation": time_to_station,
                    "currentLocation": current_location,
                    "direction": direction,
                    "updatedAt": datetime.now()
                }
             }
        )

    def delete_arrival(self, vehicle_id):
        self.db.Arrivals.delete_one({"vehicleId": vehicle_id})

    # CRUD Stations
    def find_station_by_id(self, naptan_id):
        return self.db.Stations.find_one({"naptanId": naptan_id})

    def find_all_stations(self):
        return self.db.Stations.find()

    def insert_station(self, naptan_id, name, mode, lines):
        self.db.Stations.insert_one({
            "naptanId": ObjectId(naptan_id),
            "name": name,
            "mode": mode,
            "lines": [ObjectId(line) for line in lines],
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        })

    def update_station(self, naptan_id, name, mode, lines):
        self.db.Stations.update_one(
            {"naptanId": naptan_id},
            {"$set": 
                {
                    "name": name,
                    "mode": mode,
                    "lines": [ObjectId(line) for line in lines],
                    "updatedAt": datetime.now()
                }
             }
        )

    def delete_station(self, naptan_id):
        self.db.Stations.delete_one({"naptanId": naptan_id})

    # CRUD para Vehicles
    def insert_vehicle(self, vehicle_id, line_id, current_location, status):
        self.db.Vehicles.insert_one({
            "vehicleId": vehicle_id,
            "lineId": ObjectId(line_id),
            "currentLocation": current_location,
            "status": status,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        })

    def find_vehicle_by_id(self, vehicle_id):
        return self.db.Vehicles.find_one({"vehicleId": vehicle_id})

    def find_all_vehicles(self):
        return self.db.Vehicles.find()

    def update_vehicle(self, vehicle_id, line_id, current_location, status):
        self.db.Vehicles.update_one(
            {"vehicleId": vehicle_id},
            {"$set": 
                {
                    "lineId": ObjectId(line_id),
                    "currentLocation": current_location,
                    "status": status, 
                    "updatedAt": datetime.now()
                }
             }
        )

    def delete_vehicle(self, vehicle_id):
        self.db.Vehicles.delete_one({"vehicleId": vehicle_id})
