import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, call
import socket
import struct
from ping import Ping, get_checksum
from response import Response

class TestPing(unittest.TestCase):
    def setUp(self):
        # ip = "127.0.0.1"
        # self.ping = Ping(ip, 10001, ip, 10002, 2)
        pass

    def test_ping_timeout(self):
        with patch("socket.socket") as mock_socket:
            # Создаем экземпляр Ping
            ping = Ping(
                src_ip="127.0.0.1",
                src_port=12345,
                dst_ip="127.0.0.1",
                dst_port=80,
                timeout=1
            )

            # Настраиваем recvfrom чтобы вызывал timeout
            mock_socket.return_value.recvfrom.side_effect = socket.timeout()
            
            # Вызываем ping и проверяем результат
            with patch('builtins.print') as mock_print:  # мокаем print чтобы проверить вывод
                code, response_time = ping.ping(1)
                
                # Проверяем что вернулся правильный код
                self.assertEqual(code, Response.TIMEOUT)
                self.assertEqual(response_time, 0)
                
                # Проверяем что было напечатано "whoopsie"
                mock_print.assert_called_with("whoopsie")
                
            # Проверяем что settimeout был вызван с правильным значением
            mock_socket.return_value.settimeout.assert_called_with(1)
            
            # Проверяем что sendto был вызван
            self.assertTrue(mock_socket.return_value.sendto.called)
    
    def test_ping_success(self):
        with patch("socket.socket") as mock_socket:
            # Создаем объект Ping
            ping = Ping(
                src_ip="127.0.0.1",
                src_port=54321,
                dst_ip="127.0.0.1",
                dst_port=80,
                timeout=1
            )

            # Подготовка фейкового ответа (SYN-ACK пакет)
            fake_response = self._build_fake_syn_ack_response(seq=1)

            # Настраиваем поведение recvfrom:
            # - первый вызов возвращает SYN-ACK (порт открыт)
            # mock_socket.return_value.recvfrom.side_effect = [
                # (fake_response, ("127.0.0.1", 80)),  # Первый вызов - успешный ответ
                # socket.timeout()  # Второй вызов - таймаут (чтобы выйти из цикла)
            # ]
            mock_socket.return_value.recvfrom.return_value = (fake_response, ("127.0.0.1", 80))

            # Вызываем ping и проверяем результат
            code, response_time = ping.ping(1)

            # Проверяем что вернулся PORT_OPEN
            self.assertEqual(code, Response.PORT_OPEN)
            self.assertGreater(response_time, 0)  # Время ответа должно быть > 0

            # Проверяем что sendto вызывался дважды:
            # 1. Для исходного SYN-пакета
            # 2. Для RST-пакета после получения SYN-ACK
            self.assertEqual(mock_socket.return_value.sendto.call_count, 2)
    
    def _build_fake_syn_ack_response(self, seq):
        # IP-заголовок (20 байт, минимально валидный)
        ip_header = bytes(20) # bytes([0x45, 0x00, 0x00, 0x3c]) + bytes(16)

        # TCP-заголовок (20 байт)
        tcp_header = struct.pack(
            '!HHIIBBHHH',
            80,                  # Source port (dst port в ответе)
            54321,               # Destination port (src port в ответе)
            12345,              # Sequence number (не важно)
            seq + 1,             # ACK number (должен быть seq + 1)
            5 << 4,              # Data offset
            0x12,               # Flags (SYN + ACK)
            5840,               # Window
            0,                  # Checksum (можно 0 для теста)
            0                   # Urgent pointer
        )

        # Собираем полный пакет (IP + TCP)
        return ip_header + tcp_header