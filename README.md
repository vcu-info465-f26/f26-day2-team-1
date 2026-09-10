# Team 1 API Choice

**API:** USGS Earthquake Catalog API

**Endpoint 1:** Recent earthquake query using the USGS FDSN Event query service with GeoJSON format, a minimum magnitude of 2.5, results ordered by time, and a limit of 10 earthquakes.

**Endpoint 2:** Specific earthquake detail query using the USGS FDSN Event query service with an earthquake event ID.

**Connection:** Both calls use the earthquake event ID, so we can use the ID from the recent earthquake results to retrieve and connect the detailed information for the same earthquake.
