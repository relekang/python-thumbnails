# -*- coding: utf-8 -*-
import unittest

from thumbnails import get_thumbnail
from thumbnails.conf import settings
from thumbnails.images import Thumbnail

from .compat import mock
from .utils import override_settings


class GetThumbnailTestCase(unittest.TestCase):

    @mock.patch('{}.get'.format(settings.THUMBNAIL_CACHE_BACKEND), lambda o, x:  True)
    def test_get_thumbnail_cached(self):
        self.assertTrue(get_thumbnail('', '200'))

    @mock.patch('{}.set'.format(settings.THUMBNAIL_CACHE_BACKEND))
    @mock.patch('{}.save'.format(settings.THUMBNAIL_STORAGE_BACKEND))
    @mock.patch('thumbnails.engines.base.BaseThumbnailEngine.get_thumbnail')
    def test_get_thumbnail(self, mock_get_thumbnail, mock_save, mock_cache_set):
        thumbnail = get_thumbnail('http://puppies.lkng.me/400x600/', '200')
        self.assertTrue(mock_get_thumbnail.called)
        self.assertTrue(mock_cache_set.called)
        self.assertTrue(mock_save.called)
        mock_save.assert_has_calls([
            mock.call(thumbnail.path, b''),
            mock.call(thumbnail.alternative_resolution_path(2), b''),
        ])
        self.assertIsInstance(thumbnail, Thumbnail)

    @mock.patch('{}.get'.format(settings.THUMBNAIL_CACHE_BACKEND), lambda x, y: True)
    @mock.patch('{}.set'.format(settings.THUMBNAIL_CACHE_BACKEND))
    @mock.patch('{}.save'.format(settings.THUMBNAIL_STORAGE_BACKEND))
    @mock.patch('thumbnails.engines.base.BaseThumbnailEngine.get_thumbnail')
    def test_force(self, mock_get_thumbnail, mock_save, mock_cache_set):
        get_thumbnail('http://puppies.lkng.me/400x600/', '200', force=True)
        get_thumbnail('http://puppies.lkng.me/400x600/', '200', force=True)
        get_thumbnail('http://puppies.lkng.me/400x600/', '200')
        self.assertEqual(len(mock_get_thumbnail.call_args_list), 4)
        self.assertEqual(len(mock_save.call_args_list), 4)
        self.assertEqual(len(mock_cache_set.call_args_list), 2)

    def test_dummy(self):
        with override_settings(THUMBNAIL_DUMMY=True):
            self.assertEqual(
                get_thumbnail('t.jpg', '200x200').url,
                'http://puppies.lkng.me/200x200'
            )
