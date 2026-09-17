# Team 1 API Choice

**API:** USGS Earthquake Catalog API

**Endpoint 1:** Recent earthquake query using the USGS FDSN Event query service with GeoJSON format, a minimum magnitude of 2.5, results ordered by time, and a limit of 10 earthquakes.

**Endpoint 2:** Specific earthquake detail query using the USGS FDSN Event query service with an earthquake event ID.

**Connection:** Both calls use the earthquake event ID, so we can use the ID from the recent earthquake results to retrieve and connect the detailed information for the same earthquake.
## Sprint 1 Team Workflow

- Project Manager: Danny Truong
- Approval Rotation: Joshua → Danny → Hira → Vishvag → Joshua
- Tester: Vishvag

## Sprint 1 Statement

By September 24, we can answer one real question about whether shallow earthquakes feel stronger than deeper ones by running a SQL query across data our own code has been collecting since September 10.