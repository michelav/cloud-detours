#!/usr/bin/env python3
import yaml
from logging import config, getLogger
from pydetours.core import detours_context
from pydetours.dispatcher import Dispatcher
from pydetours.comm import DefaultChannel
from pydetours.handler import DefaultIOHandler, SimpleControlHandler
from pydetours.comm import get_Zcontext
from pathlib import Path


def create_handlers(dispatcher_conf):
    """ Create a map of handlers.

    It process the dispatcher configuration and creates
    a map with sockets (channel sockets) as keys and
    handlers as values.
    """
    handler_table = {}
    instances = dispatcher_conf['handlers']['instances']
    for handler in instances:
        handler.start()
        handle = handler.handle
        handler_table[handle.socket] = handler
    return handler_table


def setup_dirs(dirs):
    for place in dirs:
        cur_dir = Path(place)
        if not cur_dir.exists():
            cur_dir.mkdir()


def channel_constructor(loader, node):
    value = loader.construct_scalar(node)
    return DefaultChannel(value)


def io_handler_constructor(loader, node):
    options = loader.construct_mapping(node)
    handle = options.pop('channel')
    return DefaultIOHandler(handle, **options)


def control_handler_constructor(loader, node):
    options = loader.construct_mapping(node)
    handle = options.pop('channel')
    return SimpleControlHandler(handle, **options)


def main():
    """" Main execution code. """
    setup_dirs(detours_context['detours']['dirs'])

    config.dictConfig(detours_context['logging'])
    logger = getLogger(__name__)

    # COnfiguring constructors for custom tags
    yaml.add_constructor(u'!control_handler', control_handler_constructor)
    yaml.add_constructor(u'!io_handler', io_handler_constructor)
    yaml.add_constructor(u'!channel', channel_constructor)

    dispatch_layer = detours_context['detours']['dispatch_layer']

    with open(dispatch_layer, 'r') as f:
        handlers_conf = yaml.load(f)

    table = create_handlers(handlers_conf)
    reactor_dispatcher = Dispatcher(table)
    reactor_dispatcher.control_handler = handlers_conf['handlers']['control']
    reactor_dispatcher.dispatch_events()
    logger.info('Detours service terminated.')
    get_Zcontext().term()


if __name__ == '__main__':
    main()
