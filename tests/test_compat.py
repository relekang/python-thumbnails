# -*- coding: utf-8 -*-
import os
import shutil
import unittest

from thumbnails.compat import makedirs


class CompatTestCase(unittest.TestCase):

    def test_makedirs(self):
        path = os.path.join(os.getcwd(), 'makedirs-test/folders')
        makedirs(path, exist_ok=True)
        makedirs(path, exist_ok=True)

        with self.assertRaises(OSError):
            makedirs(path)

        shutil.rmtree(os.path.dirname(path))
