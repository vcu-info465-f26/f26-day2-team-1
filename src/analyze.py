import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "project.db"

query = """
SELECT
    CASE
        WHEN d.depth_km < 30 THEN 'Shallow (< 30 km)'
        ELSE 'Deep (>= 30 km)'
    END AS depth_group,
    COUNT(*) AS earthquake_count,
    AVG(d.significance) AS average_significance,
    AVG(e.magnitude) AS average_magnitude
FROM earthquakes AS e
INNER JOIN earthquake_details AS d
    ON e.id = d.event_id
WHERE d.depth_km IS NOT NULL
  AND d.significance IS NOT NULL
  AND e.magnitude IS NOT NULL
GROUP BY depth_group
ORDER BY CASE WHEN d.depth_km < 30 THEN 1 ELSE 2 END;
"""

with sqlite3.connect(DATABASE_PATH) as connection:
    results = connection.execute(query).fetchall()

print("Earthquake Depth Comparison\n")

for row in results:
    print("Group:", row[0])
    print("Count:", row[1])
    print("Average significance:", round(row[2], 2))
    print("Average magnitude:", round(row[3], 2))
    print()

groups = {row[0]: row for row in results}
shallow = groups.get("Shallow (< 30 km)")
deep = groups.get("Deep (>= 30 km)")

print("Conclusion:")

if shallow and deep:
    if shallow[2] > deep[2]:
        print("Shallow earthquakes had higher average significance than deep earthquakes.")
    elif shallow[2] < deep[2]:
        print("Deep earthquakes had higher average significance than shallow earthquakes.")
    else:
        print("Shallow and deep earthquakes had the same average significance.")

    print(
        f"Average magnitude was {shallow[3]:.2f} for shallow earthquakes "
        f"and {deep[3]:.2f} for deep earthquakes."
    )
else:
    print("Only one depth group was present in the joined data.")