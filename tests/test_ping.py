import unittest
from unittest.mock import patch
import socket
import struct
from ping import Ping
from response import Response


class TestPing(unittest.TestCase):
    def test_ping_timeout(self):
        with patch("socket.socket") as mock_socket:
            ping = Ping("127.0.0.1", 54321, "127.0.0.1", 80, 1, False)

            mock_socket.return_value.recvfrom.side_effect = socket.timeout()
            
            code, response_time = ping.ping(1)

            self.assertEqual(code, Response.TIMEOUT)
            self.assertAlmostEqual(response_time, 0, places=3)
            
            mock_socket.return_value.settimeout.assert_called_with(1)
            
            self.assertTrue(mock_socket.return_value.sendto.called)
    
    def test_ping_success(self):
        with patch("socket.socket") as mock_socket:
            ping = Ping("127.0.0.1", 54321, "127.0.0.1", 80, 1, False)

            fake_response = self._build_fake_syn_ack_response(seq=1)

            mock_socket.return_value.recvfrom.return_value = (fake_response, ("127.0.0.1", 80))

            code, response_time = ping.ping(1)

            self.assertEqual(code, Response.PORT_OPEN)
            self.assertGreater(response_time, 0)

            self.assertEqual(mock_socket.return_value.sendto.call_count, 2)
    
    def test_ping_count(self):
        with patch.object(Ping, "ping") as mock_ping, patch("time.sleep") as mock_sleep:
            mock_ping.return_value = (Response.TIMEOUT, 0)
            ping = Ping("127.0.0.1", 54321, "127.0.0.1", 80, 1, False)
            ping.start(5, 1)
            self.assertEqual(mock_ping.call_count, 5)
    
    def test_ping_interval(self):
        with patch.object(Ping, "ping") as mock_ping, patch("time.sleep") as mock_sleep:
            mock_ping.return_value = (Response.TIMEOUT, 0)
            ping = Ping("127.0.0.1", 54321, "127.0.0.1", 80, 1, False)
            ping.start(1, 1)
            mock_sleep.assert_called_with(1)
    
    def _build_fake_syn_ack_response(self, seq):
        ip_header = bytes(20)

        tcp_header = struct.pack(
            "!HHIIBBHHH",
            80,
            54321,
            12345,
            seq + 1,
            5 << 4,
            0x12,
            1024,
            0,
            0
        )

        return ip_header + tcp_header
