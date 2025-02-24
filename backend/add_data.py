import cx_Oracle
import json
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch database connection details from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME")

# Ensure environment variables are set
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE_NAME]):
    raise ValueError("Missing one or more required environment variables for DB connection.")

# Database connection details
dsn_tns = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE_NAME)
connection = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn_tns)
cursor = connection.cursor()

# Load data from JSON file
with open("new_data.json", "r") as file:
    data = json.load(file)

import re

def format_value(value):
    if value is None:
        return "NULL"
    elif isinstance(value, str):
        # Check if the value is in the ISO 8601 date format (YYYY-MM-DD)
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return f"TO_DATE('{value}', 'YYYY-MM-DD')"  # ✅ Correct date format for Oracle
        elif re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?", value):
            # Handle timestamps
            value = value.split("+")[0].split("Z")[0]  # Remove timezone info
            return f"TO_TIMESTAMP('{value}', 'YYYY-MM-DD\"T\"HH24:MI:SS.FF')"
        else:
            return "'{}'".format(value.replace("'", "''"))  # Escape single quotes
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        raise ValueError(f"Unsupported data type: {type(value)}")


# Iterate through tables and insert data
for table_name, rows in data.items():
    print(f"Inserting data into table: {table_name}")
    for row in rows:
        columns = ", ".join(row.keys())
        values = ", ".join(format_value(value) for value in row.values())
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        try:
            cursor.execute(insert_query)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            print(f"Error inserting into table {table_name}: {error.message}")
            print(f"Query: {insert_query}")
    
    print(f"Data inserted successfully for table: {table_name}")

# Commit the transaction
connection.commit()

# Close the connection
cursor.close()
connection.close()
