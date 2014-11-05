import unittest
import comm.channel as channel


class ChannelTestCase(unittest.TestCase):

    """ Channel TestCase. """

    @classmethod
    def setUpClass(cls):
        """ SetUp the whole class. """
        cls._client = channel.DefaultChannel('ipc:///tmp/channels.ipc')
        cls._server = channel.DefaultChannel('ipc:///tmp/channels.ipc')
        cls._client.connect()
        cls._server.bind()

    @classmethod
    def tearDownClass(cls):
        """ Tear Down the whole class. """
        cls._client.close()
        cls._server.close()

    def message_error_test(self):
        """ MessageError Test. """
        evt = None
        client = ChannelTestCase._client
        self.assertRaises(channel.EventError, client.send, evt)

    def send_recv_test(self):
        """ Send and Receive Test. """
        go = {'control': 'ping', 'payload': 'True'}
        payload = bytes([0, 1, 2, 3, 4, 5, 6])

        client = ChannelTestCase._client
        server = ChannelTestCase._server
        client.send([go, payload])
        event = server.recv()

        come = event[0]
        data = event[1]

        self.assertEqual('ping', come['control'], 'Headers are not equals.')
        self.assertEqual('True', come['payload'], 'Headers are not equals.')
        self.assertEqual(payload.__len__, data.__len__, 'Payload corrupted.')
        self.assertEqual(payload[3], data[3], 'Payload corrupted.')

if __name__ == '__main__':
    unittest.main()
