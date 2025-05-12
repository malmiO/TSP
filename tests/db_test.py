import unittest
from unittest.mock import patch, MagicMock

from database import Database
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database()

    @patch('mysql.connector.connect')
    def test_connect_success(self, mock_connect):
        mock_connect.return_value = MagicMock()
        self.db.connect()
        mock_connect.assert_called_once()

    @patch('mysql.connector.connect')
    def test_connect_failure(self, mock_connect):
        mock_connect.side_effect = Exception("Database connection error")
        with self.assertRaises(Exception):
            self.db.connect()

    @patch('mysql.connector.connect')
    def test_initialize_db(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        self.db.initialize_db()
        mock_cursor.execute.assert_called()

    @patch('mysql.connector.connect')
    def test_save_game_result(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        game_id = self.db.save_game_result(
            'Player1', 'A', ['B', 'C'], 'A-B-C-A', 100, True, True, 'A-B-C-A', 90
        )
        self.assertIsNotNone(game_id)
        mock_cursor.execute.assert_called()

    @patch('mysql.connector.connect')
    def test_save_algorithm_performance(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        self.db.save_algorithm_performance(1, [('Brute Force', 0.5), ('Held-Karp', 1.2)])
        mock_cursor.execute.assert_called()

if __name__ == '__main__':
    unittest.main()
