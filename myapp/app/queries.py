from bson import ObjectId
from datetime import datetime

class Queries:
    def __init__(self, db):
        self.db = db

    # Queries for Lines
    def find_lines_by_mode(self, mode):
        return list(self.db.Lines.find({"mode": mode}))

    def find_line_by_name(self, name):
        return self.db.Lines.find_one({"name": name})

    def find_lines_with_most_disruptions(self):
        return list(self.db.Lines.aggregate([
            {"$project": {"name": 1, "disruptionCount": {"$size": "$disruptions"}}},
            {"$sort": {"disruptionCount": -1}},
            {"$limit": 5}
        ]))

    # Queries for Arrivals
    def find_arrivals_by_line(self, line_id, limit=10):
        return list(self.db.Arrivals.aggregate([
            {"$match": {"lineId": ObjectId(line_id)}},
            {"$sort": {"expectedArrival": 1}},
            {"$limit": limit}
        ]))

    def find_arrivals_by_station(self, station_id, limit=10):
        return list(self.db.Arrivals.aggregate([
            {"$match": {"stationId": ObjectId(station_id)}},
            {"$sort": {"expectedArrival": 1}},
            {"$limit": limit}
        ]))

    def count_arrivals_by_line(self):
        return list(self.db.Arrivals.aggregate([
            {"$group": {"_id": "$lineId", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))

    def count_arrivals_by_station(self):
        return list(self.db.Arrivals.aggregate([
            {"$group": {"_id": "$stationId", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]))

    def find_arrivals_by_vehicle(self, vehicle_id):
        return list(self.db.Arrivals.find({"vehicleId": vehicle_id}))

    def find_arrivals_with_long_wait(self, time=300):
        return list(self.db.Arrivals.find({"timeToStation": {"$gt": time}}))

    # Queries Lines Stations
    def find_stations_by_line(self, line_id):
        return list(self.db.Stations.find({"lines": ObjectId(line_id)}))

    def find_stations_by_mode(self, mode):
        return list(self.db.Stations.find({"mode" : mode}))

    def find_stations_with_most_lines(self):
        return list(self.db.Stations.aggregate([
            {"$project": {"name": 1, "lineCount": {"$size": "$lines"}}},
            {"$sort": {"lineCount": -1}},
            {"$limit": 5}
        ]))

    # Queries for Vehicles
    def find_vehicles_by_line_and_status(self, line_id, status="In Service"):
        return list(self.db.Vehicles.find({"lineId": ObjectId(line_id), "status": status}))

    def find_vehicles_by_location(self, location):
        return list(self.db.Vehicles.find({"currentLocation": {"$regex": location}}))

    def count_vehicles_by_line(self):
        return list(self.db.Vehicles.aggregate([
            {"$group": {"_id": "$lineId", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]))
