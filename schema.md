# API Schema

## Earthquakes

| Field     | Type      | What it is                    |
| --------- | --------- | ----------------------------- |
| id        | String    | ID for the earthquake         |
| location  | String    | Where the earthquake happened |
| magnitude | Number    | Earthquake magnitude          |
| time      | Date/Time | When the earthquake happened  |
| latitude  | Number    | Latitude of the earthquake    |
| longitude | Number    | Longitude of the earthquake   |

## Earthquake Details

| Field          | Type   | What it is                       |
| -------------- | ------ | -------------------------------- |
| event_id       | String | ID of the earthquake             |
| status         | String | Current status of the earthquake |
| tsunami        | Number | Whether a tsunami was reported   |
| significance   | Number | USGS significance value          |
| stations       | Number | Number of stations used          |
| magnitude_type | String | Type of magnitude measurement    |
| depth_km       | Number | Depth of the earthquake          |

## How They Connect

The `id` from the Earthquakes endpoint is used as the `event_id` for the Earthquake Details endpoint. This lets us take a specific earthquake from the first endpoint and use its ID to get more information about that same earthquake.

```text
Earthquakes
-----------
id
location
magnitude
time
latitude
longitude
     |
     | id → event_id
     |
     v
Earthquake Details
------------------
event_id
status
tsunami
significance
stations
magnitude_type
depth_km
```
