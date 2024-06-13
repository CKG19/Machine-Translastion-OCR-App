import mysql.connector
import pandas as pd

dbconfig = {
    'host'      : 'DB_HOST',
    'user'      : 'DB_USER',
    'password'  : 'DB_PASSWORD',
    'database'  : 'DB_NAME'
}

class TranslationApplicationDatabase:
    def __init__(self, host=dbconfig['host'], database=dbconfig['database'], user=dbconfig['user'], password=dbconfig['password']):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.conn = self.connection()
        self.cursor = self.create_cursor()

    def connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
    
    def create_cursor(self):
        return self.conn.cursor()
    
    def close_connection(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def execute_query(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        if query.strip().upper().startswith("SELECT"):
            result = self.cursor.fetchall()
            return result
        else:
            self.commit()

    def authenticate_admin(self, username, password):
        query = """
                SELECT COUNT(*) 
                FROM admin 
                WHERE username = %s AND password = %s;
                """
        params = (username, password)
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()[0]
        return result > 0

    def insert_translation_history(self, input, output):
        query = """
                INSERT INTO translation_history (translation_input, translation_output)
                VALUES (%s, %s);
                """
        params = (input, output)
        self.execute_query(query, params)

    def read_translation_history(self):
        query = """
                SELECT *
                FROM translation_history
                """
        result = self.execute_query(query)
        return result
    
    def delete_translation_history(self, history_translation_id):
        query = """
                DELETE FROM translation_history
                WHERE translation_history_id = %s;
                """
        params = (history_translation_id,)
        self.execute_query(query, params)

    def update_translation_history(self, history_translation_id, translation_input, translation_output):
        query = """
                UPDATE translation_history
                SET translation_input = %s, translation_output = %s
                WHERE translation_history_id = %s;
                """
        params = (translation_input, translation_output, history_translation_id)
        self.execute_query(query, params)
