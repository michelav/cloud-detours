""" Provides core features for all modules in Cloud Detours. """

import yaml
import os


def create_context():
    """ Create and populate detours default context. """
    config_file = os.environ.get('CONFIG_FILE', 'etc/detours-config.yaml')

    with open(config_file, 'r') as f:
        config = yaml.load(f)
        f.close()
    return config


detours_context = create_context()

class CloudDetoursError(Exception):
    pass

class BadProviderError(CloudDetoursError):
    pass

class BadContainerError(CloudDetoursError):
    pass

class BadOptionsError(CloudDetoursError):
    pass