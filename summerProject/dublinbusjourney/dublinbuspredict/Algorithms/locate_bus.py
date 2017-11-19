import requests
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except:
    pass

# Gets the list of stops for a route, from the beginning of the line to the destination stop
def get_stop_list(route, direction, dest):
    # Tranform the direction string received from the Dublin Bus API to a number, so it matches to the Database
    if direction == 'Inbound':
        direction = 1
    elif direction == 'Outbound':
        direction = 0

    # Connect to the database to first get the trip_id and then get stop_id's for that trip
    db = pymysql.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    query = "SELECT bus_timetable.trip_id " \
            "FROM bus_timetable " \
            "WHERE direction =" + str(direction) + " and route_id ='" + str(route) + \
            "' ORDER BY stop_sequence limit 1;"
    cursor.execute(query)
    rows = cursor.fetchall()
    query = "SELECT bus_timetable.stop_id " \
            "FROM bus_timetable " \
            "WHERE trip_id ='" + str(rows[0][0]) + "' and route_id ='" + str(route) + \
            "' ORDER BY stop_sequence;"
    cursor.execute(query)
    rows2 = cursor.fetchall()
    db.close()

    # Loop through the results to remove unecessary inner tupples and to get the stops only up to the destination
    stop_list = []
    for i in rows2:
        stop_list.append(i[0])
        if str(i[0]) == str(dest):
            break
    return stop_list


# Queries the Dublin Bus API for the arrival time of a particular bus (nº1, 2 or 3) and returns the results
def get_real_time(route_id, stop_id, position):
    base_url = 'https://data.dublinked.ie/cgi-bin/rtpi/realtimebusinformation?stopid=' + str(stop_id) + '&routeid=' + str(route_id) + '&maxresults&operator&format=json'
    response = requests.get(base_url)
    results = response.json()

    # Used try catch in case the API has a missing bus, in which case we just reduce the indexing
    try:
        bus_at = [{'stopid':stop_id, 'duetime':results['results'][position]['duetime'], 'scheduledarrivaldatetime':results['results'][position]['scheduledarrivaldatetime'], 'arrivaldatetime':results['results'][position]['arrivaldatetime'],
                              'direction':results['results'][position]['direction'], 'origin':results['results'][position]['origin'], 'destination':results['results'][position]['destination']}]
    except:
        bus_at = [{'stopid':stop_id, 'duetime':results['results'][len(results['results']) - 1]['duetime'], 'scheduledarrivaldatetime':results['results'][len(results['results']) - 1]['scheduledarrivaldatetime'], 'arrivaldatetime':results['results'][len(results['results']) - 1]['arrivaldatetime'],
                              'direction':results['results'][len(results['results']) - 1]['direction'], 'origin':results['results'][len(results['results']) - 1]['origin'], 'destination':results['results'][len(results['results']) - 1]['destination']}]
    return bus_at


# Gets the list of stops from the stop closest to the bus down to the destination stop, including all the information needed for the model
def central(route, source, dest, direction, position):
    # Get list of stops to search bus in
    route_stops = get_stop_list(route, direction, dest)

    # Position means what bus where querying, the first, second or third, as this affects the index we use from Dublin Bus API real time results
    position = int(position)

    # Iterates through the list of stops and tries to find each bus using position
    bus_stops = []
    source_reached = False
    for i in range(len(route_stops) - 1, -1, -1):
        if str(route_stops[i]) == str(source):
            source_reached = True

        # Once the origin stop is reached, we begin searching for the bus location
        if source_reached:
            # Get time for next 3 buses arriving at stop
            x = get_real_time(route, route_stops[i], int(position))

            # These series of if statments check for errors in the results coming the API, and append data in different ways according to
            # a number of different circumstances.
            if source_reached and len(bus_stops) != 0 and x[0]['duetime'] != 'Due' and len(bus_stops[len(bus_stops) - 1]) != 1 and int(x[0]['duetime']) > int(bus_stops[len(bus_stops) - 1]['duetime']):

                # If its the first bus, and the duetime at current stop is longer than the at the previous stop, that means we've
                # shifted into another bus. We shift the position to match that change. When position is zero, the list is complete.
                if position == 0:
                    bus_stops.append([{'stopid':x[0]['stopid'], 'arrival':x[0]['arrivaldatetime']}])
                    break
                position -= 1
                x = get_real_time(route, route_stops[i], position)

            # If the list of stops is not empty and the bus is Due, we found the bus, and return the list.
            if len(bus_stops) != 0 and x[0]['duetime'] == 'Due' and source_reached:
                bus_stops.append([{'stopid':x[0]['stopid'], 'arrival':x[0]['arrivaldatetime']}])
                return bus_stops

            # If is zero, that means we reached the beginning of the route and did not find the bus. We return the whole thing.
            if i == 0:
                bus_stops.append([{'stopid':x[0]['stopid'], 'arrival':x[0]['arrivaldatetime']}])
                return bus_stops

            # Appends stopid, duetime and arrivaltime to the bus list, if it does not fall into any of the if statements
            bus_stops.append([{'stopid':x[0]['stopid'], 'duetime':x[0]['duetime'], 'arrival':x[0]['arrivaldatetime']}])
        else:
            #Just append the stopid. We wont find the bus after origin stop, so no need to query the API.
            bus_stops.append([{'stopid':route_stops[i]}])
    return bus_stops


# This is a support function called from the javascript to know how many buses are arriving next at the origin stop, up to 3 buses
# and use the number to query/model and display predictions one by one.
def get_buses(route_id, source_id):
    base_url = 'https://data.dublinked.ie/cgi-bin/rtpi/realtimebusinformation?stopid=' + str(source_id) + '&routeid=' + str(route_id) + '&maxresults&operator&format=json'
    response = requests.get(base_url)
    results = response.json()
    counter = 0
    first_3_buses = []

    # Get up to three buses arriving next at the origin stop.
    for i in results['results']:
        if counter == 3:
            break
        first_3_buses.append({'duetime':i['duetime'], 'scheduledarrivaldatetime':i['scheduledarrivaldatetime'], 'arrivaldatetime':i['arrivaldatetime'],
                              'direction':i['direction'], 'origin':i['origin'], 'destination':i['destination'], 'order':counter})
        counter += 1
    return first_3_buses
