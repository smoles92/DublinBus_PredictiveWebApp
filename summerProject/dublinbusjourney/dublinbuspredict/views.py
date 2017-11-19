import json
import requests
from django.http import HttpResponse
from django.shortcuts import render
from requests_oauthlib import OAuth1
from .Algorithms import project_central, locate_bus
import MySQLdb
from .Algorithms import time_date
from datetime import datetime

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except:
    pass


route_id, source_id, destination_id, direction = '17', 1, 1, 1
time, date = 0, 0
day_of_week = ''
new_info_buses = ['1']
old_info_buses = []
stops_origin_1, stops_destination_1, stops_destination_2, list_stops = [], [], [], []
bus1, bus2, bus3, busNumber = 0, 0, 0, 0
stops1, stops2, stops3 = [], [], []
list_routes = ['1', '4', '7', '9', '11', '13', '14', '15', '16', '17', '18', '25', '27', '31', '32',
                   '33', '37', '38', '39', '40', '41', '42', '43', '44', '47', '49', '53', '59', '61', '63',
                   '65', '66', '67', '68', '69', '70', '75', '76', '79', '83', '84', '102', '104', '111',
                   '114', '116', '118', '122', '123', '130', '140', '142', '145', '150', '151', '161', '184',
                   '185', '220', '236', '238', '239', '270', '747', '757', '14C', '15A', '15B', '16C', '17A',
                   '25A', '25B', '25D', '25X', '26A', '27A', '27B', '27X', '29A', '31A', '31B', '31D', '32A', '32X',
                   '33A', '33B', '33X', '38A', '38B', '38D', '39A', '40B', '40D', '41A', '41B', '41C', '41X', '42D',
                   '44B', '45A', '46A', '46E', '51D', '51X', '54A', '56A', '65B', '66A', '66B', '66X', '67X', '68A',
                   '68X', '69X', '70D', '76A', '77A', '77X', '79A', '7A', '7B', '7D', '83A', '84A', '84X']

def index(request):
    global list_routes
    db = MySQLdb.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    cursor.execute("SELECT distinct(bus_timetable.route_id) "
                   "FROM bus_timetable order by bus_timetable.route_id + 0;")
    rows = cursor.fetchall()
    routes = []
    for i in rows:
        routes.append(i[0])
    cursor.execute("SELECT bus_stops.stop_id "
                   "FROM bus_stops;")
    rows2 = cursor.fetchall()
    db.close()
    stops = []
    for i in rows2:
        stops.append(i[0])
    return render(request, 'dublinbuspredict/index.html', {'list_routes': routes, 'list_stops': stops})

def pilot_routes(request):
    global stops_origin_1
    route_id = request.GET.get('route')
    weekday = datetime.weekday(datetime.now())
    time = datetime.now().time().strftime('%H:%M:%S')
    d = 0
    if weekday < 5:
        d = 'business_day'
    elif weekday == 5:
        d = 'saturday'
    else:
        d = 'sunday'
    db = pymysql.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    query = "SELECT distinct(trip_id), count(stop_id), direction " \
            "FROM bus_timetable " \
            "WHERE bus_timetable.route_id ='" + str(route_id) + "' and bus_timetable.day_of_week='" + d + "' and bus_timetable.arrival_time>='" + str(time) + "' " \
            "GROUP BY trip_id, direction " \
            "ORDER BY stop_sequence;"
    cursor.execute(query)
    trip_list = cursor.fetchall()
    trip_count_in = 0
    trip_count_out = 0
    trip_inbound = 0
    trip_outbound = 0
    for i in trip_list:
        if i[2] == 1:
            if i[1] > trip_count_in:
                trip_inbound = i[0]
                trip_count_in = i[1]
        elif i[2] == 0:
            if i[1] > trip_count_out:
                trip_outbound = i[0]
                trip_count_out = i[1]
    query = "SELECT bus_timetable.stop_id, bus_timetable.trip_id " \
            "FROM bus_timetable " \
            "WHERE bus_timetable.trip_id ='" + str(trip_inbound) + "' or bus_timetable.trip_id='" + str(trip_outbound) + "' " \
            "ORDER BY stop_sequence;"
    cursor.execute(query)
    stops_in = cursor.fetchall()
    stops_origin_1 = stops_in
    db.close()
    return HttpResponse(json.dumps({"stops":stops_in}), content_type='application/json')

def pilot_dest(request):
    source_id = request.GET.get('source')
    route_id = request.GET.get('route')
    global direction, stops_origin_1, stops_destination_1, stops_destination_2
    trip_id = 0
    for i in stops_origin_1:
        if str(i[0]) == str(source_id):
            trip_id = str(i[1])
            break
    db = pymysql.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    query = "SELECT bus_timetable.stop_id, bus_stops.lat, bus_stops.lon, bus_stops.long_name, bus_stops.name, bus_timetable.accum_dist " \
            "FROM bus_timetable, bus_stops " \
            "WHERE bus_timetable.trip_id ='" + trip_id + "' and bus_timetable.stop_id = bus_stops.stop_id ORDER BY stop_sequence;"
    cursor.execute(query)
    bus_stops = cursor.fetchall()
    db.close()
    stops = []
    stops2 = []
    found = False
    for i in bus_stops:
        if str(i[0]) == str(source_id):
            stops2.append(i)
            found = True
            continue
        if found:
            stops.append(i)
            stops2.append(i)
    stops_destination_1 = stops
    stops_destination_2 = stops2
    return HttpResponse(json.dumps({"stops":stops}), content_type='application/json')

def run_model(request):
    global route_id
    global source_id
    global destination_id
    global new_info_buses
    global stops_destination_1
    route_id = request.GET.get('route')
    source_id = request.GET.get('source')
    destination_id = request.GET.get('destination')
    direction = request.GET.get('direction')
    position = request.GET.get('position')
    for_js = []
    for_js.append(project_central.main(route_id, source_id, destination_id, direction, position))
    return HttpResponse(json.dumps({'info_buses': for_js, 'info_stops': stops_destination_1}), content_type='application/json')


# This is a support function called from the javascript to know how many buses are arriving next at the origin stop, up to 3 buses
# and use the number to query/model and display predictions one by one.
def get_number_buses(request):
    route_id = request.GET.get('route')
    source_id = request.GET.get('source')
    buses = locate_bus.get_buses(route_id, source_id)
    if buses != []:
        direction = buses[0]['direction']
        return HttpResponse(json.dumps({'buses': len(buses), 'direction': direction}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'buses': 'No buses found!'}), content_type='application/json')


def set_info_next_page(request):
    global route_id, source_id, destination_id, time, date, day_of_week
    route_id = request.GET.get('route')
    source_id = request.GET.get('source')
    destination_id = request.GET.get('destination')
    time = request.GET.get('time')
    date = request.GET.get('date')
    return HttpResponse(json.dumps({'ok':'ok'}), content_type='application/json')


def get_info_next_page(request):
    global route_id, source_id, destination_id, time, date, direction
    return HttpResponse(json.dumps({'source': source_id, 'destination':destination_id, 'route':route_id, 'time':time, 'date':date, 'direction':direction}), content_type='application/json')

def load_routes_for_map(request):
    global list_routes
    global source_id
    global route_id
    global destination_id
    global time, date
    global day_of_week
    db = MySQLdb.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    cursor.execute("SELECT distinct(bus_timetable.route_id) "
                   "FROM bus_timetable order by bus_timetable.route_id + 0;")
    rows = cursor.fetchall()
    routes = []
    for i in rows:
        routes.append(i[0])
    cursor.execute("SELECT bus_stops.stop_id "
                   "FROM bus_stops;")
    rows2 = cursor.fetchall()
    db.close()
    stops = []
    for i in rows2:
        stops.append(i[0])
    global new_info_buses
    return HttpResponse(json.dumps({'list_routes': routes, 'list_stops': stops, 'info_buses': new_info_buses}), content_type='application/json')

def run_planner(request):
    global route_id
    global source_id
    global destination_id
    global new_info_buses
    global date
    global time
    global direction
    global list_stops
    global bus1, bus2, bus3, stops1, stops2, stops3, busNumber
    route_id = request.GET.get('route')
    source_id = request.GET.get('source')
    destination_id = request.GET.get('destination')
    date = request.GET.get('date')
    time = request.GET.get('time')
    # bus = request.GET.get('bus')
    # stops = request.GET.get('stops')
    stops = []
    if busNumber == 0 and bus1 != 0:
        bus = bus1
        stops = stops1
        busNumber += 1
    elif busNumber == 1 and bus2 != 0:
        bus = bus2
        stops = stops2
        busNumber += 1
    elif busNumber == 2 and bus3 != 0:
        bus = bus3
        stops = stops3
        busNumber += 1
    if stops != []:
        new_info_buses = time_date.time_date(route_id, source_id, destination_id, date, time, direction, stops, bus)
    return HttpResponse(json.dumps({'info_buses': new_info_buses, 'stops':stops}), content_type='application/json')

def map(request):
    return render(request, 'dublinbuspredict/map.html')

def connections(request):
    return render(request, 'dublinbuspredict/connections.html')

def contact(request):
    return render(request, 'dublinbuspredict/contact.html')

def tourism(request):
    return render(request, 'dublinbuspredict/tourism.html')

def tickets_fares(request):
    return render(request, 'dublinbuspredict/tickets_fares.html')

def sampleQuery(rows):
    # Connect to database using these credentials.
    global route_id, source_id, destination_id, stops_destination_2
    global direction
    return HttpResponse(json.dumps({'data': stops_destination_2}), content_type="application/json")

def get_stops_starting_from_source(request):
    source_id = request.GET.get('source')
    db = MySQLdb.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    cursor.execute("select distinct(route_id), direction "
                   "from summerProdb.bus_timetable where stop_id ='" + str(source_id) + "';")
    rows = cursor.fetchall()
    getting_stops = []
    for i in rows:
        cursor.execute("select distinct(stop_id), stop_sequence from summerProdb.bus_timetable where route_id='" + str(i[0]) + "' and direction='"+ str(i[1]) + "';")
        result = cursor.fetchall()
        found = False
        for i in result:
            if str(i[0]) == str(source_id):
                found = True
            elif found:
                if i[0] not in getting_stops and i[1] > result[0][1]:
                    getting_stops.append(i[0])
    db.close()
    getting_stops = sorted(getting_stops)
    return HttpResponse(json.dumps({'stops': getting_stops}), content_type="application/json")

def get_stops_dest_extra_route(request):
    source_id = request.GET.get('source')
    dest_id = request.GET.get('dest')
    db = MySQLdb.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    cursor.execute("select distinct(route_id) "
                   "from summerProdb.bus_timetable where stop_id ='" + str(source_id) + "';")
    rows = cursor.fetchall()
    routes = []
    for i in rows:
        routes.append(i[0])
    cursor.execute("select distinct(route_id) "
                   "from summerProdb.bus_timetable where stop_id='" + str(dest_id) + "'order by bus_timetable.route_id + 0;")
    rows2 = cursor.fetchall()
    routes2 = []
    for i in rows2:
        routes2.append(i[0])
    routes3 = []
    for i in routes:
        if i in routes2:
            cursor.execute("select accum_dist "
                "from summerProdb.bus_timetable where stop_id='" + str(source_id) + "' AND route_id='" + str(i) + "' ORDER BY bus_timetable.stop_sequence limit 1;")
            distance_src = cursor.fetchall()
            cursor.execute("select accum_dist "
                "from summerProdb.bus_timetable where stop_id='" + str(dest_id) + "' AND route_id='" + str(i) + "' and accum_dist > 0 ORDER BY bus_timetable.stop_sequence limit 1;")
            distance_dst = cursor.fetchall()
            if distance_dst != () and distance_src != ():
                if distance_dst[0][0] > distance_src[0][0]:
                    distance = (distance_dst[0][0] - distance_src[0][0])
                elif distance_dst[0][0] < distance_src[0][0]:
                    distance = (distance_src[0][0] - distance_dst[0][0])
                if distance >= 0:
                    distance = round(distance, 1)
                    routes3.append((i, distance))
    routes3 = sorted(routes3, key=lambda x: x[1])
    return HttpResponse(json.dumps({'routes': routes3}), content_type="application/json")

def run_queries(request):
    global list_stops, time, route_id, source_id, destination_id, direction, date
    global bus1, bus2, bus3, stops1, stops2, stops3, busNumber
    global stops_destination_1
    list_stops = time_date.get_all_stops(time, route_id, source_id, destination_id, date, direction)
    bus1, bus2, bus3 = 0, 0, 0
    stops1, stops2, stops3 = [], [], []
    bus1 = list_stops[0][0]
    stops1 = list_stops[1]
    if len(list_stops[0]) == 2 or len(list_stops[0]) == 3:
        bus2 = list_stops[0][1]
        stops2 = list_stops[2]
    if len(list_stops[0]) == 3:
        bus3 = list_stops[0][2]
        stops3 = list_stops[3]
    busNumber = 0
    return HttpResponse(json.dumps({'list_stops': list_stops,'stops':stops_destination_1}), content_type="application/json")

# Function for loading basic tourist page info
def get_tourist(request):
    db = pymysql.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    query = "SELECT * FROM tourism;"
    cursor.execute(query)
    touristData = cursor.fetchall()
    return HttpResponse(json.dumps({'data': touristData}), content_type="application/json")

# Function for loading routes that go to stops surrounding tourist attractions
def get_tourist_routes(request):
    db = pymysql.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    query = "SELECT * FROM tourism_routes;"
    cursor.execute(query)
    stop_data = cursor.fetchall()
    return HttpResponse(json.dumps({'data': stop_data}), content_type="application/json")

# Scrapes AA roadwatch twitter for dublin traffic data. Sends to urls for display in 9 divs using JS. 
def get_TwitterAPIAARoadwatch(request):
    base_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=aaroadwatch&count=100'
    CONSUMER_KEY = 'wJx7TMGnDB5glAeRVZeMeqBCi'
    CONSUMER_SECRET = 'Iri0sl7eg1lDGFHViCAdC2XcuhgUXaERRzSX1EdunQOvVLnkkg'
    ACCESS_TOKEN_KEY = '876448778223579137-PMiTnrAgI5BQE7swQ0851A3SxyWQNWk'
    ACCESS_TOKEN_SECRET = 'qTQafqyMIbmpqpPj639wU8m0k564RCKPmeEpJW6OFz7NA'
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    # Makes the call to the API
    response = requests.get(base_url, auth=auth)
    results = response.json()
    text=[]
    create_time=[]
 
    for i in results:
        if 'DUBLIN' in i['text'] or 'Luas' in i['text']:
         create_time.append(i['created_at'])
         text.append(i['text'])
    return HttpResponse(json.dumps({'create_time': create_time,'text':text}), content_type="application/json")

def set_stops_for_maps(request):
    global stops_destination_1, stops_destination_2
    route = request.GET.get('route')
    source = request.GET.get('source')
    dest = request.GET.get('dest')
    db = MySQLdb.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    cursor.execute("SELECT bus_timetable.trip_id "
                   "FROM bus_timetable, bus_stops "
                   "WHERE bus_timetable.stop_id = '" + str(source) + "' AND bus_timetable.route_id = '" + str(route) + "' limit 1;")
    trip_id = cursor.fetchall()[0][0]
    cursor.execute("SELECT bus_timetable.stop_id, bus_stops.lat, bus_stops.lon, bus_stops.long_name, bus_stops.name, bus_timetable.accum_dist "
                   "FROM bus_timetable, bus_stops "
                   "WHERE bus_timetable.route_id = '" + str(route) + "' AND bus_timetable.trip_id = '" + str(trip_id) + "' AND bus_timetable.stop_id = bus_stops.stop_id "
                   "ORDER BY bus_timetable.stop_sequence;")
    rows = cursor.fetchall()
    db.close()
    stops = []
    stops2 = []
    found = False
    for i in rows:
        if str(i[0]) == str(source):
            found = True
            stops.append(i)
            stops2.append(i)
            continue
        if found:
            stops.append(i)
            stops2.append(i)
        if str(i[0]) == str(dest):
            break
    stops_destination_1 = stops
    stops_destination_2 = stops2
    return HttpResponse(json.dumps({'ok':'ok'}), content_type='application/json')
