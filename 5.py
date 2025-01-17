import sqlite3

# Connect to the database
conn = sqlite3.connect('src/alchemy_data.db')  # Update with your database path
cursor = conn.cursor()

# Execute the DELETE query
cursor.execute("DELETE FROM alchemy_data WHERE experiment_id = 5")
conn.commit()

# Confirm deletion
print("Experiment 5 data has been deleted.")

# Close the connection
conn.close()
