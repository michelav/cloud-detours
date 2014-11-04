
import zmq
import json


__ZMQ_CONTEXT__ = None


def get_context():
    """ Build Context as a singleton. """
    global __ZMQ_CONTEXT__
    if __ZMQ_CONTEXT__ is None:
        __ZMQ_CONTEXT__ = zmq.Context()
        pass
    return __ZMQ_CONTEXT__


class EventError(Exception):

    """ Default exception for EventErrors. """

pass


class Channel(object):

    """docstring for Channel."""

    pass


class DefaultChannel(Channel):

    """docstring for DefaultChannel. """

    def __init__(self, endpoint):
        """ Constructor. """
        super(DefaultChannel, self).__init__()
        self._endpoint = endpoint
        self._context = get_context()

    def connect(self):
        """ Connect the channel into the _endpoint. """
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(self._endpoint)

    def bind(self):
        """ Bind the channel into the _endpoint. """
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(self._endpoint)

    def send(self, msg):
        """ Send event as message.

        The event is a list where each item is a frame
        of the message to be sent.

        The event should be organized according to the
        following frames:
        [HEADER FRAME] - A Map with control instructions
        [PAYLOAD FRAME] - If selected in Header frame
        [END] - End Delimiter frame

        Raises MessageError if None or invalid message.

        """
        if not msg:
            raise EventError('Invalid Event.')
        msg.append('[END]'.encode())
        self._socket.send_multipart(msg)

    def recv(self):
        """ Receive event as message.

        Return a dictionary with all headers and metadata of the event
        as well as an array of bytes as payload. One must test if payload
        is None .

        The event should be organized according to the
        following frames:
        [HEADER FRAME] - A Map with control instructions
        [PAYLOAD FRAME] - If selected in Header frame
        [END] - End Delimiter frame

        """
        msg = self._socket.recv_multipart()
        # payload = None
        header = json.loads(msg[0].decode())
        event = [header]
        if 'True' == header.get('payload', 'False'):
            event.append(msg[1])
        return event

    def close(self):
        """ Close channel connection. """
        self._socket.close()
