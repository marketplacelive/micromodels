import sqlite3

conn = sqlite3.connect("action_data.db")
cursor = conn.cursor()

try:
    # Add the category_id column
    cursor.execute("ALTER TABLE action_list ADD COLUMN category_id INTEGER")
    cursor.execute("ALTER TABLE action_list ADD COLUMN opportunity_id TEXT")

    opportunity_ids = {
        "Vodafone":"006Hs00001DHMVAIA5",
        "Siemens":"006Hs00001DHMV9IAP",
        "American Airlines":"006Hs00001DHMVBIA5",
        "Walmart":"006Hs00001DHMXyIAP",
        "Ericsson":"006Hs00001DHMYmIAP"
    }


    # Create a dictionary to map categories to unique IDs
    category_ids = {}

    # Loop through each row in the action_list table
    rows = cursor.execute("SELECT DISTINCT(category) FROM action_list").fetchall()
    category_id = 1
    for row in rows:
        category = row[0]  # Get existing ID or None
        if category not in category_ids.values():
            category_ids[category] = category_id
        else:
            category_id = category_ids[category]

        cursor.execute("UPDATE action_list SET category_id = ? WHERE category = ?", (category_id, category))
        conn.commit()
        category_id = max(category_ids.values())+1
    for opp, opp_id in opportunity_ids.items():
        cursor.execute("UPDATE action_list SET opportunity_id = ? WHERE account_name = ?", (opp_id, opp))
        conn.commit()
except sqlite3.Error as error:
    print("Error while executing SQL:", error)
finally:
    conn.close()

print("Column added and populated successfully!")