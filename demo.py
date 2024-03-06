import sqlite3

# Connect to SQLite database (or create if not exists)
conn = sqlite3.connect('blueprint.db')
cursor = conn.cursor()

# Create the "options" table
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY,
        "Project-name" TEXT,
        "Brd-generator" TEXT,
        "Use-cases" TEXT,
        "test-cases" TEXT,
        "test-scripts" TEXT,
        "Boiler-templete" TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Table 'options' created successfully.")
