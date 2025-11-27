import psycopg2
from psycopg2 import pool
import sys

class Database:
    """Manages database connection and cursor operations"""
    
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                dbname="Final Project",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
            print("Database connection established successfully.")
        except psycopg2.Error as e:
            print(f"Failed to connect to database: {e}")
            sys.exit(1)
    
    def get_cursor(self):
        """Returns the database cursor"""
        return self.cursor
    
    def get_connection(self):
        """Returns the database connection"""
        return self.connection
    
    def commit(self):
        """Commits the current transaction"""
        self.connection.commit()
    
    def rollback(self):
        """Rolls back the current transaction"""
        self.connection.rollback()
    
    def close(self):
        """Closes cursor and connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")