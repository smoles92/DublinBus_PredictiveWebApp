from .locate_bus import central, get_buses
from datetime import datetime, timedelta
from .model_prototype_1 import model

import pandas as pd
pd.options.mode.chained_assignment = None
from sklearn.externals import joblib
from dateutil import parser
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except:
    pass

def holidays(date):
    publicholidays_2017 = ['2017-08-07', '2017-10-30', '2017-12-25', '2017-12-26',
                        '2017-12-27']
    schoolholidays_2017 = ['2017-07-07', '2017-08-07', '2017-09-07', '2017-10-07',
                        '2017-11-07', '2017-12-07', '2017-07-13', '2017-07-14',
                        '2017-07-15', '2017-07-16', '2017-07-17', '2017-07-18',
                        '2017-07-19', '2017-07-20', '2017-07-21', '2017-07-22',
                        '2017-07-23', '2017-07-24', '2017-07-25', '2017-07-26',
                        '2017-07-27', '2017-07-28', '2017-07-29', '2017-07-30',
                        '2017-07-31', '2017-01-08', '2017-02-08', '2017-03-08',
                        '2017-04-08', '2017-05-08', '2017-06-08', '2017-07-08',
                        '2017-08-08', '2017-09-08', '2017-10-08', '2017-11-08',
                        '2017-12-08', '2017-08-13', '2017-08-14', '2017-08-15',
                        '2017-08-16', '2017-08-17', '2017-08-18', '2017-08-19',
                        '2017-08-20', '2017-08-21', '2017-08-22', '2017-08-23',
                        '2017-08-24', '2017-08-25', '2017-08-26', '2017-08-27',
                        '2017-08-28', '2017-08-29', '2017-08-30', '2017-08-31',
                        '2017-10-28', '2017-10-29', '2017-10-30', '2017-10-31',
                        '2017-01-11', '2017-02-11', '2017-03-11', '2017-04-11',
                        '2017-05-11', '2017-12-23', '2017-12-24', '2017-12-25',
                        '2017-12-26', '2017-12-27', '2017-12-28', '2017-12-29',
                        '2017-12-30', '2017-12-31']
    date = date[6:10] + '-' + date[3:5] + '-' + date[:2]
    p_holiday = False
    s_holiday = False
    if date in publicholidays_2017:
        p_holiday = True
    if date in schoolholidays_2017:
        s_holiday = True
    return p_holiday, s_holiday


def time_to_arrive(datetime, sec):
    new_time = datetime + timedelta(seconds=sec)
    new_time = new_time.strftime('%d/%m/%Y %H:%M:%S')
    return new_time


def get_trip_id(bus_route, stop_id, arrival_time, day):
    db = pymysql.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    if day < 5:
        d = 'business_day'
    elif day == 5:
        d = 'saturday'
    elif (day == 6): #or (p_holiday == True):
        d = 'sunday'
    rows2 = ()
    while rows2 == ():
        cursor.execute('SELECT DISTINCT trip_id FROM bus_timetable WHERE bus_timetable.route_id = "' + str(bus_route) + '" AND bus_timetable.stop_id = "' + str(stop_id) + '" AND bus_timetable.arrival_time >= "' + str(arrival_time)[11:] + '" AND bus_timetable.day_of_week = "' + d + '" ORDER BY bus_timetable.arrival_time ASC LIMIT 1;')
        rows2 = cursor.fetchall()
        if rows2 == ():
            arrival_time = str(parser.parse(arrival_time) - datetime.timedelta(minutes=2))
    return rows2[0]

def main(bus_route, source_stop, destination_stop, direction, position):
    info = central(bus_route, source_stop, destination_stop, direction, position)
    trip_id = get_trip_id(bus_route, source_stop, info[len(info)-1][0]['arrival'], datetime.weekday(parser.parse(info[len(info)-1][0]['arrival'])))
    with open("C:\\Users\\steph\\OneDrive\\Desktop\\trained_modelv10.pkl", "rb") as f:
        rtr = joblib.load(f)
    if type(info) == str:
        return info
    for j in range(len(info) - 1, -1, -1):
        hour = 0
        if j == len(info) - 1:
            hour = info[j][0]['arrival']
            weekday = datetime.weekday(parser.parse(info[j][0]['arrival']))
            holiday = holidays(info[j][0]['arrival'])
        else:
            hour = info[j + 1][0]['arrival']
            weekday = datetime.weekday(parser.parse(info[j + 1][0]['arrival']))
            holiday = holidays(info[j + 1][0]['arrival'])
        p_holiday = holiday[0]
        s_holiday = holiday[1]
        info[j][0]['duration'] = model(bus_route, info[j][0]['stopid'], hour, weekday, p_holiday, s_holiday, rtr, trip_id)[0]
        if j == len(info) - 1: 
            info[j][0]['arrival'] = (time_to_arrive(parser.parse(info[j][0]['arrival']), info[j][0]['duration']))
        else:
            info[j][0]['arrival'] = (time_to_arrive(parser.parse(info[j + 1][0]['arrival']), info[j][0]['duration']))
        if str(info[j][0]['stopid']) == source_stop:
            info[j][0]['status'] = 'src'
        elif str(info[j][0]['stopid']) == destination_stop:
            info[j][0]['status'] = 'dest'
        else:
            info[j][0]['status'] = 'normal'
    found = False
    clean = []
    for i in range(len(info) - 1, -1, -1):
        if str(info[i][0]['stopid']) == str(source_stop):
            found = True
        if found:
            clean.append(info[i])
    return clean
