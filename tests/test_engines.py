# -*- coding: utf-8 -*-
import hashlib
import os
import unittest
from unittest import mock

from PIL import Image

from thumbnails.engines import DummyEngine, PgmagickEngine, PillowEngine, WandEngine
from thumbnails.engines.base import BaseThumbnailEngine
from thumbnails.errors import ThumbnailError
from thumbnails.images import SourceFile

from .utils import is_tox_env


class EngineTestMixin(object):

    def setUp(self):
        self.engine = self.ENGINE()
        self.filename = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
        self.file = SourceFile(self.filename)
        self.url = SourceFile('http://dummyimage.com/400x600')

        image = Image.new('L', (400, 600))
        image.save(self.filename)

    def tearDown(self):
        os.remove(self.filename)

    def assertSize(self, thumbnail, width, height):
        self.assertEqual(thumbnail.size[0], width)
        self.assertEqual(thumbnail.size[1], height)

    def assertRawData(self, raw_data):
        self.assertEqual(hashlib.sha1(raw_data).hexdigest(), self.RAW_DATA_HASH)

    @mock.patch('thumbnails.engines.base.BaseThumbnailEngine.create')
    @mock.patch('thumbnails.engines.base.BaseThumbnailEngine.cleanup')
    def test_get_thumbnail(self, mock_create, mock_cleanup):
        self.engine.get_thumbnail(self.file, '200', None, None)
        self.assertTrue(mock_create.called)
        self.assertTrue(mock_cleanup.called)

    @mock.patch('thumbnails.engines.base.BaseThumbnailEngine.create',
                side_effect=ThumbnailError(''))
    @mock.patch('thumbnails.engines.base.BaseThumbnailEngine.cleanup')
    def test_get_thumbnail_fail(self, mock_create, mock_cleanup):
        self.engine.get_thumbnail(self.file, '200', None, None)
        self.assertTrue(mock_create.called)
        self.assertTrue(mock_cleanup.called)

    def test_create_from_file(self):
        thumbnail = self.engine.create(self.file, (200, 300), None)
        self.assertSize(thumbnail, 200, 300)

    def test_create_from_url(self):
        thumbnail = self.engine.create(self.url, (200, 300), None)
        self.assertSize(thumbnail, 200, 300)

    def test_create_with_crop(self):
        thumbnail = self.engine.create(self.url, (200, 200), 'center')
        self.assertSize(thumbnail, 200, 200)

    def test_no_scale_no_crop(self):
        thumbnail = self.engine.create(self.url, (400, 600), None)
        self.assertSize(thumbnail, 400, 600)

    def test_raw_data(self):
        raw_data = self.engine.raw_data(
            self.engine.engine_load_image(self.file),
            self.engine.default_options()
        )
        self.assertRawData(raw_data)

    def test_cleanup(self):
        self.assertIsNone(self.engine.cleanup(self.file))

    def test_engine_colormode(self):
        image = self.engine.engine_load_image(self.file)
        self.engine.engine_colormode(image, 'RGB')

    def test_engine_get_format(self):
        image = self.engine.engine_load_image(self.file)
        self.assertEqual(self.engine.engine_get_format(image), 'JPEG')

        png_path = os.path.join(os.path.dirname(__file__), 'test_image.png')
        Image.new('L', (400, 600)).save(png_path)
        image = self.engine.engine_load_image(SourceFile(png_path))
        self.assertEqual(self.engine.engine_get_format(image), 'PNG')
        os.remove(png_path)

        png_path = os.path.join(os.path.dirname(__file__), 'test_image.gif')
        Image.new('L', (400, 600)).save(png_path)
        image = self.engine.engine_load_image(SourceFile(png_path))
        self.assertEqual(self.engine.engine_get_format(image), 'GIF')
        os.remove(png_path)


class BaseEngineTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = BaseThumbnailEngine()

    def test__calculate_scaling_factor_without_crop(self):
        calculate_scaling_factor = self.engine._calculate_scaling_factor
        original_size = (400, 600)
        self.assertEqual(calculate_scaling_factor(original_size, (400, 600), False), 1)
        self.assertEqual(calculate_scaling_factor(original_size, (100, 600), False), 0.25)
        self.assertEqual(calculate_scaling_factor(original_size, (400, 300), False), 0.5)
        self.assertEqual(calculate_scaling_factor(original_size, (200, 300), False), 0.5)
        self.assertEqual(calculate_scaling_factor(original_size, (200, None), False), 0.5)
        self.assertEqual(calculate_scaling_factor(original_size, (None, 300), False), 0.5)

    def test_parse_size(self):
        self.assertEqual(self.engine.parse_size('100'), (100, None))
        self.assertEqual(self.engine.parse_size('100x200'), (100, 200))
        self.assertEqual(self.engine.parse_size('1x10'), (1, 10))
        self.assertEqual(self.engine.parse_size('x1000'), (None, 1000))

    def test_parse_crop(self):
        self.assertEqual(self.engine.parse_crop('center', (200, 200), (100, 100)), (50, 50))
        self.assertEqual(self.engine.parse_crop('top', (200, 200), (100, 100)), (50, 0))
        self.assertEqual(self.engine.parse_crop('bottom', (200, 200), (100, 100)), (50, 100))
        self.assertEqual(self.engine.parse_crop('left', (200, 200), (100, 100)), (0, 50))
        self.assertEqual(self.engine.parse_crop('right', (200, 200), (100, 100)), (100, 50))

    def test_calculate_offset(self):
        self.assertEqual(self.engine.calculate_offset(0, 1000, 200), 0)
        self.assertEqual(self.engine.calculate_offset(50, 1000, 200), 400)
        self.assertEqual(self.engine.calculate_offset(100, 1000, 200), 800)

    def test_evaluate_options(self):
        self.assertEqual(self.engine.evaluate_options(None), self.engine.default_options())
        self.assertEqual(self.engine.evaluate_options({}), self.engine.default_options())
        self.assertEqual(self.engine.evaluate_options({'quality': 50})['quality'], 50)
        self.assertEqual(
            len(self.engine.evaluate_options({'quality': 50}).keys()),
            len(self.engine.evaluate_options({}).keys()),
        )

    def test_calculate_alternative_resolution_size(self):
        self.assertEqual(
            self.engine.calculate_alternative_resolution_size(2, (100, None)),
            (200, None)
        )
        self.assertEqual(
            self.engine.calculate_alternative_resolution_size(2, (100, 150)),
            (200, 300)
        )
        self.assertEqual(
            self.engine.calculate_alternative_resolution_size(2, (None, 150)),
            (None, 300)
        )
        self.assertEqual(
            self.engine.calculate_alternative_resolution_size(1.5, (100, 100)),
            (150, 150)
        )

    @mock.patch('thumbnails.engines.base.BaseThumbnailEngine.engine_colormode')
    def test_colormode(self, mock_engine_colormode):
        self.engine.colormode(None, {'colormode': 'RGB'})
        mock_engine_colormode.assert_called_once_with(None, 'RGB')

    @mock.patch('thumbnails.engines.base.BaseThumbnailEngine.engine_get_format', lambda *x: None)
    def test_get_format(self):
            self.assertEqual(self.engine.get_format(None, {}), 'JPEG')
            self.assertEqual(self.engine.get_format(None, {'format': 'WEBP'}), 'WEBP')


class DummyEngineTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = DummyEngine()
        self.filename = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
        self.file = SourceFile(self.filename)
        self.url = SourceFile('http://puppies.lkng.me/400x600/')

    def test_create_from_file(self):
        thumbnail = self.engine.create(self.file, (200, 300), None)
        self.assertEqual(thumbnail.width, 200)
        self.assertEqual(thumbnail.height, 300)
        self.assertEqual(thumbnail.url, 'http://puppies.lkng.me/200x300')

    def test_create_from_url(self):
        thumbnail = self.engine.create(self.url, (200, 300), None)
        self.assertEqual(thumbnail.width, 200)
        self.assertEqual(thumbnail.height, 300)
        self.assertEqual(thumbnail.url, 'http://puppies.lkng.me/200x300')


@unittest.skipIf(not is_tox_env('pillow'), 'not pillow environment')
class PillowEngineTestCase(EngineTestMixin, unittest.TestCase):
    ENGINE = PillowEngine
    RAW_DATA_HASH = 'cd63a4ccd85070c76db822ca5ccb11ba59966256'

    @mock.patch('PIL.Image.Image.load', side_effect=IOError)
    def test_load_with_io_error(self, mock_image_load):
        with self.assertRaises(ThumbnailError):
            self.engine.engine_load_image(self.file)
        self.assertTrue(mock_image_load.called)

    @mock.patch('PIL.Image.Image.load', side_effect=OSError)
    def test_load_with_os_error(self, mock_image_load):
        with self.assertRaises(ThumbnailError):
            self.engine.engine_load_image(self.file)
        self.assertTrue(mock_image_load.called)


@unittest.skipIf(not is_tox_env('wand'), 'not wand environment')
class WandEngineTestCase(EngineTestMixin, unittest.TestCase):
    ENGINE = WandEngine
    RAW_DATA_HASH = '8eb021308a7fb04cb0e87ce9026828f42e8a4a81'


@unittest.skipIf(not is_tox_env('pgmagick'), 'not pgmagick environment')
class PgmagickEngineTestCase(EngineTestMixin, unittest.TestCase):
    ENGINE = PgmagickEngine
    RAW_DATA_HASH = '47be661ff0e19f6e78eaa38b68db74d10f3f4c96'

    def assertSize(self, thumbnail, width, height):
        geometry = thumbnail.size()
        self.assertEqual(geometry.width(), width)
        self.assertEqual(geometry.height(), height)
