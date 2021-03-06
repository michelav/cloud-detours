
import zmq
import json
import logging


__ZMQ_CONTEXT__ = None

""" Module-wide logger """
logger = logging.getLogger(__name__)

""" Fast pass for isEnableFor(DEBUG). """
is_debug_enabled = logger.isEnabledFor(logging.DEBUG)


def get_Zcontext():
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
        self._context = get_Zcontext()
        self._poller = zmq.Poller()
        self._socket = None

    @property
    def socket(self):
        """ socket property."""
        return self._socket

    @property
    def endpoint(self):
        """ socket property."""
        return self._endpoint

    def connect(self):
        """ Connect the channel into the _endpoint. """
        if self._socket is None:
            self._socket = self._context.socket(zmq.REQ)
            self._socket.connect(self._endpoint)
            self._poller.register(self._socket, zmq.POLLIN)

    def bind(self):
        """ Bind the channel into the _endpoint. """
        if self._socket is None:
            self._socket = self._context.socket(zmq.REP)
            self._socket.bind(self._endpoint)
            self._poller.register(self._socket, zmq.POLLIN)

    def send(self, evt):
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
        if not evt:
            raise EventError('Invalid Event.')

        header = evt[0]
        has_payload = ('True' == header.get('payload', 'False'))
        msg = [json.dumps(header).encode()]
        if has_payload:
            msg.append(evt[1])

        msg.append('[END]'.encode())
        self._socket.send_multipart(msg)

    def recv(self, timeout=None):
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
        if self._poller.poll(timeout):
            msg = self._socket.recv_multipart()
            if not msg:
                raise EventError('Invalid Event.')

            header = json.loads(msg[0].decode())
            event = [header]

            has_payload = ('True' == header.get('payload', 'False'))
            if has_payload:
                event.append(msg[1])
            # [END] delimiter discarded
            return event
        else:
            error_msg = "Timeout while receiving Message."
            logger.warning(error_msg)
            raise IOError(error_msg)

    def close(self):
        """ Close channel connection. """
        # self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.close()
        logger.info("%s connection closed.", self._endpoint)
