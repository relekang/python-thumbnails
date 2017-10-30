# -*- coding: utf-8 -*-
import sys
if sys.version_info.major == 3:  # noqa: E402
    from pathlib import Path
    py3 = True  # noqa: E402
else:  # noqa: E402
    from pathlib2 import Path  # Python 2 backport
    py3 = False  # noqa: E402
import codecs
import os
from io import BytesIO

from thumbnails import helpers

from .conf import settings


class BaseStorageBackend(object):

    def __init__(self):
        self.location = settings.THUMBNAIL_PATH

    def path(self, path):
        """
        Creates a path based on the location attribute of the backend and the path argument
        of the function. If the path argument is an absolute path the path is returned.

        :param path: The path that should be joined with the backends location.
        """
        if os.path.isabs(path):
            return path
        return os.path.join(self.location, path)

    def open(self, name, **kwargs):
        return self._open(self.path(name), **kwargs)

    def exists(self, name):
        return self._exists(self.path(name))

    def save(self, name, data):
        return self._save(self.path(name), data)

    def _open(self, name, **kwargs):
        raise NotImplementedError

    def _exists(self, name):
        raise NotImplementedError

    def _save(self, name, data):
        raise NotImplementedError


class FilesystemStorageBackend(BaseStorageBackend):
    """
    A storage engine that uses Python built in filesystem functionality.
    """

    def __init__(self):
        super(FilesystemStorageBackend, self).__init__()
        if not os.path.exists(self.location):
            if py3:
                os.makedirs(self.location, exist_ok=True)
            else:
                Path(self.location).mkdir(exist_ok=True)

    def _open(self, name, mode='rb', encoding=None, errors='strict'):
        return codecs.open(name, mode=mode, encoding=encoding, errors=errors)

    def _exists(self, name):
        return os.path.exists(name)

    def _save(self, name, data):
        if not os.path.exists(os.path.dirname(name)):
            if py3:
                os.makedirs(os.path.dirname(name), exist_ok=True)
            else:
                Path(os.path.dirname(name)).mkdir(exist_ok=True)

        with open(name, 'wb') as f:
            f.write(data)


class DjangoStorageBackend(BaseStorageBackend):
    """
    A wrapper around Django's storage backend
    """

    def __init__(self):
        super(DjangoStorageBackend, self).__init__()
        self._backend = helpers.import_attribute(settings.DEFAULT_FILE_STORAGE)

    def _open(self, name, mode='rb'):
        return self._backend.open(name, mode=mode)

    def _exists(self, name):
        return self._backend.exists(name)

    def _save(self, name, data):
        return self._backend.save(name, BytesIO(data))
