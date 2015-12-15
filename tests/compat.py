# -*- coding: utf-8 -*-
import six

if six.PY3:
    from unittest import mock  # noqa

elif six.PY2:
    import mock  # noqa
