import streamlit as st
import random
import time
import datetime
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from tsp_algorithms import run_tsp_algorithms
from google.cloud import firestore
from dotenv import load_dotenv
from database import db

# Load environment variables
load_dotenv()

# Initialize database connection
db.initialize_db()

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "welcome" 

if "player_name" not in st.session_state:
    st.session_state.player_name = ""

if "home_city" not in st.session_state:
    st.session_state.home_city = ""
    
if "cities" not in st.session_state:
    st.session_state.cities = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"] 
    
if "selected_cities" not in st.session_state:
    st.session_state.selected_cities = []
    
# --- Validation Functions ---
def validate_name(name):
    """Validate player name"""
    name = name.strip()
    if not name:
        return "Name cannot be empty"
    if len(name) > 20:
        return "Name is too long - max 20 characters"
    if not name.replace(" ", "").isalnum():
        return "Name should only contain letters, numbers and spaces"
    return None

def validate_city_selection(selected_cities, home_city):
    """Validate city selection"""
    if not selected_cities:
        return "Please select cities to visit"
    if home_city in selected_cities:
        return "Home city should not be in selected cities"
    if len(selected_cities) < 3:
        return "Please select at least 3 cities to visit for the game to be challenging"
    return None

def validate_user_path(user_path, home_city, selected_cities):
    """Validate the user's path input"""
    if not user_path:
        return "Please enter a path"
    
    try:
        path = [city.strip().upper() for city in user_path.split(",") if city.strip()]
    except Exception:
        return "Invalid path format - use comma-separated city names"
    
    # Basic structure validation
    if len(path) < 4:
        return "Path must start at home, visit cities, and end at home — at least 4 cities required"
    
    if path[0] != home_city or path[-1] != home_city:
        return f"Path must start and end at home city ({home_city})"
    
    # Check all required cities are visited exactly once
    required_cities = set(selected_cities)
    visited_cities = set(path[1:-1])  # Exclude first and last (home city)
    
    if len(path[1:-1]) != len(required_cities):
        return f"You must visit exactly {len(required_cities)} cities (excluding home)"
    
    if required_cities != visited_cities:
        missing = required_cities - visited_cities
        extra = visited_cities - required_cities
        errors = []
        if missing:
            errors.append(f"Missing cities: {', '.join(missing)}")
        if extra:
            errors.append(f"Extra cities: {', '.join(extra)}")
        return ". ".join(errors)
    
    # Check for duplicate visits (excluding the home city at start/end)
    city_counts = {}
    for city in path[1:-1]:
        city_counts[city] = city_counts.get(city, 0) + 1
        if city_counts[city] > 1:
            return f"City {city} is visited more than once"

    return None

# --- Page Navigation Functions ---
def go_to_name_input():
    st.session_state.page = "name_input"

def save_name_and_continue():
    name_error = validate_name(st.session_state.player_name)
    if name_error:
        st.warning(name_error)
    else:
        st.session_state.page = "home_city_selection"

def go_to_city_selection():
    st.session_state.page = "select_cities"

def go_to_path_game():
    selection_error = validate_city_selection(
        st.session_state.selected_cities,
        st.session_state.home_city,
        st.session_state.player_name
    )
    if selection_error:
        st.warning(selection_error)
    else:
        st.session_state.start_time = datetime.datetime.now()
        st.session_state.page = "path_game"

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")

#if st.session_state.player_name:
#    st.sidebar.markdown(f"👤 **Player:** {st.session_state.player_name}")

nav_option = st.sidebar.radio(
    "Go to:",
    ["Play Game", "Algorithm Performance", "Leaderboard"],
    index=0
)

if nav_option == "Play Game" and st.session_state.page not in ["welcome", "name_input", "home_city_selection", "select_cities", "path_game", "evaluate_path"]:
    st.session_state.page = "welcome"
elif nav_option == "Algorithm Performance":
    st.session_state.page = "algorithm_performance"
elif nav_option == "Leaderboard":
    st.session_state.page = "leaderboard"

# --- Page: Welcome ---
if st.session_state.page == "welcome":
    st.title("🗺️ Traveling Salesman Problem Game")

    st.markdown("""
    Welcome to the Traveling Salesman Problem Game!

    🚀 **Goal:**  
    Visit all selected cities exactly once and return to the home city using the shortest route possible.

    🧠 **How to Play:**
    1. Click **Start Game** to begin.
    2. Enter your name.
    3. A home city will be chosen for you.
    4. Select the cities you want to visit.
    5. Try to guess the shortest possible path!

    Let's see how good your optimization skills are! 😎
    """)

    st.button("▶️ Start Game", on_click=go_to_name_input)

# --- Page: Name Input ---
elif st.session_state.page == "name_input":
    st.title("👤 Enter Your Name")
    
    # Use a temporary key for the text input
    temp_name = st.text_input("What's your name?", key="temp_player_name",
                            placeholder="Enter your name here...",
                            max_chars=50)
    
    if st.button("➡️ Continue"):
        name_error = validate_name(temp_name)
        if name_error:
            st.error(name_error)
        else:
            st.session_state.player_name = temp_name
            st.session_state.page = "home_city_selection"
            st.rerun()
    
# --- Page: Home City Selection ---
elif st.session_state.page == "home_city_selection":
    st.title("🏠 Selecting Your Home City...")

    placeholder = st.empty()
    city_list = st.session_state.cities
    for _ in range(20):  # Shuffle animation
        placeholder.markdown(f"### 🔄 Shuffling... **{random.choice(city_list)}**")
        time.sleep(0.1)

    selected_city = random.choice(city_list)
    st.session_state.home_city = selected_city

    placeholder.markdown(f"### 🎉 Your Home City is: **{selected_city}**")

    st.success(f"🏙️ Great choice, {st.session_state.player_name}! Let's pick your travel cities.")

    st.button("🧭 Select Cities to Visit", on_click=go_to_city_selection)

# --- Page: City Selection ---
elif st.session_state.page == "select_cities":
    st.title("🧭 Choose Cities to Visit")

    st.markdown("Click on the cities you want to visit (excluding your home city).")

    st.markdown(f"🏠 **Home City:** `{st.session_state.home_city}`")
    #st.markdown(f"👤 **Player:** {st.session_state.player_name}")

    remaining_cities = [city for city in st.session_state.cities if city != st.session_state.home_city]

    def select_city(city):
        if city not in st.session_state.selected_cities:
            st.session_state.selected_cities.append(city)
        else:
            st.session_state.selected_cities.remove(city)

    cols = st.columns(3)
    for i, city in enumerate(remaining_cities):
        with cols[i % 3]:
            if city in st.session_state.selected_cities:
                if st.button(f"❌ {city}", key=f"remove_{city}"):
                    select_city(city)
            else:
                if st.button(f"➕ {city}", key=f"add_{city}"):
                    select_city(city)

    if st.session_state.selected_cities:
        st.markdown("### ✅ Selected Cities:")
        cols = st.columns(10)
        for i, city in enumerate(st.session_state.selected_cities):
            if i >= 10:
                break
            with cols[i]:
                st.write(city)
        
        st.markdown(f"**Total selected:** {len(st.session_state.selected_cities)} cities")
        
        if st.button("✅ Confirm Selection"):
            error = validate_city_selection(
                st.session_state.selected_cities,
                st.session_state.home_city
            )
            if error:
                st.error(error)
            else:
                st.session_state.page = "path_game"
                st.rerun()
    else:
        st.info("Please select cities to continue.")

# --- Page: Path Game ---
elif st.session_state.page == "path_game":
    st.title("🧩 Find the Shortest Route!")

    selected = st.session_state.selected_cities
    home = st.session_state.home_city
    all_cities = [home] + selected

    st.markdown(f"🏠 **Home City:** `{home}`")
    st.markdown(f"🗺️ **Cities to Visit:** `{', '.join(selected)}`")

    def generate_distances(cities):
        distances = {}
        for i, city1 in enumerate(cities):
            for j, city2 in enumerate(cities):
                if i < j:  
                    dist = random.randint(50, 100)
                    distances[(city1, city2)] = dist
                    distances[(city2, city1)] = dist

        return distances

    if "distances" not in st.session_state:
        st.session_state.distances = generate_distances(all_cities)

    distances = st.session_state.distances

    G = nx.Graph()
    G.add_nodes_from(all_cities)
    for (i, j), d in distances.items():
        G.add_edge(i, j, weight=d)

    node_colors = []
    for node in G.nodes():
        if node == st.session_state.home_city:
            node_colors.append("red")   
        else:
            node_colors.append("skyblue")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 City Map")
        pos = nx.spring_layout(G, seed=42)
        fig, ax = plt.subplots(figsize=(6, 6))
        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2000, font_size=12, ax=ax)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=10, ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("📏 Distance Matrix")
        matrix = pd.DataFrame(index=all_cities, columns=all_cities)
        for i in all_cities:
            for j in all_cities:
                if i == j:
                    matrix.loc[i, j] = 0
                else:
                    matrix.loc[i, j] = distances.get((i, j), distances.get((j, i), 0))
    
        display_matrix = matrix.copy()
        for i in all_cities:
            display_matrix.loc[i, i] = '-'
        
        st.dataframe(matrix.astype(str))
        
    st.markdown("### 🚶‍♂️ Your Move!")
    st.markdown("Enter the cities in the order you want to visit (starting and ending at your home city).")

    user_path = st.text_input("🛣️ Enter your path (comma separated):", placeholder=f"{home},...,{home}")
    if st.button("🚀 Submit Path"):
        if not user_path:
            st.warning("Please enter a path")
        else:
            validation_error = validate_user_path(user_path, home, selected)
            if validation_error:
                st.error(f"Invalid path: {validation_error}")
            else:
                st.session_state.user_path = user_path
                st.session_state.page = "evaluate_path"
                st.rerun()
    
# --- Page: Evaluate Path ---
elif st.session_state.page == "evaluate_path":
    
    st.title("🏁 Game Results & Evaluation")
    

    user_input = st.session_state.user_path
    home = st.session_state.home_city
    selected = st.session_state.selected_cities
    all_cities = [home] + selected
    distances = st.session_state.distances

    city_indices = {city: i for i, city in enumerate(all_cities)}
    city_names = list(city_indices.keys())

    dist_matrix = [[0] * len(city_names) for _ in range(len(city_names))]
    for (c1, c2), d in distances.items():
        i, j = city_indices[c1], city_indices[c2]
        dist_matrix[i][j] = d
        dist_matrix[j][i] = d

    def path_distance(path):
        total = 0
        for i in range(len(path) - 1):
            from_city = path[i]
            to_city = path[i + 1]
            from_idx = city_indices[from_city]
            to_idx = city_indices[to_city]
            d = dist_matrix[from_idx][to_idx]
            total += d
        return total

    validation_error = validate_user_path(user_input, home, selected)
    if validation_error:
        st.error(f"❌ Invalid path: {validation_error}")
        st.button("🔙 Go Back and Fix Path", on_click=lambda: st.session_state.update({"page": "path_game"}))
        st.stop()

    user_path = [city.strip().upper() for city in user_input.split(",") if city.strip()]
    user_distance = path_distance(user_path)

    algo_outputs = run_tsp_algorithms(dist_matrix, home_index=0)
    best_result = min(algo_outputs, key=lambda x: x['cost'])
    best_path_names = [city_names[i] for i in best_result['path']]

    end_time = datetime.datetime.now()
    start_time = st.session_state.get("start_time")
    time_taken = (end_time - start_time).total_seconds() if start_time else None

    is_optimal = abs(user_distance - best_result['cost']) < 0.001

    st.markdown("## 📝 Your Journey Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🙋 Your Path")
        st.markdown(f"**Path:** `{ ' -> '.join(user_path) }`")
        st.markdown(f"**Distance:** `{user_distance}` units")
        if time_taken is not None:
            st.markdown(f"⏱️ **Time Taken:** `{time_taken:.2f} seconds`")

    with col2:
        st.subheader("🧠 Optimal Path")
        st.markdown(f"**Best Path:** `{ ' -> '.join(best_path_names) }`")
        st.markdown(f"**Best Distance:** `{best_result['cost']}` units")

    if is_optimal:
        st.balloons()
        st.success("🎉 Amazing ! You found the optimal path!")
    else:
        st.info("🔍 Your path is valid, but not the shortest.")

    game_id = db.save_game_result(
        st.session_state.player_name,
        home,
        selected,
        ','.join(user_path),
        user_distance,
        is_optimal, 
        ' -> '.join(best_path_names),
        best_result['cost']
    )

    if game_id is not None:
        db.save_algorithm_performance(
            game_id,
            [(res['algorithm'], res['time']) for res in algo_outputs]
        )
    else:
        st.error("❌ Failed to save game results. Check database logs.")
        
    with st.expander("📊 See How the Algorithms Performed"):
        for res in algo_outputs:
            algo_name = res['algorithm']
            cost = res['cost']
            t = res['time']
            path = [city_names[i] for i in res['path']]
            st.markdown(f"**{algo_name}**: `{ ' -> '.join(str(x) for x in path) }` = {str(cost)} units in `{str(t)}` seconds")

    st.markdown("---")
    st.markdown("Want to try again or check the leaderboard?")
    if st.button("🔄 Play Again"):
        for key in list(st.session_state.keys()):
            if key not in ["cities"]:
                del st.session_state[key]
        st.session_state.page = "welcome"
        st.rerun()

# --- Page: Algorithm Performance ---
elif st.session_state.page == "algorithm_performance":
    st.title("📊 Algorithm Performance")

    st.markdown("""
    This page shows the performance of the three TSP algorithms (Brute Force, Held-Karp, Nearest Neighbor) 
    over the last 10 game rounds. The chart below compares their execution times.
    """)

    try:
        # Fetch last 10 game results
        game_results = db.query(
            "tsp_game_results",
            order_by="timestamp",
            direction=firestore.Query.DESCENDING,
            limit=10
        )
        # Extract game IDs (already sorted by timestamp descending)
        game_ids = [game["id"] for game in game_results]

        # Fetch algorithm performances for these games
        data = []
        for i, game_id in enumerate(game_ids):
            perf_docs = db.query(
                "tsp_algorithm_performance",
                filters=[("game_id", "==", game_id)]
            )
            for perf in perf_docs:
                data.append({
                    "Game Round": len(game_ids) - i,  # Most recent game gets highest number
                    "algorithm_name": perf["algorithm_name"],
                    "execution_time": perf["execution_time"]
                })

        if data:
            # Create DataFrame
            df = pd.DataFrame(data)
            df = df.sort_values(by='Game Round', ascending=True)

            # Create pivot table
            pivot_df = df.pivot(index='Game Round', columns='algorithm_name', values='execution_time')

            # Display bar chart
            fig = px.bar(
                df,
                x="Game Round",
                y="execution_time",
                color="algorithm_name",
                title="Algorithm Execution Times (Last 10 Game Rounds)",
                labels={"Game Round": "Game Round", "execution_time": "Time (seconds)", "algorithm_name": "Algorithm"},
                barmode="group"
            )
            st.plotly_chart(fig)

            # Display pivot table
            st.subheader("Performance by Game Round")
            st.dataframe(pivot_df)
        else:
            st.warning("No performance data available. Play some games to generate data!")
    except Exception as e:
        st.error(f"Failed to fetch performance data: {e}")
        
# --- Page: Leaderboard ---
elif st.session_state.page == "leaderboard":
    st.title("🏆 Leaderboard")

    st.markdown("""
    Check out the top players who found the shortest routes!
    """)

    try:
        # Fetch all optimal game results
        optimal_games = db.query(
            "tsp_game_results",
            filters=[("is_optimal", "==", True)]
        )
        if optimal_games:
            # Create DataFrame
            df = pd.DataFrame(optimal_games)
            # Filter out invalid player names
            df = df[df['player_name'].notnull() & (df['player_name'] != '')]
            # Aggregate data
            leaderboard = df.groupby('player_name').agg(
                optimal_count=('player_name', 'count'),
                best_distance=('user_distance', 'min'),
                last_played=('timestamp', 'max')
            ).reset_index()
            # Sort and limit to top 10
            leaderboard = leaderboard.sort_values(
                by=['optimal_count', 'best_distance'], ascending=[False, True]
            ).head(10)
            # Set index to start at 1
            leaderboard.index = leaderboard.index + 1

            st.subheader("Top Players")
            st.dataframe(leaderboard.style.format({
                'best_distance': '{:.0f} units',
                'last_played': lambda x: x.strftime('%Y-%m-%d %H:%M') if pd.notnull(x) else ''
            }))
        else:
            st.warning("No leaderboard data available. Play some games to appear here!")
    except Exception as e:
        st.error(f"Failed to fetch leaderboard data: {e}")