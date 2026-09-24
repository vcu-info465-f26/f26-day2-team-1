import sqlite3

# connects to the database
connection = sqlite3.connect("project.db")

# compares earthquakes based on their depth
query = """
SELECT
    CASE
        WHEN d.depth_km < 40 THEN 'Shallow'
        ELSE 'Deep'
    END AS depth_group,
    COUNT(*) AS earthquake_count,
    AVG(d.significance) AS average_significance,
    AVG(e.magnitude) AS average_magnitude
FROM earthquakes e
JOIN earthquake_details d
    ON e.id = d.event_id
GROUP BY depth_group;
"""

# runs the query and gets the results
results = connection.execute(query).fetchall()

print("Earthquake Depth Comparison")
print()

# prints the results for each depth group
for row in results:
    print("Group:", row[0])
    print("Count:", row[1])
    print("Average significance:", round(row[2], 2))
    print("Average magnitude:", round(row[3], 2))
    print()

# separates the shallow and deep results
shallow = [row for row in results if row[0] == "Shallow"][0]
deep = [row for row in results if row[0] == "Deep"][0]

print("Conclusion:")

# compares the average magnitude of the two groups
if shallow[3] > deep[3]:
    print("Shallow earthquakes had a higher average magnitude than deep earthquakes.")
elif shallow[3] < deep[3]:
    print("Deep earthquakes had a higher average magnitude than shallow earthquakes.")
else:
    print("Shallow and deep earthquakes had the same average magnitude.")

# closes the database connection
connection.close()