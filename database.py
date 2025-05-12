import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

firebase_config = dict(st.secrets["firebase"])
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")


if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

firestore_db = firestore.client()

class FirebaseDatabase:
    def __init__(self, firestore_db):
        self.db = firestore_db
        print("\u2705 Firebase connection established")
    
    def initialize_db(self):
        # Firestore is schemaless, so no need to pre-create tables/collections
        print("\u2705 No schema setup required for Firestore")

    def save_game_result(
        self, player_name, home_city, selected_cities, user_path,
        user_distance, is_optimal, best_path, best_distance  # Removed is_correct
    ):
        if not player_name or not isinstance(player_name, str):
            print("Invalid player name")
            return None

        try:
            game_data = {
                "player_name": player_name.strip(),
                "home_city": home_city,
                "selected_cities": list(selected_cities) if selected_cities else [],
                "user_path": user_path,
                "user_distance": user_distance,
                "is_optimal": is_optimal,  # Now correctly used
                "best_path": best_path,
                "best_distance": best_distance,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            # Correctly create a new document reference and set data
            doc_ref = self.db.collection("tsp_game_results").document()
            doc_ref.set(game_data)
            print("\u2705 Game result saved")
            return doc_ref.id  # Return the document ID
        except Exception as e:
            print(f"\u274C Failed to save game result: {e}")
            return None

    def save_algorithm_performance(self, game_id, algorithm_data):
        if not game_id:
            print("\u274C Invalid game_id")
            return

        try:
            for algo_name, exec_time in algorithm_data:
                self.db.collection("tsp_algorithm_performance").add({
                    "game_id": game_id,
                    "algorithm_name": algo_name,
                    "execution_time": exec_time,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
            print("\u2705 Algorithm performance saved")
        except Exception as e:
            print(f"\u274C Failed to save algorithm performance: {e}")

    def query(self, collection_name, filters=None, order_by=None, direction=firestore.Query.DESCENDING, limit=None):
        try:
            collection_ref = self.db.collection(collection_name)
            if filters:
                for field, op, value in filters:
                    collection_ref = collection_ref.where(field, op, value)
            if order_by:
                collection_ref = collection_ref.order_by(order_by, direction=direction)
            if limit:
                collection_ref = collection_ref.limit(limit)
            docs = collection_ref.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"\u274C Failed to execute query: {e}")
            return []

# Initialize database connection
db = FirebaseDatabase(firestore_db)
db.initialize_db()