# Django Restaurant Uptime Monitoring Project

This Django project provides backend APIs to monitor the online status of restaurants during their business hours. It leverages three data sources to generate reports for restaurant owners.

## Problem Statement

Loop monitors several restaurants in the US and needs to monitor if the store is online or not. All restaurants are supposed to be online during their business hours. Due to some unknown reasons, a store might go inactive for a few hours. Restaurant owners want to get a report of how often this happened in the past.

## Data Sources

### 1. Store Activity Data (CSV)

- CSV with columns (`store_id`, `timestamp_utc`, `status`) where status is active or inactive. 
- Timestamps are in UTC.

[Link to CSV](https://drive.google.com/file/d/1UIx1hVJ7qt_6oQoGZgb8B3P2vd1FD025/view?usp=sharing)

### 2. Business Hours Data (CSV)

- Schema: `store_id`, `dayOfWeek` (0=Monday, 6=Sunday), `start_time_local`, `end_time_local`
- Times are in the local time zone.
- If data is missing for a store, assume it is open 24*7.

[Link to CSV](https://drive.google.com/file/d/1va1X3ydSh-0Rt1hsy2QSnHRA4w57PcXg/view?usp=sharing)

### 3. Timezone Data (CSV)

- Schema: `store_id`, `timezone_str`
- If data is missing for a store, assume it is America/Chicago.

[Link to CSV](https://drive.google.com/file/d/101P9quxHoMZMZCVWQ5o-shonk2lgK1-o/view?usp=sharing)


## Data Output Requirement

Generate a report with the following schema:

`store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), update_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)` 

1. Uptime and downtime should only include observations within business hours. 
2. Extrapolate uptime and downtime based on the periodic polls to the entire time interval.


## Considerations/Evaluation Criteria

1. Well-structured code handling corner cases, with a good type system. 
2. Correct functionality for trigger + poll architecture, database reads, and CSV output. 
3. Well-documented logic for computing hours overlap and uptime/downtime.
4. Optimized code that runs within a reasonable amount of time.

## Getting Started

1. Clone the repository.
2. Set up a virtual environment and install dependencies from `requirements.txt`.
3. Configure the Django project with your database settings.
4. Import the provided CSV data into the database.
5. Run the Django server.
6. Access the APIs at the specified endpoints.

## Project Structure


## Usage
1. Trigger the database generation using the `reports/populate` API endpoint.
1. Trigger the report generation using the `reports/trigger_report` API endpoint.
2. Poll the status of the report using the `reports/get_report` API endpoint with the provided `report_id`.
3. Once the report generation is complete, download the CSV file.

## Dependencies

- Django
- Django Rest Framework

