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
# Helper function to serialize MongoDB documents
def serialize_mongo_document(doc):
    return {
        k: str(v) if isinstance(v, ObjectId) else v
        for k, v in doc.items()
        if not isinstance(v, dict) and not isinstance(v, list)
    }


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
    try:
        lines = get_crud().find_all_lines() 
        formatted_lines = [
            {
                'lineId': str(line.get('lineId', '')),
                'name': line.get('name', ''),
                'mode': line.get('mode', ''),
                'status': line.get('status', ''),
                'disruptions': line.get('disruptions', []),
                'createdAt': line.get('createdAt', '').isoformat() if line.get('createdAt') else None,
                'updatedAt': line.get('updatedAt', '').isoformat() if line.get('updatedAt') else None
            }
            for line in lines
        ]
        return jsonify(formatted_lines), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    try:
        arrivals = get_crud().find_all_arrivals()
        formatted_arrivals = [
            {
                'vehicleId': str(arrival.get('vehicleId', '')),
                'lineId': str(arrival.get('lineId', '')),
                'stationId': str(arrival.get('stationId', '')),
                'destination': arrival.get('destination', ''),
                'expectedArrival': arrival.get('expectedArrival', '').isoformat() if arrival.get('expectedArrival') else None,
                'timeToStation': arrival.get('timeToStation', 0),
                'currentLocation': arrival.get('currentLocation', ''),
                'direction': arrival.get('direction', ''),
                'createdAt': arrival.get('createdAt', '').isoformat() if arrival.get('createdAt') else None
            }
            for arrival in arrivals
        ]
        return jsonify(formatted_arrivals), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    try:
        stations = get_crud().find_all_stations()
        formatted_stations = [
            {
                'naptanId': str(station.get('naptanId', '')),
                'name': station.get('name', ''),
                'mode': station.get('mode', ''),
                'lines': [str(line) for line in station.get('lines', [])],
                'createdAt': station.get('createdAt', '').isoformat() if station.get('createdAt') else None,
                'updatedAt': station.get('updatedAt', '').isoformat() if station.get('updatedAt') else None
            }
            for station in stations
        ]
        return jsonify(formatted_stations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    try:
        vehicles = get_crud().find_all_vehicles()
        formatted_vehicles = [
            {
                '_id': str(vehicle.get('_id')),
                'vehicleId': str(vehicle.get('vehicleId', '')),
                'lineId': str(vehicle.get('lineId', '')),
                'currentLocation': vehicle.get('currentLocation', ''),
                'status': vehicle.get('status', ''),
                'createdAt': vehicle.get('createdAt', '').isoformat() if vehicle.get('createdAt') else None,
                'updatedAt': vehicle.get('updatedAt', '').isoformat() if vehicle.get('updatedAt') else None
            }
            for vehicle in vehicles
        ]
        return jsonify(formatted_vehicles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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


@main_routes.route('/queries', methods=['GET', 'POST'])
def execute_queries():
    results = {}

    if request.method == 'POST':
        # Get the parameters from the form
        mode = request.form.get('mode')
        line_name = request.form.get('line_name')
        station_id = request.form.get('station_id')
        vehicle_id = request.form.get('vehicle_id')
        location = request.form.get('location')
        time = request.form.get('time', type=int)

        # Execute the queries based on the parameters
        if mode:
            results['lines_by_mode'] = get_queries().find_lines_by_mode(mode)

        if line_name:
            results['line_by_name'] = get_queries().find_line_by_name(line_name)

        if station_id:
            results['arrivals_by_station'] = get_queries().find_arrivals_by_station(station_id)

        if vehicle_id:
            results['arrivals_by_vehicle'] = get_queries().find_arrivals_by_vehicle(vehicle_id)

        if location:
            results['vehicles_by_location'] = get_queries().find_vehicles_by_location(location)

        if time:
            results['arrivals_with_long_wait'] = get_queries().find_arrivals_with_long_wait(time)

        results['count_arrivals_by_line'] = get_queries().count_arrivals_by_line()
        results['count_arrivals_by_station'] = get_queries().count_arrivals_by_station()
        results['stations_with_most_lines'] = get_queries().find_stations_with_most_lines()
        results['count_vehicles_by_line'] = get_queries().count_vehicles_by_line()
        results['lines_with_most_disruptions'] = get_queries().find_lines_with_most_disruptions()

    return render_template('queries.html', results=results)
