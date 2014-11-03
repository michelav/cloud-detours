import unittest
import comm.channel as channel


class ChannelTestCase(unittest.TestCase):

    """ Channel TestCase. """

    def send_recv_test(self):
        """ Send and Receive Test. """
        go = '{\"control\": \"ping\", \"payload\": \"True\"}'
        payload = bytes([0, 1, 2, 3, 4, 5, 6])

        client = channel.DefaultChannel('ipc:///tmp/channels.ipc')
        server = channel.DefaultChannel('ipc:///tmp/channels.ipc')
        client.connect()
        server.bind()
        client.send(go, payload)
        come, data = server.recv()

        self.assertEqual('ping', come['control'], 'Headers are not equals.')
        self.assertEqual('True', come['payload'], 'Headers are not equals.')
        self.assertEqual(payload.__len__, data.__len__, 'Payload corrupted.')
        self.assertEqual(payload[3], data[3], 'Payload corrupted.')

if __name__ == '__main__':
    unittest.main()
