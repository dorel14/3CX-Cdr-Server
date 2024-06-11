import unittest
from unittest.mock import patch, Mock
from sourcegraph.scpclient import SCPClient

class TestSCPClient(unittest.TestCase):

    @patch('sourcegraph.scpclient.SCPClient.get_connection')
    def test_get(self, mock_get_connection):
        client = SCPClient('user', 'host')
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection
        mock_scp = mock_connection.open_sftp_client.return_value
        mock_scp.get.return_value = b'test content'

        content = client.get('/path/to/file')

        mock_get_connection.assert_called_once()
        mock_connection.open_sftp_client.assert_called_once()
        mock_scp.get.assert_called_once_with('/path/to/file')
        self.assertEqual(content, b'test content')

    @patch('sourcegraph.scpclient.SCPClient.get_connection')
    def test_put(self, mock_get_connection):
        client = SCPClient('user', 'host')
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection
        mock_scp = mock_connection.open_sftp_client.return_value

        client.put('/path/to/file', b'test content')

        mock_get_connection.assert_called_once()
        mock_connection.open_sftp_client.assert_called_once()
        mock_scp.put.assert_called_once_with(b'test content', '/path/to/file')
