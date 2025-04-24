import unittest
from database import Database
from tsp_algorithms import brute_force_tsp

class TestTSP(unittest.TestCase):
    def test_brute_force(self):
        matrix = [[0, 10, 15], [10, 0, 20], [15, 20, 0]]
        result = brute_force_tsp(matrix, 0)
        self.assertEqual(result['cost'], 45)

    def test_db_save(self):
        db = Database()
        game_id = db.save_game_result("Test", "A", ["B", "C"], "A,B,C,A", 100, True, True, "A,B,C,A", 100)
        self.assertIsNotNone(game_id)