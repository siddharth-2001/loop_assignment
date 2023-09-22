import pandas as pd
import pytz
from store.models import Store, StoreStatus, BusinessHours, Timezone
from datetime import datetime, timedelta, timezone
from django.db import transaction
from .models import Report

from .timeline import Timeline, Event

g_timenow_hardcoded = '2023-01-25 18:13:22.47922 UTC'
g_format = "%Y-%m-%d %H:%M:%S.%f UTC"
g_utc_datetime = datetime.strptime(g_timenow_hardcoded, g_format)
g_utc_datetime_hardcoded = pytz.utc.localize(g_utc_datetime)

def process_timeline(p_timeline):

    l_event_list = p_timeline.event_list

    l_uptime = timedelta()
    l_downtime = timedelta()

    l_last_event = None

    for event in l_event_list:

        if l_last_event is None and event.status == 'open':
            l_last_event = event
            continue

        elif l_last_event is None:
            continue

        if l_last_event.status == 'close' and event.status != 'open':
            continue

        # elif l_last_event.status != 'close' and event.status != 'close':
        else:

            if l_last_event.status == 'active' or l_last_event.status == 'open':
                l_uptime += event.time - l_last_event.time

            elif l_last_event.status == 'inactive':
                l_downtime += event.time - l_last_event.time

            l_last_event = event
                
    return l_uptime, l_downtime


def trigger_report(p_report_id):

    l_stores = Store.objects.all()
    l_df_data = []
    for store in l_stores:
        l_df_data.append(generate_report(store.store_id))

    l_df = pd.DataFrame.from_dict(l_df_data)
    
    l_df.to_csv('static/report.csv', index=False, header=True)
    l_report = Report.objects.get(report_id = p_report_id)
    l_report.status = 'complete'
    l_report.save()


    


def generate_report(p_store_id):

    l_store = Store.objects.get(store_id=p_store_id)

    l_store_timezone = 'America/Chicago'

    try:
        l_store_timezone = Timezone.objects.get(store=l_store)

    except:
        pass

    l_week_timeline = generate_timeline(l_store, l_store_timezone, 7, 0)
    l_day_timeline = generate_timeline(l_store, l_store_timezone, 1, 0)
    l_hour_timeline = generate_timeline(l_store, l_store_timezone, 0, 1)

    l_week_uptime, l_week_downtime = process_timeline(l_week_timeline)
    l_day_uptime, l_day_downtime = process_timeline(l_day_timeline)
    l_hour_uptime, l_hour_downtime = process_timeline(l_hour_timeline)

    l_dict = {}

    l_dict['store_id'] = p_store_id
    l_dict['uptime_last_hour(in mins)'] = l_hour_uptime.total_seconds()/60
    l_dict['uptime_last_day(in hours)'] = l_day_uptime.total_seconds()/3600
    l_dict['uptime_last_week(in hours)'] = l_week_uptime.total_seconds()/3600
    l_dict['downtime_last_hour(in mins)'] = l_hour_downtime.total_seconds()/60
    l_dict['downtime_last_day(in hours)'] = l_day_downtime.total_seconds()/3600
    l_dict['downtime_last_week(in hours)'] = l_week_downtime.total_seconds()/3600

    return l_dict


def generate_timeline(p_store, p_timezone,p_days,p_hours):

    l_business_hours = BusinessHours.objects.filter(store=p_store)

    l_polls = StoreStatus.objects.filter(store=p_store)

    l_timeline = Timeline(
        start=g_utc_datetime_hardcoded - timedelta(days=p_days, hours=p_hours),
        end=g_utc_datetime_hardcoded
    )
    
    #if no data for business hours assume store is open 24*7
    if len(l_business_hours) == 0:

        l_timeline.add_event(Event(time=g_utc_datetime_hardcoded- timedelta(days=p_days, hours=p_hours), status='open'))
        l_timeline.add_event(Event(time=g_utc_datetime_hardcoded, status = 'close'))


    for x in l_business_hours:

        try:
            
            l_open = Event(time=convert_local_time_to_utc(x.day_of_week, x.start_time_local, p_timezone),status='open')
            l_close = Event(time=convert_local_time_to_utc(x.day_of_week, x.end_time_local, p_timezone),status='close')

            if l_open.time > l_timeline.start_time and l_open.time < l_timeline.end_time:
                l_timeline.add_event(new_event=l_open)
            if l_close.time > l_timeline.start_time and l_close.time < l_timeline.end_time:
                l_timeline.add_event(new_event=l_close)

        except Exception as e:
            print(e)

    for poll in l_polls:

        if poll.timestamp_utc < l_timeline.start_time or poll.timestamp_utc > l_timeline.end_time:
            continue

        l_timeline.add_event(Event(time=poll.timestamp_utc, status=poll.status))

    l_timeline.sort_timeline()

    return l_timeline


def populate_database():

    # iterate through the rows and add store objects in a batch
    l_stores = set()

    l_data_frame = pd.read_csv('static/store status.csv')
    populate_store_database(l_data_frame, l_stores)

    l_data_frame = pd.read_csv('static/hours.csv')
    populate_store_database(l_data_frame, l_stores)

    l_data_frame = pd.read_csv('static/timezone.csv')
    populate_store_database(l_data_frame, l_stores)

    del l_stores
    # Iterate through the rows and then add store status

    l_data_frame = pd.read_csv('static/store status.csv')
    populate_status_database(l_data_frame)

    l_data_frame = pd.read_csv('static/hours.csv')
    populate_business_hours_database(l_data_frame)

    l_data_frame = pd.read_csv('static/timezone.csv')
    populate_timezone_database(l_data_frame)



def populate_timezone_database(p_data_frame):

    l_object_list = []

    for id, row in p_data_frame.iterrows():

        try:
            l_object_list.append(
                Timezone(
                    store_id=row['store_id'],
                    timezone_str=row['timezone_str']
                )
            )

        except Exception as e:
            print(e)

    Timezone.objects.bulk_create(
        l_object_list,
        update_conflicts=True,
        update_fields=['timezone_str'],
        unique_fields=['store_id']
    )
    del l_object_list


def populate_status_database(p_data_frame):
    l_object_list = []

    for id, row in p_data_frame.iterrows():

        try:

            l_utc_timezone = pytz.utc
            l_format = "%Y-%m-%d %H:%M:%S.%f UTC"
            l_utc_datetime = datetime.strptime(row['timestamp_utc'], l_format)
            l_utc_datetime = l_utc_timezone.localize(l_utc_datetime)

            l_object_list.append(StoreStatus(store_id=row['store_id'],
                                             status_id=str(
                                                 row['store_id']) + str(l_utc_datetime),
                                             timestamp_utc=l_utc_datetime,
                                             status=row['status']))

        except Exception as e:
            print(e)

        if len(l_object_list) == 99999:

            StoreStatus.objects.bulk_create(l_object_list, update_conflicts=True, unique_fields=['status_id'], update_fields=['status'])
            l_object_list.clear()

    del l_object_list


def populate_business_hours_database(p_data_frame):

    l_object_list = []

    for id, row in p_data_frame.iterrows():

        try:

            l_object_list.append(
                BusinessHours(
                    hours_id=str(row['store_id']) +
                    'day_of_week' + str(row['day']),
                    store_id=row['store_id'],
                    day_of_week=row['day'],
                    start_time_local=row['start_time_local'],
                    end_time_local=row['end_time_local'],
                )
            )

        except Exception as e:
            print(e)

    BusinessHours.objects.bulk_create(
        l_object_list,
        update_conflicts=True,
        update_fields=['start_time_local', 'end_time_local'],
        unique_fields=['hours_id']
    )

    del l_object_list


def populate_store_database(p_data_frame, p_stores):

    l_object_list = []

    for id, row in p_data_frame.iterrows():

        try:
            if row['store_id'] not in p_stores:

                l_object_list.append(
                    Store(store_id=row['store_id'],
                          created_at=pytz.utc.localize(datetime.now()))
                )

                p_stores.add(row['store_id'])

        except Exception as e:
            print(e)

    Store.objects.bulk_create(l_object_list, update_conflicts=True, unique_fields=[
                              'store_id'], update_fields=['created_at'])


def convert_local_time_to_utc(day_index, local_time, timezone_str):

    # Define the timezone
    local_timezone = pytz.timezone(timezone_str)

    # Get the current date and time in the local timezone
    current_datetime = g_utc_datetime_hardcoded.astimezone(local_timezone)

    # Find the most recent occurrence of the specified day
    last_occurrence = current_datetime - \
        timedelta(days=(current_datetime.weekday() - day_index) % 7)

    # Combine the date from the last occurrence with the provided local time
    combined_datetime = datetime(last_occurrence.year, last_occurrence.month, last_occurrence.day,
                                 local_time.hour, local_time.minute)

    combined_datetime = local_timezone.localize(combined_datetime)

    # Convert to UTC
    utc_time = combined_datetime.astimezone(pytz.utc)

    return utc_time
