from flask import Blueprint, render_template, request, jsonify, current_app
from bson import ObjectId
from .queries import Queries
from .crud import CRUD

#Create Blueprints for the routes
main_routes = Blueprint('main', __name__)

def get_queries():
    return Queries(current_app.db)

def get_crud():
    return CRUD(current_app.db)

#Create the routes
@main_routes.route('/')
def main():
    return render_template('index.html')

@main_routes.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main_routes.route('/otra-pagina')
def otra_pagina():
    return render_template('otra-pagina.html')

#CRUDs
#Lines
@main_routes.route('/lines', methods=['POST'])
def create_line():
    data = request.get_json()
    if not all (key in data for key in ['lineId', 'name', 'mode', 'status', 'disruptions']):
        return jsonify({'error': 'Missing data'}), 400
    try:
        get_crud().insert_line(
            line_id = data['lineId'],
            name = data['name'],
            mode = data['mode'],
            status = data['status'],
            disruptions = data['disruptions']
        )
        return jsonify({'message': 'Line created successfully'}), 201
    except:
        return jsonify({'error': 'An error occurred'}), 500

@main_routes.route('/lines', methods=['GET'])
def get_all_lines():
    lines = get_crud().find_all_lines()
    lines = [
    {
        **line,
        '_id': str(line['_id']),
        'lineId': str(line['lineId']),
        'createdAt': line['createdAt'].isoformat(),
        'updatedAt': line['updatedAt'].isoformat()
    }
    for line in lines
]
    return jsonify(lines), 200

@main_routes.route('/line/<line_id>', methods=['GET'])
def get_line(line_id):
    line = get_crud().find_line_by_id(line_id)
    line = {
        **line,
        '_id': str(line['_id']),
        'lineId': str(line['lineId']),
        'createdAt': line['createdAt'].isoformat(),
        'updatedAt': line['updatedAt'].isoformat()
    }
    if line:
        return jsonify(line), 200
    else:
        return jsonify({'error': 'Line not found'}), 404

@main_routes.route('/line/<line_id>', methods=['PUT'])
def update_line(line_id):
    data = request.get_json()
    if not all (key in data for key in ['name', 'mode', 'status', 'disruptions']):
        return jsonify({'error': 'Missing data'}), 400

    try:
        get_crud().update_line(
            line_id = line_id,
            name = data['name'],
            mode = data['mode'],
            status = data['status'],
            disruptions = data['disruptions']
        )
        return jsonify({'message': 'Line updated successfully'}), 200
    except:
        return jsonify({'error': 'An error occurred'}), 500

@main_routes.route('/line/<line_id>', methods=['DELETE'])
def delete_line(line_id):
    try:
        get_crud().delete_line(line_id = line_id)
        return jsonify({'message': 'Line deleted successfully'}), 200
    except:
        return jsonify({'error': 'An error occurred'}), 500

#Arrivals
@main_routes.route('/arrivals', methods=['POST'])
def create_arrival():
    data = request.get_json()
    if not all (key in data for key in ['vehicleId', 'lineId', 'stationId', 'destination', 'expected_arrival', 'time_to_station', 'current_location', 'direction']):
        return jsonify({'error': 'Missing data'}), 400

    try:
        get_crud().insert_arrival(
            vehicle_id = data['vehicleId'],
            line_id = data['lineId'],
            station_id = data['stationId'],
            destination = data['destination'],
            expected_arrival = data['expected_arrival'],
            time_to_station = data['time_to_station'],
            current_location = data['current_location'],
            direction = data['direction']
        )
        return jsonify({'message': 'Arrival created successfully'}), 201
    except:
        return jsonify({'error': 'An error occurred'}), 500

@main_routes.route('/arrivals', methods=['GET'])
def get_all_arrivals():
    arrivals = get_crud().find_all_arrivals()
    arrivals = [
        {
            **arrival,
            '_id': str(arrival['_id']),
            'vehicleId': str(arrival['vehicleId']),
            'lineId': str(arrival['lineId']),
            'stationId': str(arrival['stationId']),
            'expectedArrival': arrival['expectedArrival'].isoformat(),
            'createdAt': arrival['createdAt'].isoformat(),
            'updatedAt': arrival['updatedAt'].isoformat()
        }
        for arrival in arrivals
    ]
    return jsonify(arrivals), 200

@main_routes.route('/arrivals/<vehicle_id>', methods=['GET'])
def get_arrival(vehicle_id):
    arrival = get_crud().find_arrival_by_id(vehicle_id)
    arrival = {
        **arrival,
        '_id': str(arrival['_id']),
        'vehicleId': str(arrival['vehicleId']),
        'lineId': str(arrival['lineId']),
        'stationId': str(arrival['stationId']),
        'expectedArrival': arrival['expectedArrival'].isoformat(),
        'createdAt': arrival['createdAt'].isoformat(),
        'updatedAt': arrival['updatedAt'].isoformat()
    }
    
    if arrival:
        return jsonify(arrival), 200
    else:
        return jsonify({'error': 'Arrival not found'}), 404

@main_routes.route('/arrival/<vehicle_id>', methods=['PUT'])
def update_arrival(vehicle_id):
    data = request.get_json()
    if not all (key in data for key in ['lineId', 'stationId', 'destination', 'expected_arrival', 'time_to_station', 'current_location', 'direction']):
        return jsonify({'error': 'Missing data'}), 400

    try:
        get_crud().update_arrival(
            vehicle_id = vehicle_id,
            line_id = data['lineId'],
            station_id = data['stationId'],
            destination = data['destination'],
            expected_arrival = data['expected_arrival'],
            time_to_station = data['time_to_station'],
            current_location = data['current_location'],
            direction = data['direction']
        )
        return jsonify({'message': 'Arrival updated successfully'}), 200
    except:
        return jsonify({'error': 'An error occurred'}), 500

@main_routes.route('/arrival/<vehicle_id>', methods=['DELETE'])
def delete_arrival(vehicle_id):
    try:
        get_crud().delete_arrival(vehicle_id = vehicle_id)
        return jsonify({'message': 'Arrival deleted successfully'}), 200
    except:
        return jsonify({'error': 'An error occurred'}), 500

#Stations
@main_routes.route('/stations', methods=['GET'])
def get_all_stations():
    stations = get_crud().find_all_stations()
    stations = [
        {
            **station,
            '_id': str(station['_id']),
            'stationId': str(station['stationId']),
            'createdAt': station['createdAt'].isoformat(),
            'updatedAt': station['updatedAt'].isoformat()
        }
        for station in stations
    ]
    return jsonify(stations), 200

@main_routes.route('/station/<station_id>', methods=['GET'])
def get_station(station_id):
    station = get_crud().find_station_by_id(station_id)
    station = {
        **station,
        '_id': str(station['_id']),
        'stationId': str(station['stationId']),
        'createdAt': station['createdAt'].isoformat(),
        'updatedAt': station['updatedAt'].isoformat()
    }
    if station:
        return jsonify(station), 200
    else:
        return jsonify({'error': 'Station not found'}), 404

@main_routes.route('/station/<station_id>', methods=['PUT'])
def update_station(station_id):
    data = request.get_json()
    if not all (key in data for key in ['name', 'mode', 'lines']):
        return jsonify({'error': 'Missing data'}), 400

    try:
        get_crud().update_station(
            naptan_id = station_id,
            name = data['name'],
            mode = data['mode'],
            lines = data['lines']
        )
        return jsonify({'message': 'Station updated successfully'}), 200
    except:
        return jsonify({'error': 'An error occurred'}), 500

@main_routes.route('/station/<station_id>', methods=['DELETE'])
def delete_station(station_id):
    try:
        get_crud().delete_station(naptan_id = station_id)
        return jsonify({'message': 'Station deleted successfully'}), 200
    except:
        return jsonify({'error': 'An error occurred'}), 500

#Vehicles
@main_routes.route('/vehicles', methods=['POST'])
def create_vehicle():
    data = request.get_json()

    if not all (key in data for key in ['vehicleId', 'lineId', 'current_location', 'status']):
        return jsonify({'error': 'Missing data'}), 400

    try:
        get_crud().insert_vehicle(
            vehicle_id = data['vehicleId'],
            line_id = data['lineId'],
            current_location = data['current_location'],
            status = data['status']
        )
        return jsonify({'message': 'Vehicle created successfully'}), 201
    except:
        return jsonify({'error': 'An error occurred'}), 500

@main_routes.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    vehicles = get_crud().find_all_vehicles()
    vehicles = [
        {
            **vehicle,
            '_id': str(vehicle['_id']),
            'vehicleId': str(vehicle['vehicleId']),
            'createdAt': vehicle['createdAt'].isoformat(),
            'updatedAt': vehicle['updatedAt'].isoformat()
        }
        for vehicle in vehicles
    ]
    return jsonify(vehicles), 200

@main_routes.route('/vehicle/<vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = get_crud().find_vehicle_by_id(vehicle_id)
    vehicle = {
        **vehicle,
        '_id': str(vehicle['_id']),
        'vehicleId': str(vehicle['vehicleId']),
        'createdAt': vehicle['createdAt'].isoformat(),
        'updatedAt': vehicle['updatedAt'].isoformat()
    }
    if vehicle:
        return jsonify(vehicle), 200
    else:
        return jsonify({'error': 'Vehicle not found'}), 404

@main_routes.route('/vehicle/<vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    data = request.get_json()
    if not all (key in data for key in ['lineId', 'current_location', 'status']):
        return jsonify({'error': 'Missing data'}), 400

    try:
        get_crud().update_vehicle(
            vehicle_id = vehicle_id,
            line_id = data['lineId'],
            current_location = data['current_location'],
            status = data['status']
        )
        return jsonify({'message': 'Vehicle updated successfully'}), 200
    except:
        return jsonify({'error': 'An error occurred'}), 500

@main_routes.route('/vehicle/<vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    try:
        get_crud().delete_vehicle(vehicle_id = vehicle_id)
        return jsonify({'message': 'Vehicle deleted successfully'}), 200
    except:
        return jsonify({'error': 'An error occurred'}), 500

#Queries

#Lines

@main_routes.route('/lines/mode/<mode>', methods=['GET'])
def get_lines_by_mode(mode):
    lines = get_queries().find_lines_by_mode(mode)
    lines = [
        {
            **line,
            '_id': str(line['_id']),
            'lineId': str(line['lineId']),
            'createdAt': line['createdAt'].isoformat(),
            'updatedAt': line['updatedAt'].isoformat()
        }
        for line in lines
    ]
    return jsonify(lines), 200

@main_routes.route('/line/name/<name>', methods=['GET'])
def get_lines_by_name(name):
    line = get_queries().find_line_by_name(name)
    line = {
        **line,
        '_id': str(line['_id']),
        'lineId': str(line['lineId']),
        'createdAt': line['createdAt'].isoformat(),
        'updatedAt': line['updatedAt'].isoformat()
    }
    return jsonify(line), 200

@main_routes.route('/lines/disruptions', methods=['GET'])
def get_lines_with_most_disruptions():
    lines = get_queries().find_lines_with_most_disruptions()
    lines = [
        {
            **line,
            '_id': str(line['_id']),
            'lineId': str(line['lineId']),
            'createdAt': line['createdAt'].isoformat(),
            'updatedAt': line['updatedAt'].isoformat()
        }
        for line in lines
    ]
    return jsonify(lines), 200

#Arrivals

@main_routes.route('/arrivals/line/<line_id>', methods=['GET'])
def get_arrivals_by_line(line_id):
    arrivals = get_queries().find_arrivals_by_line(line_id)
    arrivals = [
        {
            **arrival,
            '_id': str(arrival['_id']),
            'vehicleId': str(arrival['vehicleId']),
            'lineId': str(arrival['lineId']),
            'stationId': str(arrival['stationId']),
            'expectedArrival': arrival['expectedArrival'].isoformat(),
            'createdAt': arrival['createdAt'].isoformat(),
            'updatedAt': arrival['updatedAt'].isoformat()
        }
        for arrival in arrivals
    ]
    return jsonify(arrivals), 200

@main_routes.route('/arrivals/station/<station_id>', methods=['GET'])
def get_arrivals_by_station(station_id):
    arrivals = get_queries().find_arrivals_by_station(station_id)
    arrivals = [
        {
            **arrival,
            '_id': str(arrival['_id']),
            'vehicleId': str(arrival['vehicleId']),
            'lineId': str(arrival['lineId']),
            'stationId': str(arrival['stationId']),
            'expectedArrival': arrival['expectedArrival'].isoformat(),
            'createdAt': arrival['createdAt'].isoformat(),
            'updatedAt': arrival['updatedAt'].isoformat()
        }
        for arrival in arrivals
    ]
    return jsonify(arrivals), 200

@main_routes.route('/arrivals/vehicle/<vehicle_id>', methods=['GET'])
def get_arrivals_by_vehicle(vehicle_id):
    arrivals = get_queries().find_arrivals_by_vehicle(vehicle_id)
    arrivals = [
        {
            **arrival,
            '_id': str(arrival['_id']),
            'vehicleId': str(arrival['vehicleId']),
            'lineId': str(arrival['lineId']),
            'stationId': str(arrival['stationId']),
            'expectedArrival': arrival['expectedArrival'].isoformat(),
            'createdAt': arrival['createdAt'].isoformat(),
            'updatedAt': arrival['updatedAt'].isoformat()
        }
        for arrival in arrivals
    ]
    return jsonify(arrivals), 200

@main_routes.route('/arrivals/long_wait', methods=['GET'])
def get_arrivals_with_long_wait():
    arrivals = get_queries().find_arrivals_with_long_wait()
    arrivals = [
        {
            **arrival,
            '_id': str(arrival['_id']),
            'vehicleId': str(arrival['vehicleId']),
            'lineId': str(arrival['lineId']),
            'stationId': str(arrival['stationId']),
            'expectedArrival': arrival['expectedArrival'].isoformat(),
            'createdAt': arrival['createdAt'].isoformat(),
            'updatedAt': arrival['updatedAt'].isoformat()
        }
        for arrival in arrivals
    ]
    return jsonify(arrivals), 200

@main_routes.route('/arrivals/count/line', methods=['GET'])
def count_arrivals_by_line():
    count = get_queries().count_arrivals_by_line()
    return jsonify(count), 200

@main_routes.route('/arrivals/count/station', methods=['GET'])
def count_arrivals_by_station():
    count = get_queries().count_arrivals_by_station()
    return jsonify(count), 200

#Staions

@main_routes.route('/stations/line/<line_id>', methods=['GET'])
def get_stations_by_line(line_id):
    stations = get_queries().find_stations_by_line(line_id)
    stations = [
        {
            **station,
            '_id': str(station['_id']),
            'naptanId': str(station['naptanId']),
            'name': station['name'],
            'mode': station['mode'],
            'createdAt': station['createdAt'].isoformat(),
            'updatedAt': station['updatedAt'].isoformat()
        }
        for station in stations
    ]
    return jsonify(stations), 200

@main_routes.route('/stations/mode/<mode>', methods=['GET'])
def get_stations_by_mode(mode):
    stations = get_queries().find_stations_by_mode(mode)
    stations = [
        {
            **station,
            '_id': str(station['_id']),
            'naptanId': str(station['naptanId']),
            'name': station['name'],
            'mode': station['mode'],
            'createdAt': station['createdAt'].isoformat(),
            'updatedAt': station['updatedAt'].isoformat()
        }
        for station in stations
    ]
    return jsonify(stations), 200

@main_routes.route('/stations/lines', methods=['GET'])
def get_stations_most_lines():
    count = get_queries().find_stations_with_most_lines()
    return jsonify(count), 200

#Vehicles

@main_routes.route('/vehicles/line_status/<line_id>', methods=['GET'])
def get_vehicles_by_line_status(line_id):
    vehicles = get_queries().find_vehicles_by_line_and_status(line_id)
    vehicles = [
        {
            **vehicle,
            '_id': str(vehicle['_id']),
            'vehicleId': str(vehicle['vehicleId']),
            'lineId': str(vehicle['lineId']),
            'currentLocation': vehicle['currentLocation'],
            'createdAt': vehicle['createdAt'].isoformat(),
            'updatedAt': vehicle['updatedAt'].isoformat()
        }
        for vehicle in vehicles
    ]
    return jsonify(vehicles), 200

@main_routes.route('/vehicles/location/<location>', methods=['GET'])
def get_vehicles_by_location(location):
    vehicles = get_queries().find_vehicles_by_location(location)
    vehicles = [
        {
            **vehicle,
            '_id': str(vehicle['_id']),
            'vehicleId': str(vehicle['vehicleId']),
            'lineId': str(vehicle['lineId']),
            'currentLocation': vehicle['currentLocation'],
            'createdAt': vehicle['createdAt'].isoformat(),
            'updatedAt': vehicle['updatedAt'].isoformat()
        }
        for vehicle in vehicles
    ]
    return jsonify(vehicles), 200

@main_routes.route('/vehicles/line_count', methods=['GET'])
def count_vehicles_by_line(line_id):
    count = get_queries().count_vehicles_by_line()
    return jsonify(count), 200
