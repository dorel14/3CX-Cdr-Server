import unittest
from tcp_socket_server import TcpSocketServer


class TestTcpSocketServer(unittest.TestCase):
    def setUp(self):
        self.server = TcpSocketServer("localhost", 8000)

    def test_start_server(self):
        self.server.start_server()
        self.assertTrue(self.server.is_running)

    def test_stop_server(self):
        self.server.start_server()
        self.server.stop_server()
        self.assertFalse(self.server.is_running)

    def test_handle_client(self):
        # Mocked client socket and data
        client_socket = MockSocket()
        data = b"Test data"

        self.server.handle_client(client_socket, data)
        # Add assertions to verify expected behavior

    def tearDown(self):
        self.server.stop_server()


if __name__ == "__main__":
    unittest.main()
