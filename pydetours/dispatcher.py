"""
Provide dispatcher skeleton to use in Cloud Detours.

This module provides dispatcher. The framework class one
may use to create dispatchers and plug them into Cloud Detours.

"""
import zmq
import logging
import traceback
from pydetours.core import CloudDetoursError


""" Module-wide logger """
logger = logging.getLogger(__name__)

""" Fast pass for isEnableFor(DEBUG). """
is_debug_enabled = logger.isEnabledFor(logging.DEBUG)


class ReactorDispatcher(object):

    """Uses Reactor Pattern to dispatch events. """

    @property
    def control_handler(self):
        """ Control handler property.

        Tuple with handle as first element and handler as value
        Fulfill Reactor pattern with a control channel.
        """
        return self._control_handler

    @control_handler.setter
    def control_handler(self, value):
        """ Control handler property. """
        self._control_handler = value
        handle = self._control_handler.handle.socket
        self._handler_table[handle] = self._control_handler
        self._control_handler.controlled = self
        self._dispatching = True

    def __init__(self, handler_table):
        """ Constructor.

        handler_table maps ZMQ.Sockets into Handlers

        """
        super(ReactorDispatcher, self).__init__()
        self._handler_table = handler_table

    def dispatch_events(self):
        """ Handle all arriving events and dispatch to appropriate handler. """
        if self._control_handler is None:
            msg = "Control Handler is not configured."
            logger.error(msg)
            raise CloudDetoursError(msg)

        handles = self._handler_table.keys()
        poller = zmq.Poller()
        for handle in handles:  # detours channel
            poller.register(handle, zmq.POLLIN)

        # poller.register(self._control.socket, zmq.POLLIN)
        while self._dispatching:
            try:
                socks = dict(poller.poll())
            except KeyboardInterrupt:
                self.terminate()
                break
            for ready_channel in socks.keys():
                handler = self._handler_table[ready_channel]
                handler.handle_event()

    def _handle_control_evt(self):
        """ Process control messages. """
        control_evt = self._control.recv()
        header = control_evt[0]

        # TODO: Include all message possibilities
        action = header['action']
        self._dispatching = not ('terminate' == action)

    def check_status(self):
        handlers = self._handler_table.values()
        status_table = {}
        for elm in handlers:
            try:
                status = elm.check_status()
            except:
                formatted_lines = traceback.format_exc().splitlines()
                status = "NOK: {}".format(formatted_lines[-1])
            status_table[elm.name] = status
        return status_table

    def terminate(self):
        """ Terminate dispatching process. """
        handlers = self._handler_table.values()
        for elm in handlers:
            elm.stop()
        self._dispatching = False


class Dispatcher(object):

    """docstring for dispatcher. """

    @property
    def control_handler(self):
        """ Control handler property.

        Tuple with handle as first element and handler as value
        Fulfill Reactor pattern with a control channel.
        """
        return self._mechanism.control_handler

    @control_handler.setter
    def control_handler(self, value):
        """ Control handler property. """
        logger.debug("Setting control_handler.")
        self._mechanism.control_handler = value

    def __init__(self, handler_table, mechanism=ReactorDispatcher):
        """ Create a Dispatcher.

        handler_table is a dictionary of handles to handlers.
        The default mechanism is Reactor Pattern.

        """
        self._mechanism = mechanism(handler_table)

    def dispatch_events(self):
        """ Handle all arriving events and dispatch to appropriate handler. """
        self._mechanism.dispatch_events()
