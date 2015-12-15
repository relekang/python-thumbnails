# -*- coding: utf-8 -*-
import hashlib
import os
import unittest

from PIL import Image

from thumbnails.compat import BytesIO
from thumbnails.conf import settings
from thumbnails.images import SourceFile, Thumbnail

from . import data
from .compat import mock
from .utils import has_installed


class ThumbnailTestCase(unittest.TestCase):

    def setUp(self):
        self.instance = Thumbnail(['n', 'ame'])
        self.instance.size = 200, 400

    def test_name(self):
        self.assertEqual(self.instance.name, 'n/ame')

    def test_path(self):
        self.assertTrue(self.instance.path.endswith('thumbnails-cache/n/ame.jpg'))

    def test_url(self):
        self.assertTrue(self.instance.url.endswith('/n/ame.jpg'))

    def test_width(self):
        self.assertEqual(self.instance.width, 200)

    def test_height(self):
        self.assertEqual(self.instance.height, 400)

    def test_ratio(self):
        self.assertEqual(self.instance.ratio, 0.5)

    def test_is_portrait(self):
        self.assertTrue(self.instance.is_portrait)
        self.instance.size = 400, 200
        self.assertFalse(self.instance.is_portrait)

    def test_is_landscape(self):
        self.assertFalse(self.instance.is_landscape)
        self.instance.size = 400, 200
        self.assertTrue(self.instance.is_landscape)

    @mock.patch('{}.exists'.format(settings.THUMBNAIL_STORAGE_BACKEND))
    def test_exists(self, mock_exists):
        self.instance = Thumbnail(['name'])
        self.assertTrue(self.instance.exists)
        mock_exists.assert_called_with(self.instance.path)


class SourceImageTestCase(unittest.TestCase):
    FILE_PATH = os.path.join(os.path.dirname(__file__), 'test_image.jpg')

    def test_init(self):
        self.assertEqual(SourceFile(self.FILE_PATH).file, self.FILE_PATH)

    @unittest.skipIf(not has_installed('django'), 'Django not installed')
    def test_django_image_files(self):
        from django.db.models.fields import files
        field = files.FileField()
        f = SourceFile(files.FieldFile(field=field, instance=None, name=self.FILE_PATH))
        self.assertEqual(f.file, self.FILE_PATH)
        f = SourceFile(files.ImageFieldFile(field=field, instance=None, name=self.FILE_PATH))
        self.assertEqual(f.file, self.FILE_PATH)

    def test_base64_encoded_string(self):
        file = SourceFile(data.BASE64_STRING_OF_IMAGE)
        self.assertEqual(
            hashlib.sha1(file.open().getvalue()).hexdigest(),
            '6666212f5302426c845ecb2a2901fae021735f24'
        )
        image = Image.open(BytesIO(file.open().read()))
        self.assertIsNotNone(image.load())
