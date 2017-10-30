# -*- coding: utf-8 -*-
import unittest
from unittest import mock

from thumbnails.cache_backends import (BaseCacheBackend, DjangoCacheBackend, RedisCacheBackend,
                                       SimpleCacheBackend)
from thumbnails.images import Thumbnail

from .utils import has_installed


class CacheBackendTestMixin(object):
    def setUp(self):
        self.backend = self.BACKEND()

    def test_get_empty(self):
        self.assertIsNone(self.backend.get('not-in-cache'))

    def test_set_and_get(self):
        thumbnail = Thumbnail(['n', 'ame'], 'jpg')
        self.backend.set(thumbnail)
        cached_thumbnail = self.backend.get(thumbnail.name)
        self.assertIsInstance(cached_thumbnail, Thumbnail)
        self.assertEqual(cached_thumbnail.name, thumbnail.name)


class BaseCacheBackendTestCase(unittest.TestCase):
    def setUp(self):
        self.backend = BaseCacheBackend()

    def test_init(self):
        self.assertEqual(self.backend.TIMEOUT, 31536000)

    @mock.patch('thumbnails.cache_backends.BaseCacheBackend._get')
    def test_get_calls_backend_specific_get(self, mock__get):
        self.backend.get(['hi', 'there'])
        self.backend.get('key')
        mock__get.assert_has_calls([mock.call('hi/there'), mock.call('key')])

    @mock.patch('thumbnails.cache_backends.BaseCacheBackend._set')
    def test_set_calls_backend_specific_set(self, mock__set):
        thumbnail = Thumbnail(['hi', 'there'], 'jpg')
        self.backend.set(thumbnail)
        mock__set.assert_has_calls([mock.call('hi/there', thumbnail)])


class SimpleCacheBackendTestCase(CacheBackendTestMixin, unittest.TestCase):
    BACKEND = SimpleCacheBackend


@unittest.skipIf(not has_installed('django'), 'Django is not installed')
class DjangoCacheBackendTestCase(CacheBackendTestMixin, unittest.TestCase):
    BACKEND = DjangoCacheBackend


@unittest.skipIf(not has_installed('redis'), 'Redis not installed')
class RedisCacheBackendTestCase(CacheBackendTestMixin, unittest.TestCase):
    BACKEND = RedisCacheBackend

    def test_get_settings(self):
        settings = self.backend.get_settings()
        self.assertEqual(settings['host'], '127.0.0.1')
        self.assertEqual(settings['port'], 6379)
        self.assertEqual(settings['db'], 0)

        self.backend.connection_uri = 'redis://example.com:1234/9'
        settings = self.backend.get_settings()
        self.assertEqual(settings['host'], 'example.com')
        self.assertEqual(settings['port'], 1234)
        self.assertEqual(settings['db'], 9)
