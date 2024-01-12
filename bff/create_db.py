import sqlite3
import datetime

# Connect to the database
conn = sqlite3.connect("action_data.db")

# Create the tables with DATETIME for due_before
conn.execute("""CREATE TABLE action (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_name TEXT NOT NULL
)""")

conn.execute("""CREATE TABLE action_list (
    action_id INTEGER NOT NULL,
    account_name TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    due_before DATETIME NOT NULL, 
    FOREIGN KEY (action_id) REFERENCES action(id)
)""")


data = [
    ("An email to John Baker at Vodafone", "Vodafone", "Email", "High", datetime.datetime.strptime("05 Jun 2023 | 3PM", "%d %b %Y | %I%p")),
    ("RFP Exec summary is due", "Siemens", "RFP Review", "High", datetime.datetime.strptime("05 Jun 2023 | 3PM", "%d %b %Y | %I%p")),
    ("You require additional Stakeholder Engagement", "Siemens", "Engagement meeting", "Medium", datetime.datetime.strptime("05 Jun 2023 | 3PM", "%d %b %Y | %I%p")),
    ("Demo session needs to be set up", "American Airlines", "Meeting", "Low", datetime.datetime.strptime("05 Jun 2023 | 3PM", "%d %b %Y | %I%p")),
    ("Move deal from Stage 3 to Stage 4", "Walmart", "Contract Review", "Low", datetime.datetime.strptime("05 Jun 2023 | 3PM", "%d %b %Y | %I%p")),
    ("Ericsson's sentiment score is below average", "Ericsson", "Sentiment", "Low", datetime.datetime.strptime("05 Jun 2023 | 3PM", "%d %b %Y | %I%p")),
    ("Contract view is due", "Ericsson", "Sentiment", "Low", datetime.datetime.strptime("05 Jun 2023 | 3PM", "%d %b %Y | %I%p")),
]

for action_name, _, _, _, _ in data:
    conn.execute("""INSERT INTO action (action_name)
                    VALUES (?)""", (action_name,))

action_ids = [row[0] for row in conn.execute("SELECT id FROM action")]

for action_id, (action, account_name, category, priority, due_before) in zip(action_ids, data):
    conn.execute("""INSERT INTO action_list (action_id, account_name, category, priority, due_before)
                    VALUES (?, ?, ?, ?, ?)""", (action_id, account_name, category, priority, due_before))


conn.commit()
conn.close()

print("Database created and data inserted successfully!")