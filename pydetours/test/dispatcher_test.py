import threading
import unittest
from pydetours.comm import DefaultChannel
from pydetours.dispatcher import Dispatcher
from pydetours.handler import SimpleControlHandler


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
        if 'True' == self._header.get('payload', 'False'):
            self._payload = [x**self._id for x in evt[1]]
        resp_msg = {'sink': self._id}
        self._handle.send([resp_msg])

    def stop(self):
        """ Free all resources and close handle. """
        self._handle.close()


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
            cls._clients[x] = DefaultChannel(endpoint)
            cls._servers[x] = DefaultChannel(endpoint)
            cls._clients[x].connect()
            cls._servers[x].bind()

        handler_table = {}
        for x in range(1, cls._RANGE):
            server = cls._servers[x]
            handler = Handler(x, server)
            cls._handlers[x] = handler
            handler_table[server.socket] = handler

        control_channel = DefaultChannel('ipc:///tmp/control.ipc')
        control_channel.bind()
        control_handler = SimpleControlHandler(control_channel, name='Control')
        my_dispatcher = Dispatcher(handler_table)
        my_dispatcher.control_handler = control_handler
        threading.Thread(target=my_dispatcher.dispatch_events).start()

    @classmethod
    def tearDownClass(cls):
        """ Tear Down the whole class. """
        for x in range(1, cls._RANGE):
            cls._clients[x].close()
            cls._servers[x].close()

    def dispatch_events_test(self):
        # """ Test dispatch events. """
        handlers = ReactorDispatcherTestCase._handlers
        # msg = "{\"source\": \"%d\", \"payload\": \"False\"}"
        header1 = {'source': '1', 'payload': 'False'}

        header2 = {'source': '2', 'payload': 'True'}
        payload2 = bytes([1, 2])

        header3 = {'source': '3', 'payload': 'True'}
        payload3 = bytes([1, 2, 3])
        try:
            client1 = ReactorDispatcherTestCase._clients[1]
            client2 = ReactorDispatcherTestCase._clients[2]
            client3 = ReactorDispatcherTestCase._clients[3]
        except KeyError as k:
            self.fail("Could not get clients: {0}".format(k))

        client1.send([header1])
        resp1 = client1.recv()
        self.assertEquals(1, resp1[0].get('sink'), 'Sink value wrong.')
        self.assertEquals(header1['source'], handlers[1]._header['source'])
        self.assertEquals(header1['payload'], handlers[1]._header['payload'])

        client2.send([header2, payload2])
        resp2 = client2.recv()

        self.assertEquals('2', handlers[2]._header['source'])
        self.assertEquals('True', handlers[2]._header['payload'])
        self.assertEquals(payload2[0], handlers[2]._payload[0])
        self.assertEquals(payload2[1]**2, handlers[2]._payload[1])
        self.assertEquals(2, resp2[0].get('sink'), 'Sink value wrong.')

        client3.send([header3, payload3])
        resp3 = client3.recv()

        # Checking handling of third client
        self.assertEquals('3', handlers[3]._header['source'])
        self.assertEquals('True', handlers[3]._header['payload'])
        self.assertEquals(payload3[0], handlers[3]._payload[0])
        self.assertEquals(payload3[1]**3, handlers[3]._payload[1])
        self.assertEquals(payload3[2]**3, handlers[3]._payload[2])
        # Receing response from handler3
        self.assertEquals(3, resp3[0].get('sink'), 'Sink value wrong.')

        control = DefaultChannel('ipc:///tmp/control.ipc')
        control.connect()
        control.send([{'action': 'terminate'}])
        control.close()

if __name__ == '__main__':
    unittest.main()
