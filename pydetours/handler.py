""" Provides default handlers to process events.

A Handler must provide a constructor that accepts a channel as handle.
It should also implement handle_event method.

"""
import logging
from io import BytesIO
from pathlib import Path
from pydetours.core import CloudDetoursError, BadProviderError
from pydetours.core import BadContainerError, BadOptionsError
from libcloud.storage.providers import get_driver
from libcloud.storage.types import ObjectDoesNotExistError
from libcloud.storage.types import ContainerDoesNotExistError

""" Module-wide logger """
logger = logging.getLogger(__name__)

""" Fast pass for isEnableFor(DEBUG). """
is_debug_enabled = logger.isEnabledFor(logging.DEBUG)

# Module Constants
CONTROL = 'control'
ACTION = 'action'
RETURN = 'return'
ERROR = 'error'
MESSAGE = 'message'
PAYLOAD = 'payload'
OBJECT_NAME = 'obj_name'
DIR_NAME = 'dir_name'

MKDIR_ACTION = 'mkdir'
READ_ACTION = 'read'
WRITE_ACTION = 'write'
CLOSE_ACTION = 'close'
OPEN_ACTION = 'open'
EXISTS_ACTION = 'exists'
DELETE_ACTION = 'delete'

TRUE = 'True'
FALSE = 'False'


class Provider(object):

    """ Provider Base Class. """

    def __init__(self, **options):
        """ Build a Cloud Provider. """
        try:
            self._name = options['provider_name']
            self._container_name = options['container_name']
            # Formating prefix
            raw = options['path_prefix']
            self._prefix = raw if ('/' == raw[-1:]) else "%s/" % (raw)

            options['path_prefix']
        except KeyError:
            msg = "Incomplete options. " \
                "You must fill a name, provider, container and prefix."
            self._handle_error(BadOptionsError, msg)

    @property
    def name(self):
        """ Provider constant. """
        return self._name

    @property
    def container_name(self):
        """ Provider constant. """
        return self._container_name

    def _process_path(self, abs_path):
        """ Remove path prefix. """
        if abs_path.startswith(self._prefix):
            return abs_path[len(self._prefix):]
        else:
            return abs_path

    def _handle_error(self, error, msg, *args):
        parsed_msg = msg % args if args else msg
        logger.exception(parsed_msg)
        raise error(parsed_msg)


class DefaultCloudProvider(Provider):

    """ Provides an IO resource. """

    def __init__(self, **options):
        """ Build a Cloud Provider. """
        super(DefaultCloudProvider, self).__init__(**options)
        try:
            cls = get_driver(self._name)
            self._driver = cls(options['id'], options['key'])

            self._container = self._driver.get_container(self._container_name)
            logger.info(
                "Connected to %s container from %s provider.",
                self._container_name, self._name)

        except AttributeError:
            msg = "Provider %s doesn't exists in detours."
            self._handle_error(BadProviderError, msg, self._name)

        except ContainerDoesNotExistError:
            msg = "Container %s does not exists in %s provider."
            self._handle_error(
                BadContainerError, msg, self._container_name, self._name)

        except Exception:
            msg = "Fatal error while creating %s provider."
            self._handle_error(CloudDetoursError, msg, self._name)
            raise

    def exists(self, object_name):
        """ Check if object exists. """
        parsed_obj_name = self._process_path(object_name)
        return (self._get_object(parsed_obj_name) is not None)

    def read(self, object_name):
        """ Read the object from configured place.

        It returns the object as an immutable byte sequence or None
        if it does not exists according to its textual name in object.
        """
        as_bytes = None
        parsed_obj_name = self._process_path(object_name)
        obj = self._get_object(parsed_obj_name)
        if obj is not None:  # Object exists
            stream = obj.as_stream()

            if is_debug_enabled:
                logger.debug(
                    "Object %s downloaded as stream from %s.",
                    object_name,
                    self._container.name
                    )

            parts = []
            for chunk in stream:
                parts.append(chunk)
            as_bytes = b''.join(parts)

        return as_bytes

    def write(self, object_name, data):
        """ Write data into object_name. """
        parsed_name = self._process_path(object_name)
        contents = BytesIO(data)
        try:
            self._container.upload_object_via_stream(contents, parsed_name)
        except Exception:
            msg = "Fatal Error. Could not upload object %s to %s provider."
            self._handle_error(CloudDetoursError, msg, parsed_name, self._name)

    def mkdir(self, dir_name):
        """ Create a dir if it does not exists.

        Returns True if created, False otherwise.
        """
        # Dir should have a '/' in its end
        parsed_dir = dir_name if ('/' == dir_name[-1:]) else "%s/" % (dir_name)
        # TODO Refactor this to have '/' as a parameter or configurable value
        if not self.exists(parsed_dir):
            try:
                self._container.upload_object_via_stream(
                    BytesIO(b''), parsed_dir)
            except Exception:
                logger.exception(
                    "Fatal error: Could not create %s in %s.",
                    parsed_dir,
                    self._container.name)
                raise

        else:
            logger.warning(
                "Directory %s already exists in %s.",
                parsed_dir,
                self._container.name)
            raise Exception("Could not create directory.")

    def delete(self, obj_name):
        """ Delete the object from container. """
        parsed_name = self._process_path(obj_name)
        obj = self._get_object(parsed_name)
        obj.delete()
        if is_debug_enabled:
            logger.debug(
                "Objet %s removed from %s container.",
                parsed_name, self._container_name)

    def _get_object(self, object_name):
        """ Get object. """
        obj = None
        try:
            obj = self._container.get_object(object_name)
        except ObjectDoesNotExistError:
            logger.warn(
                "Object %s does not exists in %s",
                object_name,
                self._container_name)
        return obj


class LocalProvider(Provider):

    """ Provides local storage IO. """

    def __init__(self, **options):
        """ Constructor. """
        super(LocalProvider, self).__init__(**options)
        self._container = Path(self._container_name)
        if not self._container.is_dir():
            msg = "Container {} does not exists in {} provider.".format(
                self._container_name, self._name)
            logger.error(msg)
            raise BadContainerError(msg)

        logger.info(
            "Connected to %s container from %s provider.",
            self._container,
            self._name)

    def exists(self, object_name):
        """ Check if object_name exists  in provider. """
        local_path = "%s/%s" % (
            self._container_name, self._process_path(object_name))
        path = Path(local_path)
        return path.exists()

    def read(self, object_name):
        """ Read object. """
        file_name = self._process_path(object_name)
        cur_file = Path(file_name)
        try:
            with cur_file.open('rb') as stream:
                parts = [chunk for chunk in stream]

            # Returning file as an array of bytes
            return b''.join(parts)
        except FileNotFoundError:
            logger.warning(
                "File %s not found in %s", file_name, self._name)
            return None

    def write(self, object_name, data):
        """ Write data in object name. """
        file_name = self._process_path(object_name)

        try:
            with open(file_name, 'wb') as file_obj:
                file_obj.write(data)
            if is_debug_enabled:
                logger.debug(
                    "Object %s written into  %s provider.",
                    object_name,
                    self._name
                    )
        except OSError:
            self._handle_error(
                CloudDetoursError,
                "Could not write in %s, container %s .",
                file_name,
                self._container_name)

    def mkdir(self, dir_name):
        """ Create directory dir_name. """
        file_name = self._process_path(dir_name)
        dir_path = Path(file_name)
        dir_path.mkdir()

    def delete(self, obj_name):
        """ Delete object name. """
        parsed_name = self._process_path(obj_name)
        obj = Path(parsed_name)
        if obj.is_dir():
            obj.rmdir()
        else:
            obj.unlink()

    def _process_path(self, object_name):
        cur_path = super()._process_path(object_name)
        return "%s/%s" % (self._container_name, cur_path)


class Handler(object):

    """ Abstract class to process incoming events. """

    @property
    def handle(self):
        """ Handle property. """
        return self._handle

    def __init__(self, handle, **options):
        """ Constructor. """
        super(Handler, self).__init__()
        self._name = options['name']
        self._handle = handle
        self._actions = {}

    def handle_event(self):
        """ Process events found in its handle. """
        evt = self._handle.recv()
        header = evt[0]
        action = header.get(ACTION)
        handle_ftn = self._actions.get(action, self._default_action)
        logger.info("%s Handler: Action %s received.", self._name, action)
        handle_ftn(evt)

    def stop(self):
        """ Free all resources and close handle. """
        self._handle.close()
        logger.info("Handler %s stopped.", self._name)

    def _default_action(self, event):
        header = {ERROR, 'Unknown action.'}
        resp_evt = self._build_evt(header)
        self._handle.send(resp_evt)

    def _build_evt(self, header, payload=None):
        """ Build the response event. """
        evt = [header]
        if payload:
            evt.append(payload)
            header[PAYLOAD] = TRUE
        else:
            header[PAYLOAD] = FALSE
        return evt


class DefaultIOHandler(Handler):

    """ Sugar class to test Dispatching Mechanism. """

    def __init__(self, handle, **options):
        """ Constructor.

        Handle is the source of any arriving event.
        Options is a group of key => value pairs. Most common
        options are:

            cloud-provider => [AWS, GOOGLE]
            destination => the bucket name, for instance

        You can provide other options if needed in some
        custom Handler.

        """
        super(DefaultIOHandler, self).__init__(handle, **options)
        provider_cls = options.get('provider_class', LocalProvider)
        self._provider = provider_cls(**options)
        self._actions = {READ_ACTION: self._read,
                         WRITE_ACTION: self._write,
                         CLOSE_ACTION: self._close,
                         OPEN_ACTION: self._open,
                         EXISTS_ACTION: self._exists,
                         MKDIR_ACTION: self._mkdir,
                         DELETE_ACTION: self._delete
                         }

        logger.info(
            "%s Handler available at %s endpoint.",
            self._name,
            self._handle.endpoint)

    def check_status(self):
        """ Check if everything is ok in handler. """
        obj_name = "status_ok.txt"
        text = "All OK"
        ok = True
        try:
            self._provider.write(obj_name, text)
            received = (text.encode() == self._provider.read(obj_name))
            self._delete(obj_name)
        except Exception:
            ok = False
        else:
            ok = (ok and received)

        return ok

    def _read(self, event):
        """ Read the object from provider. """
        header = event[0]
        resp_evt = None
        try:
            obj_name = header[OBJECT_NAME]
            payload = self._provider.read(obj_name)

            if payload is not None:
                resp_header = {ACTION: READ_ACTION,
                               OBJECT_NAME: obj_name,
                               RETURN: TRUE
                               }
            else:  # Object does not exists
                resp_header = {ACTION: READ_ACTION,
                               OBJECT_NAME: obj_name,
                               RETURN: FALSE,
                               MESSAGE: 'Object does not exists'
                               }
            resp_evt = self._build_evt(resp_header, payload)

        except KeyError:
            msg = "Malformed event: A read action requests an obj_name"
            resp_evt = self._handle_error('EventError', msg)

        except Exception:
            msg = "Fatal Error when reading {} from provider {}. " \
                "Check log for more details".format(
                    obj_name, self._provider.name)
            resp_evt = self._handle_error('EventError', msg)

        self._handle.send(resp_evt)

    def _write(self, event):
        header = event[0]
        try:
            obj_name = header[OBJECT_NAME]
            self._provider.write(obj_name, event[1])
            resp_header = {ACTION: WRITE_ACTION,
                           OBJECT_NAME: obj_name,
                           RETURN: TRUE
                           }
            resp_evt = self._build_evt(resp_header, None)

        except KeyError:
            msg = "Malformed event: A write action requests an obj_name"
            resp_evt = self._handle_error('EventError', msg)

        except IndexError:
            msg = "Malformed event: A write action requests payload."
            resp_evt = self._handle_error('WriteError', msg)

        except TypeError:
            msg = "Invalid payload type. It should be an array of bytes."
            resp_evt = self._handle_error('EventError', msg)

        except Exception:
            msg = "Fatal error when writing object {} to provider {}. " \
                "Check log for more details".format(
                    obj_name, self._provider.name)
            resp_evt = self._handle_error('ProviderError', msg)

        self._handle.send(resp_evt)  # Sending back the response

    def _mkdir(self, event):
        header = event[0]
        resp_evt = None
        resp_header = None
        try:
            dir_name = header[DIR_NAME]
            self._provider.mkdir(dir_name)
            resp_header = {ACTION: MKDIR_ACTION,
                           DIR_NAME: dir_name, RETURN: TRUE}

        except KeyError:
            msg = "Malformed event: dir_name is mandatory to mkdir action."
            resp_evt = self._handle_error('EventError', msg)

        except Exception:
            msg = "Fatal Error: Could not create dir {} " \
                "in provider {}.".format(dir_name, self._provider.name)
            resp_evt = self._handle_error('MkdirError', msg)
        else:
            logger.info(
                "Directory %s created in %s.",
                dir_name,
                self._provider.name)
            resp_evt = self._build_evt(resp_header)

        self._handle.send(resp_evt)  # Sending back the response

    def _exists(self, event):
        header = event[0]
        resp_evt = None
        found = False
        try:
            obj_name = header[OBJECT_NAME]
            found = self._provider.exists(obj_name)

        except KeyError:
            msg = "Malformed event: A read action requests an obj_name"
            resp_evt = self._handle_error('EventError', msg)

        except Exception:
            msg = "Fatal Error: Could not check if  {} " \
                "exists in provider {}. ".format(obj_name, self._provider.name)
            resp_evt = self._handle_error('EventError', msg)

        if found:
            resp_header = {ACTION: EXISTS_ACTION,
                           RETURN: TRUE
                           }
        else:
            resp_header = {ACTION: EXISTS_ACTION,
                           RETURN: FALSE
                           }
        resp_evt = self._build_evt(resp_header)

        self._handle.send(resp_evt)

    def _delete(self, event):
        header = event[0]
        resp_evt = None
        try:
            obj_name = header['obj_name']
            self._provider.delete(obj_name)
            resp_header = {ACTION: DELETE_ACTION,
                           OBJECT_NAME: obj_name,
                           RETURN: TRUE
                           }
            resp_evt = self._build_evt(resp_header)
        except Exception:
            msg = "Could not delete %s in %s. Check logs." % (
                obj_name, self._provider.name)
            resp_evt = self._handle_error(
                'DeleteError', msg)
        self._handle.send(resp_evt)

    def _close(self, event):
        resp_evt = self._handle_error(
            'NotImplementedError', 'Close action is not implemented.')
        self._handle.send(resp_evt)

    def _open(self, event):
        resp_evt = self._handle_error(
            'NotImplementedError', 'Open action is not implemented.')
        self._handle.send(resp_evt)

    def _handle_error(self, error_type, message):
        logger.exception(message)
        resp_header = {ERROR: error_type, MESSAGE: message,
                       PAYLOAD: FALSE}
        return [resp_header]


class SimpleControlHandler(Handler):

    """ Simple handler that process control messages. """

    @property
    def controlled(self):
        return self._controlled

    @controlled.setter
    def controlled(self, value):
        self._controlled = value

    def __init__(self, handle, **options):
        super(SimpleControlHandler, self).__init__(handle, **options)
        self._actions = {'status': self._check_status,
                 'terminate': self._terminate}

        logger.info("%s Handler available at %s endpoint.",
            self._name,
            self._handle.endpoint)

    def _check_status(self, evt):
        status = self._controlled.check_status()
        header = {ACTION: 'status', RETURN: status}
        self._handle.send(self._build_evt(header))

    def _terminate(self, evt):
        logger.info("Terminate command requested.")
        self._controlled.terminate()
