# ==========================================================================
# R.H.E.A. - LONG-TERM MEMORY CORE (MYSQL RAG)
# ==========================================================================

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MemoryCore:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.db_name = os.getenv("DB_NAME", "rhea_memory")
        
        self.connection = None
        self._connect_and_initialize()

    def _connect_and_initialize(self):
        """
        Connects to the MySQL server and ensures the memory database and tables exist.
        """
        try:
            # First connect without specifying a database to create it if it doesn't exist
            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            cursor.close()
            temp_conn.close()

            # Now connect to the actual database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
            
            # Create the memory table with FULLTEXT indexing for our RAG search
            cursor = self.connection.cursor()
            table_query = """
            CREATE TABLE IF NOT EXISTS user_knowledge (
                id INT AUTO_INCREMENT PRIMARY KEY,
                memory_text TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FULLTEXT(memory_text)
            )
            """
            cursor.execute(table_query)
            self.connection.commit()
            cursor.close()
            
            print("[SYSTEM] MySQL Memory Core Online. RAG Database Connected.")
            
        except Error as e:
            print(f"[ERROR] Fatal Database Error. Memory Core Offline: {e}")

    def remember_fact(self, text):
        """
        Saves a new fact to the long-term memory database.
        """
        if not self.connection or not self.connection.is_connected():
            return "Memory core offline. Cannot save data."
            
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO user_knowledge (memory_text) VALUES (%s)"
            cursor.execute(query, (text,))
            self.connection.commit()
            cursor.close()
            print(f"[R.H.E.A.] Stored to memory: {text}")
            return "Stored in long-term memory."
        except Error as e:
            return f"Failed to store memory: {e}"

    def recall_relevant_memory(self, user_query, limit=3):
        """
        Acts as a lightweight RAG retrieval system. 
        Uses MySQL Natural Language search to find memories relevant to the user's current prompt.
        """
        if not self.connection or not self.connection.is_connected():
            return ""
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            # MySQL Full-Text search acts similarly to a basic vector similarity search
            query = """
                SELECT memory_text 
                FROM user_knowledge 
                WHERE MATCH(memory_text) AGAINST(%s IN NATURAL LANGUAGE MODE)
                LIMIT %s
            """
            cursor.execute(query, (user_query, limit))
            results = cursor.fetchall()
            cursor.close()
            
            if not results:
                return ""
                
            # Combine retrieved memories into a single context string
            context = " ".join([row['memory_text'] for row in results])
            print(f"[R.H.E.A.] Retrieved context from memory: {context}")
            return context
            
        except Error as e:
            print(f"[ERROR] Memory retrieval failed: {e}")
            return ""