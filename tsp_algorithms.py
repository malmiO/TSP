import itertools
import time

def run_tsp_algorithms(dist_matrix, home_index):
    """
    Runs three TSP algorithms and returns their results.
    """
    algorithms = [
        ('Brute Force', brute_force_tsp),
        ('Held-Karp', held_karp_tsp),
        ('Nearest Neighbor', nearest_neighbor_tsp)
    ]
    
    results = []
    
    for name, func in algorithms:
        start_time = time.perf_counter()
        try:
            result = func(dist_matrix, home_index)
            end_time = time.perf_counter()
            exec_time = end_time - start_time
        
            if result['path'] is None and result['cost'] == float('inf'):
                continue  
            
            results.append({
                'algorithm': name,
                'path': result['path'] or [],  
                'cost': result['cost'],
                'time': exec_time
            })
        except Exception as e:
            print(f"Algorithm {name} failed: {e}")
            continue
    
    return results

def brute_force_tsp(dist_matrix, home_index):
    """
    Brute-force exact algorithm (for small n).
    """
    n = len(dist_matrix)
    cities = [i for i in range(n) if i != home_index]
    
    if not cities:
        return {'path': [home_index, home_index], 'cost': 0}
    
    min_cost = float('inf') 
    min_path = None
    
    for perm in itertools.permutations(cities):
        current_path = [home_index] + list(perm) + [home_index]
        current_cost = 0
        valid = True
        
        for i in range(len(current_path) - 1):
            cost = dist_matrix[current_path[i]][current_path[i+1]]
            current_cost += cost
        
        if current_cost < min_cost:
            min_cost = current_cost
            min_path = current_path
    
    return {'path': min_path, 'cost': min_cost}

def held_karp_tsp(dist_matrix, home_index):
    """
    Dynamic Programming (Held-Karp) exact algorithm.
    """
    n = len(dist_matrix)
    cities = [i for i in range(n) if i != home_index]
    num_cities = len(cities)
    
    if num_cities == 0:
        return {'path': [home_index, home_index], 'cost': 0}
    
    # Mapping between city indices and subset indices
    city_to_idx = {city: idx for idx, city in enumerate(cities)}
    idx_to_city = {idx: city for idx, city in enumerate(cities)}
    
    memo = {}
    
    # Initialize base cases
    for idx in range(num_cities):
        city = cities[idx]
        mask = 1 << idx
        memo[(mask, idx)] = (dist_matrix[home_index][city], home_index)
    
    # Build DP table for subsets
    for subset_size in range(2, num_cities + 1):
        for subset in itertools.combinations(range(num_cities), subset_size):
            mask = sum(1 << bit for bit in subset)
            
            for current in subset:
                prev_mask = mask & ~(1 << current)
                min_cost = float('inf')
                min_prev = -1
                
                for prev in subset:
                    if prev == current:
                        continue
                    if (prev_mask, prev) not in memo:
                        continue
                    cost, _ = memo[(prev_mask, prev)]
                    cost += dist_matrix[idx_to_city[prev]][idx_to_city[current]]
                    if cost < min_cost:
                        min_cost = cost
                        min_prev = prev
                
                if min_prev != -1:
                    memo[(mask, current)] = (min_cost, min_prev)
    
    # Find optimal return path to home
    mask = (1 << num_cities) - 1
    min_total = float('inf')
    best_last = -1
    
    for current in range(num_cities):
        if (mask, current) not in memo:
            continue
        cost, _ = memo[(mask, current)]
        total_cost = cost + dist_matrix[idx_to_city[current]][home_index]
        if total_cost < min_total:
            min_total = total_cost
            best_last = current
    
    # Reconstruct path if valid
    if best_last == -1:
        return {'path': None, 'cost': float('inf')}
    
    path = []
    current_mask = mask
    current_node = best_last
    
    while current_mask:
        city = idx_to_city[current_node]
        path.append(city)
        new_mask = current_mask & ~(1 << current_node)
        
        if (current_mask, current_node) not in memo:
            break
            
        _, prev_node = memo[(current_mask, current_node)]
        
        if prev_node == home_index:
            break
            
        prev_idx = city_to_idx[prev_node]
        current_mask = new_mask
        current_node = prev_idx
    
    path.reverse()
    full_path = [home_index] + path + [home_index]
    
    # Add validation to ensure no duplicates (except home)
    visited = set()
    for city in full_path[1:-1]:  # Exclude first and last (home)
        if city in visited:
            # If duplicates found, fall back to brute force for small n
            if len(dist_matrix) <= 10:
                return brute_force_tsp(dist_matrix, home_index)
            return {'path': None, 'cost': float('inf')}
        visited.add(city)
    
    return {'path': full_path, 'cost': min_total}

def nearest_neighbor_tsp(dist_matrix, home_index):
    """
    Greedy heuristic algorithm.
    """
    n = len(dist_matrix)
    if n == 0:
        return {'path': [], 'cost': 0}
    
    unvisited = set(range(n))
    current = home_index
    unvisited.remove(current)
    path = [current]
    total_cost = 0
    
    while unvisited:
        next_city = min(unvisited, key=lambda city: dist_matrix[current][city])
        total_cost += dist_matrix[current][next_city]
        path.append(next_city)
        current = next_city
        unvisited.remove(current)
    
    # Return to home
    total_cost += dist_matrix[current][home_index]
    path.append(home_index)
    
    return {'path': path, 'cost': total_cost}