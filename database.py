import json
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
#load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the MySQL database using Streamlit secrets."""
        try:
            self.connection = mysql.connector.connect(
                host=st.secrets["connections"]["mysql"]["host"],
                port=st.secrets["connections"]["mysql"]["port"],
                user=st.secrets["connections"]["mysql"]["username"],
                password=st.secrets["connections"]["mysql"]["password"],
                database=st.secrets["connections"]["mysql"]["database"]
    )
            print("✅ Database connection established")
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            raise
        
        if not st.secrets.get("connections", {}).get("mysql"):
            raise ValueError("Missing MySQL config in Streamlit secrets")


    def disconnect(self):
        """Close the database connection."""
        if self.connection.is_connected():
            self.connection.close()
            print(" Database connection closed")

    def initialize_db(self):
        """Create tables if they don't exist (idempotent)."""
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tsp_game_results (
                    game_id INT AUTO_INCREMENT PRIMARY KEY,
                    player_name VARCHAR(50) NOT NULL,
                    home_city CHAR(1) NOT NULL,
                    selected_cities JSON NOT NULL,
                    user_path TEXT NOT NULL,
                    user_distance INT NOT NULL,
                    is_optimal BOOLEAN NOT NULL,
                    best_path TEXT NOT NULL,
                    best_distance INT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tsp_algorithm_performance (
                    performance_id INT AUTO_INCREMENT PRIMARY KEY,
                    game_id INT NOT NULL,
                    algorithm_name VARCHAR(20) NOT NULL,
                    execution_time FLOAT NOT NULL,
                    FOREIGN KEY (game_id) REFERENCES tsp_game_results(game_id)
                )
            """)

            self.connection.commit()
            print(" Database tables initialized")
        except Error as e:
            print(f" Failed to initialize database: {e}")
            raise

    def save_game_result(
        self, player_name, home_city, selected_cities, user_path,
        user_distance, is_correct, is_optimal, best_path, best_distance
    ):
        # Add validation for player_name
        if not player_name or not isinstance(player_name, str):
            print("Invalid player name")
            return None
            
        try:
            cursor = self.connection.cursor()
            selected_cities_json = json.dumps(list(selected_cities) if selected_cities else [])
            query = """
                INSERT INTO tsp_game_results (
                    player_name, home_city, selected_cities,
                    user_path, user_distance, is_optimal,
                    best_path, best_distance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                player_name.strip(),  # Clean the name
                home_city, 
                selected_cities_json,
                user_path, 
                user_distance, 
                is_optimal,
                best_path, 
                best_distance
            ))
            game_id = cursor.lastrowid
            self.connection.commit()
            return game_id
        except Error as e:
            print(f"Failed to save game result: {e}")
            self.connection.rollback()
            return None

    def save_algorithm_performance(self, game_id, algorithm_data):
        """Save algorithm performance metrics."""
        if game_id is None:
            print(" Invalid algorithm save: Invalid game_id")
            return

        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO tsp_algorithm_performance (
                    game_id, algorithm_name, execution_time
                ) VALUES (%s, %s, %s)
            """
            for algo_name, exec_time in algorithm_data:
                cursor.execute(query, (game_id, algo_name, exec_time))
            self.connection.commit()
        except Error as e:
            print(f" Failed to save algorithm performance: {e}")
            self.connection.rollback()

    def query(self, query, params=None):
        """Execute a generic SELECT query and return results."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f" Failed to execute query: {e}")
            return []


db = Database()