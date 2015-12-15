# -*- coding: utf-8 -*-
import os
import unittest
from copy import deepcopy

from thumbnails.conf.wrapper import SettingsWrapper

from .compat import mock
from .utils import has_installed


class SettingsWrapperTestCase(unittest.TestCase):

    def test_default_values(self):
        settings = SettingsWrapper()
        self.assertEqual(settings.THUMBNAIL_ENGINE, 'thumbnails.engines.PillowEngine')

    def test_override_by_thumbnail_settings_module(self):
        env = deepcopy(os.environ)
        env['THUMBNAILS_SETTINGS_MODULE'] = 'tests.thumbnails_settings'

        with mock.patch.dict('os.environ', env):
            settings = SettingsWrapper()
            self.assertEqual(settings.THUMBNAIL_ENGINE, 'thumbnails.engines.DummyEngine')

        settings = SettingsWrapper()
        self.assertEqual(settings.THUMBNAIL_ENGINE, 'thumbnails.engines.PillowEngine')

    @unittest.skipIf(not has_installed('django'), 'Django not installed')
    def test_django_defaults(self):
        settings = SettingsWrapper()
        self.assertEqual(
            settings.THUMBNAIL_CACHE_BACKEND,
            'thumbnails.cache_backends.DjangoCacheBackend'
        )
