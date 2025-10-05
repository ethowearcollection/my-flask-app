import psycopg2
from psycopg2 import sql

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="userdb",
            user="your_username",
            password="your_password",
            host="localhost",
            port="5432"
        )
        print("Database connected successfully")
        return conn
    except Exception as e:
        print("Error connecting to database:", e)
        return None