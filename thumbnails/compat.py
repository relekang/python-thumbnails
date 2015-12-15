# -*- coding: utf-8 -*-
import errno

import six

BytesIO = six.BytesIO
StringIO = six.StringIO

if six.PY3:
    from os import makedirs
else:
    from os import makedirs as os_makedirs

    def makedirs(name, mode=0o777, exist_ok=False):
        try:
            os_makedirs(name, mode)
        except OSError as e:
            if e.errno != errno.EEXIST or not exist_ok:
                raise
