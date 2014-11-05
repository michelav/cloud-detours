"""
Provide dispatcher skeleton to use in Cloud Detours.

This module provides dispatcher. The framework class one
may use to create dispatchers and plug them into Cloud Detours.

"""
import zmq
import comm.channel as channel


class ReactorDispatcher(object):

    """Uses Reactor Pattern to dispatch events. """

    def __init__(self, handler_table):
        """ Constructor.

        handler_table maps ZMQ.Sockets into Handlers

        """
        super(ReactorDispatcher, self).__init__()
        self._handler_table = handler_table
        self._handles = self._handler_table.keys()

        # TODO Adjust method to use a control channel
        self._control = channel.DefaultChannel('ipc:///tmp/control.ipc')
        self._control.bind()
        self._dispatching = True

    def dispatch_events(self):
        """ Handle all arriving events and dispatch to appropriate handler. """
        poller = zmq.Poller()
        for handle in self._handles:  # detours channel
            poller.register(handle, zmq.POLLIN)

        poller.register(self._control.socket, zmq.POLLIN)
        while self._dispatching:
            try:
                socks = dict(poller.poll())
            except KeyboardInterrupt:
                break
            for ready_channel in socks.keys():
                if(ready_channel == self._control.socket):
                    self._handle_control_evt()  # Control Channels
                    continue
                handler = self._handler_table[ready_channel]
                handler.handle_event()
        self._control.close()

    def _handle_control_evt(self):
        """ Process control messages. """
        control_evt = self._control.recv()
        header = control_evt[0]

        # TODO: Include all message possibilities
        action = header['action']
        self._dispatching = not ('terminate' == action)


class Dispatcher(object):

    """docstring for dispatcher. """

    def __init__(self, handler_table, mechanism=ReactorDispatcher):
        """ Create a Dispatcher.

        handler_table is a dictionary of handles to handlers.
        The default mechanism is Reactor Pattern.

        """
        self._mechanism = mechanism(handler_table)

    def dispatch_events(self):
        """ Handle all arriving events and dispatch to appropriate handler. """
        self._mechanism.dispatch_events()
