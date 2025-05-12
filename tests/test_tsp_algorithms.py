import unittest

from tsp_algorithms import brute_force_tsp, held_karp_tsp, nearest_neighbor_tsp, run_tsp_algorithms
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
class TestTSPAlgorithms(unittest.TestCase):

    def setUp(self):
        # Sample distance matrix for testing
        self.dist_matrix = [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ]
        self.home_index = 0  # Starting point (home city)

    def test_brute_force_tsp(self):
        result = brute_force_tsp(self.dist_matrix, self.home_index)
        self.assertIsNotNone(result)
        self.assertTrue(result['path'])
        self.assertGreater(result['cost'], 0)

    def test_held_karp_tsp(self):
        result = held_karp_tsp(self.dist_matrix, self.home_index)
        self.assertIsNotNone(result)
        self.assertTrue(result['path'])
        self.assertGreater(result['cost'], 0)

    def test_nearest_neighbor_tsp(self):
        result = nearest_neighbor_tsp(self.dist_matrix, self.home_index)
        self.assertIsNotNone(result)
        self.assertTrue(result['path'])
        self.assertGreater(result['cost'], 0)

    def test_run_tsp_algorithms(self):
        results = run_tsp_algorithms(self.dist_matrix, self.home_index)
        self.assertEqual(len(results), 3)  
        for result in results:
            self.assertIn('algorithm', result)
            self.assertIn('path', result)
            self.assertIn('cost', result)

if __name__ == '__main__':
    unittest.main()
