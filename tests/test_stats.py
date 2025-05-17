import unittest
from unittest.mock import patch

from stats import Stats, avg
from response import Response


class StatsTest(unittest.TestCase):
    def setUp(self):
        self.stats = Stats()

    def test_avg(self):
        assert avg(1, 2, 3) == 2
        assert avg(10, 20, 30) == 20
        assert avg(5) == 5
    
    def test_add_received_packet(self):
        self.stats.add(Response.PORT_OPEN, 0.1)
        self.assertEqual(self.stats.received, 1)
        self.assertEqual(self.stats.lost, 0)
        self.assertEqual(len(self.stats.records), 1)

    def test_add_lost_packet(self):
        self.stats.add(Response.PORT_CLOSED, 0)
        self.assertEqual(self.stats.received, 0)
        self.assertEqual(self.stats.lost, 1)
        self.assertEqual(len(self.stats.records), 0)

    def test_results_with_data(self):
        # Добавляем тестовые данные
        self.stats.add(Response.PORT_OPEN, 0.1)
        self.stats.add(Response.PORT_OPEN, 0.2)
        self.stats.add(Response.PORT_CLOSED, 0)
        
        # Заменяем функцию avg на mock для контроля её вызова
        with patch('stats.avg', return_value=150.0) as mock_avg:
            result = self.stats.results()
            
            # Проверяем, что avg была вызвана с правильными аргументами
            mock_avg.assert_called_once_with(100, 200)
            
            # Проверяем результат
            self.assertIn("3 пакетов отправлено", result)
            self.assertIn("2 пакетов доставлено", result)
            self.assertIn("Процент потерь - 33.3%", result)
            self.assertIn("min - 100.0ms", result)
            self.assertIn("max - 200.0ms", result)
            self.assertIn("avg - 150.0ms", result)

    def test_results_without_time_data(self):
        # Добавляем только потерянные пакеты (без времени)
        self.stats.add(Response.PORT_CLOSED, 0)
        self.stats.add(Response.PORT_CLOSED, 0)
        
        result = self.stats.results()
        
        # Проверяем, что статистика времени не выводится
        self.assertIn("2 пакетов отправлено", result)
        self.assertIn("0 пакетов доставлено", result)
        self.assertIn("Процент потерь - 100.0%", result)
        self.assertNotIn("Статистика времени", result)