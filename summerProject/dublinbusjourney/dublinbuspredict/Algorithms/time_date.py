try:
    import pymysql
    pymysql.install_as_MySQLdb()
except:
    pass
from datetime import timedelta
from .model_prototype_1 import model
import pandas as pd
pd.options.mode.chained_assignment = None
from sklearn.externals import joblib
from dateutil import parser
from datetime import datetime

def day(date):
    weekday = datetime.weekday(parser.parse(date))
    if weekday < 5:
        weekday = 'business_day'
    elif weekday == 5:
        weekday = 'saturday'
    elif weekday == 6:
        weekday = 'sunday'
    return weekday

def get_all_stops(time, bus_route, source_stop, destination_stop, date, direction):
    holiday = holidays(date)
    p_holiday = holiday[0]
    s_holiday = holiday[1]
    direction = direction

    query_day = day(date)
    if p_holiday:
        query_day = 'sunday'
    db = pymysql.connect(user='lucas', db='summerProdb', passwd='hello_world', host='csi6220-3-vm3.ucd.ie')
    cursor = db.cursor()
    rows1 = ()
    sql1 = """SELECT bus_timetable.trip_id
                FROM bus_timetable WHERE bus_timetable.arrival_time >= time_format('{q1time}','%T')
                AND bus_timetable.route_id = '{qbus_route}'
                AND bus_timetable.stop_id = '{qsource_stop}'
                AND bus_timetable.day_of_week = '{qquery_day}'
                AND bus_timetable.direction = '{qdirection}'
                ORDER BY bus_timetable.arrival_time ASC
                LIMIT 3"""

    cursor = db.cursor()
    while rows1 == ():
        cursor.execute(sql1.format(q1time=str(time),qbus_route=str(bus_route),\
                               qsource_stop=str(source_stop), qquery_day=str(query_day), qdirection=str(direction)))
        rows1 = cursor.fetchall()
        if direction == 0:
            direction = 1
        elif direction == 1:
            direction = 0
    print('1', rows1)
    # Create query for the first prediction
    sql2 = """SELECT time_format(bus_timetable.arrival_time,'%T') , bus_timetable.stop_id, bus_timetable.stop_sequence, bus_stops.long_name, bus_timetable.accum_dist
            FROM bus_timetable, bus_stops WHERE trip_id = '{qtrip_id}'
            AND bus_timetable.arrival_time >= '{q2time}' AND bus_timetable.stop_id = bus_stops.stop_id
            ORDER BY bus_timetable.stop_sequence"""

    cursor = db.cursor()
    cursor.execute(sql2.format(qtrip_id=str(rows1[0][0]),q2time=str(time)))
    rows2 = cursor.fetchall()
    print('2', rows2)
    # get the first predictions for the data model.
    stops1 = src_dest_list(rows2, source_stop, destination_stop)
    # create query for the second prediction
    true_second = False
    true_third = False
    if len(rows1) - 1 == 1 or len(rows1) == 3:
        sql3 = """SELECT time_format(bus_timetable.arrival_time,'%T') , bus_timetable.stop_id, bus_timetable.stop_sequence, bus_stops.long_name, bus_timetable.accum_dist
                FROM bus_timetable, bus_stops WHERE trip_id = '{qtrip_id}'
                AND bus_timetable.arrival_time >= '{q2time}' AND bus_timetable.stop_id = bus_stops.stop_id
                ORDER BY bus_timetable.stop_sequence"""
        cursor = db.cursor()
        cursor.execute(sql3.format(qtrip_id=str(rows1[1][0]),q2time=str(time)))
        rows3 = cursor.fetchall()
        print('3', rows3)
        # get the second prediction for the data model.
        stops2 = src_dest_list(rows3, source_stop, destination_stop)
        true_second = True
    # create query for the third prediction
    if len(rows1) == 3:
        sql4 = """SELECT time_format(bus_timetable.arrival_time,'%T') , bus_timetable.stop_id, bus_timetable.stop_sequence, bus_stops.long_name, bus_timetable.accum_dist
                FROM bus_timetable, bus_stops WHERE trip_id = '{qtrip_id}'
                AND bus_timetable.arrival_time >= '{q2time}' AND bus_timetable.stop_id = bus_stops.stop_id
                ORDER BY bus_timetable.stop_sequence"""
        cursor = db.cursor()
        cursor.execute(sql4.format(qtrip_id=str(rows1[2][0]),q2time=str(time)))
        rows4 = cursor.fetchall()
        print('4', rows4)
        # get the third prediction for the data model.
        stops3 = src_dest_list(rows4, source_stop, destination_stop)
        true_third = True
    db.close()
    if true_third:
        return [rows1, stops1, stops2, stops3]
    elif true_second:
        return [rows1, stops1, stops2]
    else:
        return [rows1, stops1]


def src_dest_list(rows, source, dest):
    stops = []
    found = False
    for i in rows:
        if str(i[1]) == str(source):
            found = True
        if found:
            stops.append([i[1], i[0], i[3], i[4]])
        if str(i[1]) == str(dest):
                break
    return stops


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

def time_date(bus_route, source_stop, destination_stop, date, time, direction, stops, trip_id):
    with open("C:\\Users\\steph\\OneDrive\\Desktop\\trained_modelv10.pkl", "rb") as f:
        rtr = joblib.load(f)
    holiday = holidays(date)
    p_holiday = holiday[0]
    s_holiday = holiday[1]
    weekday = datetime.weekday(parser.parse(date))
    dict = []
    status = 0
    for i in stops:
        if stops.index(i) == 0:
            status = 'src'
        elif stops.index(i) == len(stops) - 1:
            status = 'dest'
        else:
            status = 'normal'
        if stops.index(i) == 0:
            duration = model(bus_route, i[0], str(i[1]), weekday, p_holiday, s_holiday, rtr, trip_id)[0]
            predicted_arrival_time = (time_to_arrive(parser.parse(date + ' ' + str(i[1])), duration))
        else:
            duration = model(bus_route, i[0], dict[len(dict) - 1]['predicted_arrival_time'], weekday, p_holiday, s_holiday, rtr, trip_id)[0]
            predicted_arrival_time = (time_to_arrive(parser.parse(str(dict[len(dict) - 1]['predicted_arrival_time'])), duration))
        dict.append({'stopid':i[0], 'duration':duration, 'predicted_arrival_time':predicted_arrival_time, 'status':status})
    return dict
