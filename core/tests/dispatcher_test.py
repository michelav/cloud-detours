import threading
import json
import unittest
import comm.channel as channel
import handling.dispatcher as dispatcher


class Handler(object):

    """ Sugar class to test Dispatching Mechanism. """

    def __init__(self, id, handle):
        """ Constructor. """
        super(Handler, self).__init__()
        self._id = id
        self._handle = handle
        self._header = None

    def handle_event(self):
        """ Mock handle event. """
        evt = self._handle.recv()
        self._header = evt[0]
        header_dict = json.loads(evt[0])
        if 'True' == header_dict.get('payload', 'False'):
            self._payload = [x**self._id for x in evt[1]]
        resp_msg = "{\"sink\": \"%d\"}" % self._id
        self._handle.send([resp_msg.encode()])


class ReactorDispatcherTestCase(unittest.TestCase):

    """docstring for ReactorDispatcherTestCase"unittest.TestCase ."""

    @classmethod
    def setUpClass(cls):
        """ SetUp the whole class. """
        cls._clients = {}
        cls._servers = {}
        cls._handlers = {}
        cls._RANGE = 4

        for x in range(1, cls._RANGE):
            endpoint = "ipc:///tmp/%d.ipc" % x
            cls._clients[x] = channel.DefaultChannel(endpoint)
            cls._servers[x] = channel.DefaultChannel(endpoint)
            cls._clients[x].connect()
            cls._servers[x].bind()

        handler_table = {}
        for x in range(1, cls._RANGE):
            server = cls._servers[x]
            handler = Handler(x, server)
            cls._handlers[x] = handler
            handler_table[server.socket] = handler

        my_dispatcher = dispatcher.Dispatcher(handler_table)
        threading.Thread(target=my_dispatcher.dispatch_events).start()

    @classmethod
    def tearDownClass(cls):
        """ Tear Down the whole class. """
        for x in range(1, cls._RANGE):
            cls._clients[x].close()
            cls._servers[x].close()

    def dispatch_events_test(self):
        """ Test dispacth events. """
        handlers = ReactorDispatcherTestCase._handlers
        # msg = "{\"source\": \"%d\", \"payload\": \"False\"}"
        header1 = "{\"source\": \"1\", \"payload\": \"False\"}"

        header2 = "{\"source\": \"2\", \"payload\": \"True\"}"
        payload2 = bytes([1, 2])

        header3 = "{\"source\": \"3\", \"payload\": \"True\"}"
        payload3 = bytes([1, 2, 3])
        try:
            client1 = ReactorDispatcherTestCase._clients[1]
            client2 = ReactorDispatcherTestCase._clients[2]
            client3 = ReactorDispatcherTestCase._clients[3]
        except KeyError as k:
            self.fail("Could not get clients: {0}".format(k))

        client1.send([header1.encode()])
        resp1 = client1.recv()
        self.assertEquals("{\"sink\": \"1\"}", resp1[0])
        self.assertEquals(header1, handlers[1]._header)

        client2.send([header2.encode(), payload2])
        resp2 = client2.recv()

        self.assertEquals(header2, handlers[2]._header)
        self.assertEquals(payload2[0], handlers[2]._payload[0])
        self.assertEquals(payload2[1]**2, handlers[2]._payload[1])
        self.assertEquals("{\"sink\": \"2\"}", resp2[0])

        client3.send([header3.encode(), payload3])
        resp3 = client3.recv()

        self.assertEquals(header3, handlers[3]._header)
        # Checking handling of third client
        self.assertEquals(header3, handlers[3]._header)
        self.assertEquals(payload3[0], handlers[3]._payload[0])
        self.assertEquals(payload3[1]**3, handlers[3]._payload[1])
        self.assertEquals(payload3[2]**3, handlers[3]._payload[2])
        # Receing response from handler3
        self.assertEquals("{\"sink\": \"3\"}", resp3[0])

        control = channel.DefaultChannel('ipc:///tmp/control.ipc')
        control.connect()
        control.send(["{\"action\": \"terminate\"}".encode()])
        control.close()

if __name__ == '__main__':
    unittest.main()
