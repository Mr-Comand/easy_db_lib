import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None
        self.connect()
        
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            print("Connection successful")
        except Exception as e:
            print(f"An error occurred while connecting to the database: {e}")
            exit()

   
    def check_connection(self):
        if self.conn is None or self.conn.closed != 0:
            print("Connection lost. Reconnecting...")
            self.connect()

    def execute(self, query, params=None):
        self.check_connection()
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            if self.cursor.description:
                return self.cursor.fetchall()
            return None
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            self.conn.rollback()
            return None
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Connection closed")
    
# Usage example:
if __name__ == "__main__":
    db = Database()
    db.close()