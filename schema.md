# API Schema

## Earthquakes

| Field     | Type      | What it is                    |
| --------- | --------- | ----------------------------- |
| id        | String    | ID for the earthquake         |
| location  | String    | Where the earthquake happened |
| magnitude | Number    | Magnitude of the earthquake   |
| time      | Date/Time | When the earthquake happened  |
| latitude  | Number    | Latitude of the earthquake    |
| longitude | Number    | Longitude of the earthquake   |

## Regions

| Field     | Type   | What it is                        |
| --------- | ------ | --------------------------------- |
| country   | String | Country the earthquake is in      |
| iso       | String | Country code                      |
| region    | String | Region the earthquake is in       |
| latitude  | Number | Latitude used to find the region  |
| longitude | Number | Longitude used to find the region |

## Relational Key

The two tables can be connected using the **latitude and longitude**. The earthquake data gives us the coordinates, and we can use those coordinates with the Regions API to get the region information.

The earthquake `id` is used to identify each earthquake, but it isn't what connects the two tables.

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
     | latitude + longitude
     |
     v
Regions
-------
country
iso
region
latitude
longitude
```
