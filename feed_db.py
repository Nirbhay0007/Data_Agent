import psycopg2
from psycopg2 import sql 
from dotenv import load_dotenv





import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",       # Default user
        password="1234",       # Matches POSTGRES_PASSWORD in your Docker settings
        dbname="postgres"      # Default database
    )
    print("Database connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")