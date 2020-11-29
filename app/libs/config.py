import os
from configparser import ConfigParser

import rootpath as rootpath

root_path = rootpath.detect(pattern='^requirements.txt$')


def to_abs_path(path):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(root_path, path)


def abs_path(func):
    def new_func(*args, **kwargs):
        path = func(*args, **kwargs)
        if os.path.isabs(path):
            return path
        else:
            return os.path.join(root_path, path)

    return new_func


class Config:
    def __init__(self, path=os.environ['config_path']):
        self._conf = ConfigParser(os.environ)
        self._conf.read(to_abs_path(path))

    @property
    def config(self) -> ConfigParser:
        return self._conf

    def get_session_secret_key(self) -> str:
        return os.environ['session_secret_key']

    def get_client_id(self) -> str:
        return os.environ['client_id']

    def get_client_secret(self) -> str:
        return os.environ['client_secret']

