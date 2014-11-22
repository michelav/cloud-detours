import unittest
# from core import detours_context
from pydetours.core import BadContainerError, BadOptionsError, BadProviderError
from pathlib import Path
import pydetours.handler as handler
from pydetours.handler import DefaultCloudProvider, LocalProvider


class Handle(object):

    @property
    def endpoint(self):
        return "my_endpoint"


    def send(self, evt):
        self._event = evt

    @property
    def event(self):
        return self._event


class DefaultIOHandlerTestCase(unittest.TestCase):

    """docstring for ReactorDispatcherTestCase"unittest.TestCase ."""

    @classmethod
    def setUpClass(cls):
        cls.temp_container = Path('/tmp/detours')
        try:
            cls.temp_container.mkdir(mode=0o777, parents=False)
        except FileExistsError:
            pass

    def setUp(self):
        self.local_path = str(Path('.').absolute())
        self.handle = Handle()
        self.cloud_options = {'provider_name': 'google_storage',
                              'provider_class': DefaultCloudProvider,
                              'id': 'ID',
                              'key': 'KEY',
                              'container_name': 'cloud-detours-test',
                              'path_prefix': self.local_path
                              }

        self.local_options = {'provider_name': 'file system',
                              'provider_class': LocalProvider,
                              'container_name': '/tmp/detours',
                              'path_prefix': self.local_path
                              }
        self.cloud_handler = handler.DefaultIOHandler(
            self.handle, name='Google', **self.cloud_options)

        self.local_handler = handler.DefaultIOHandler(
            self.handle, name='Local', **self.local_options)

    def provider_does_not_exists_test(self):
        options = {'provider_name': 'google-cloud',
                   'provider_class': DefaultCloudProvider,
                   'id': '1234',
                   'key': '5678',
                   'container_name': 'bad_container',
                   'path_prefix': self.local_path
                   }

        with self.assertRaises(BadProviderError):
            handler.DefaultIOHandler(
                self.handle, name='Google', **options)

    def bad_container_test(self):
        cloud_options = {'provider_name': 'google_storage',
                         'provider_class': DefaultCloudProvider,
                         'id': '1234',
                         'key': '5678',
                         'container_name': 'bad_container',
                         'path_prefix': self.local_path
                         }

        local_options = {'provider_name': 'google-cloud',
                         'provider_class': LocalProvider,
                         'id': '1234',
                         'key': '5678',
                         'container_name': 'bad_container',
                         'path_prefix': self.local_path
                         }

        with self.assertRaises(BadContainerError):
            handler.DefaultIOHandler(
                self.handle, name='Google', **cloud_options)
            handler.DefaultIOHandler(self.handle, name= 'Local', **local_options)

    def bad_options_test(self):
        options = {}

        with self.assertRaises(BadOptionsError):
            handler.DefaultIOHandler(
                self.handle, name='Google CLoud', **options)
            handler.DefaultIOHandler(self.handle, name='Local', **options)

    def mkdir_test(self):

        h_mkdir = {handler.ACTION: handler.MKDIR_ACTION,
                   handler.DIR_NAME: 'my_dir'}
        r_mkdir = {handler.ACTION: handler.MKDIR_ACTION,
                   handler.DIR_NAME: 'my_dir',
                   handler.PAYLOAD: handler.FALSE,
                   handler.RETURN: handler.TRUE}

        mkdir_evt = [h_mkdir]

        # Error headers when creating a dir that exists
        error_msg = "Fatal Error: Could not create dir %s in provider %s."
        e_google = {handler.ERROR: 'MkdirError',
                    handler.PAYLOAD: handler.FALSE,
                    handler.MESSAGE: error_msg % ('my_dir', 'google_storage')}
        e_local = {handler.ERROR: 'MkdirError',
                   handler.PAYLOAD: handler.FALSE,
                   handler.MESSAGE: error_msg % ('my_dir', 'file system')}

        # Requesting to delete a dir that doesnt exists
        edel_header = {handler.ACTION: handler.DELETE_ACTION,
                       handler.OBJECT_NAME: 'my_dir123/'
                       }
        del_error_msg = "Could not delete %s in %s. Check logs."
        ed_google = {handler.ERROR: 'DeleteError',
                     handler.MESSAGE: del_error_msg % ('my_dir123/', 'google_storage'),
                     handler.PAYLOAD: handler.FALSE}
        ed_local = {handler.ERROR: 'DeleteError',
                    handler.MESSAGE: del_error_msg % ('my_dir123/', 'file system'),
                    handler.PAYLOAD: handler.FALSE}

        # Requesting to delete my_dir
        del_header = {handler.ACTION: handler.DELETE_ACTION,
                      handler.OBJECT_NAME: 'my_dir/'}
        rdel_header = {handler.ACTION: handler.DELETE_ACTION,
                       handler.OBJECT_NAME: 'my_dir/',
                       handler.RETURN: handler.TRUE,
                       handler.PAYLOAD: handler.FALSE}

        handlers = [self.cloud_handler, self.local_handler]
        mkdir_error_msgs = [e_google, e_local]
        del_error_msgs = [ed_google, ed_local]

        for i in range(0, len(handlers)):
            with self.subTest(i=i):
                handlers[i]._mkdir(mkdir_evt)
                return_evt = self.handle.event
                self.assertEqual(r_mkdir, return_evt[0])

                handlers[i]._mkdir(mkdir_evt)
                return_evt = self.handle.event
                self.assertEqual(mkdir_error_msgs[i], return_evt[0])

                handlers[i]._delete([edel_header])
                return_evt = self.handle.event
                self.assertEqual(del_error_msgs[i], return_evt[0])

                handlers[i]._delete([del_header])
                return_evt = self.handle.event
                self.assertEqual(rdel_header, return_evt[0])

    def read_write_delete_test(self):
        file_path = "%s/%s" % (self.local_path, 'my_obj.txt')
        text = "My writing text"

        h_read = {handler.ACTION: handler.READ_ACTION,
                  handler.OBJECT_NAME: file_path}
        read_evt = [h_read]

        h_failread = {handler.ACTION: handler.READ_ACTION,
                      handler.OBJECT_NAME: file_path,
                      handler.RETURN: handler.FALSE,
                      handler.PAYLOAD: handler.FALSE,
                      handler.MESSAGE: 'Object does not exists'}

        rh_read = {handler.ACTION: handler.READ_ACTION,
                   handler.OBJECT_NAME: file_path,
                   handler.PAYLOAD: handler.TRUE,
                   handler.RETURN: handler.TRUE}

        h_npwrite = {handler.ACTION: handler.WRITE_ACTION,
                     handler.PAYLOAD: handler.FALSE,
                     handler.OBJECT_NAME: file_path}

        h_failwrite = {handler.ERROR: 'WriteError',
                       handler.PAYLOAD: handler.FALSE,
                       handler.MESSAGE: 'Malformed event: '
                       'A write action requests payload.'}

        h_write = {handler.ACTION: handler.WRITE_ACTION,
                   handler.OBJECT_NAME: file_path,
                   handler.PAYLOAD: handler.TRUE}
        rh_write = {handler.ACTION: handler.WRITE_ACTION,
                    handler.OBJECT_NAME: file_path,
                    handler.PAYLOAD: handler.FALSE,
                    handler.RETURN: handler.TRUE}

        write_evt = [h_write, text.encode()]

        h_del = {handler.ACTION: handler.DELETE_ACTION,
                 handler.OBJECT_NAME: file_path
                 }
        rdel_header = {handler.ACTION: handler.DELETE_ACTION,
                       handler.OBJECT_NAME: file_path,
                       handler.PAYLOAD: handler.FALSE,
                       handler.RETURN: handler.TRUE}

        handlers = [self.cloud_handler, self.local_handler]

        for i in range(0, len(handlers)):
            with self.subTest(i=i):
                # Reading an obj that does not exists
                handlers[i]._read(read_evt)
                return_evt = self.handle.event
                self.assertEqual(h_failread, return_evt[0])

                # Failed Writing
                handlers[i]._write([h_npwrite])
                return_evt = self.handle.event
                self.assertEqual(h_failwrite, return_evt[0])

                # Writing
                handlers[i]._write(write_evt)
                return_evt = self.handle.event
                self.assertEqual(rh_write, return_evt[0])

                # Reading
                handlers[i]._read(read_evt)
                return_evt = self.handle.event
                self.assertEqual(rh_read, return_evt[0])
                self.assertEqual(
                    text, return_evt[1].decode(), "Payload corrupted.")

                # Deleting
                handlers[i]._delete([h_del])
                return_evt = self.handle.event
                self.assertEqual(rdel_header, return_evt[0])

    def check_status_test(self):
        cloud_status = self.cloud_handler.check_status()
        self.assertEqual("OK", cloud_status, "Checking status should work.")
        local_status = self.local_handler.check_status()
        self.assertEqual("OK", local_status, "Checking status should work.")

if __name__ == '__main__':

#    logging.config.dictConfig(detours_context['logging'])
    unittest.main()
