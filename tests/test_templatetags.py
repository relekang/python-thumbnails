# -*- coding: utf-8 -*-
import unittest

from thumbnails import settings

from .compat import mock
from .utils import has_installed

try:
    from django.template import Context, Template
    from django.db.models.fields import files
except ImportError:
    pass


@unittest.skipIf(not has_installed('django'), 'Django not installed')
class TemplateTagTestCase(unittest.TestCase):

    @mock.patch('thumbnails.get_thumbnail')
    def test_get_thumbnail_templatetag(self, mock_get_thumbnail):
        Template(
            '{% load thumbnails %}{% get_thumbnail "static/image.jpg" "200" as im %}{{im.url}}',
        ).render(Context())

        mock_get_thumbnail.assert_called_once_with('static/image.jpg', '200')

    @mock.patch('thumbnails.get_thumbnail')
    def test_get_thumbnail_templatetag_with_kwarg(self, mock_get_thumbnail):
        Template(
            '{% load thumbnails %}'
            '{% get_thumbnail "static/image.jpg" "100x100" crop="center" as im %}{{im.url}}',
        ).render(Context())

        mock_get_thumbnail.assert_called_once_with('static/image.jpg', '100x100', crop='center')

    @mock.patch('thumbnails.get_thumbnail')
    def test_get_thumbnail_templatetag_with_multiple_kwargs(self, mock_get_thumbnail):
        Template(
            '{% load thumbnails %}'
            '{% get_thumbnail "static/image.jpg" "200x200" crop="center" scale_up=True as im %}'
            '{{im.url}}',
        ).render(Context())

        mock_get_thumbnail.assert_called_once_with('static/image.jpg', '200x200', crop='center',
                                                   scale_up=True)

    @mock.patch('thumbnails.get_thumbnail')
    def test_get_thumbnail_templatetag_with_FileField_as_source(self, mock_get_thumbnail):
        field = files.FileField()
        _file = files.FieldFile(field=field, instance=None, name='image.jpg')
        Template(
            '{% load thumbnails %}'
            '{% get_thumbnail image "200x200" as im %}'
            '{{im.url}}',
        ).render(Context({
            'image': _file
        }))

        mock_get_thumbnail.assert_called_once_with(_file, '200x200')


@mock.patch('{}.get_thumbnail'.format(settings.THUMBNAIL_ENGINE), lambda *args: None)
@mock.patch('thumbnails.images.Thumbnail.save', lambda *args: None)
@mock.patch('thumbnails.images.Thumbnail.save_alternative_resolution', lambda *args: None)
@unittest.skipIf(not has_installed('django'), 'Django not installed')
class FilterTestCase(unittest.TestCase):

    def setUp(self):
        self.MARKDOWN_TEMPLATE = Template('{% load thumbnails %}{{ text|markdown_thumbnails }}')
        self.HTML_TEMPLATE = Template('{% load thumbnails %}{{ text|html_thumbnails }}')
        self.SAFE_HTML_TEMPLATE = Template('{% load thumbnails %}{{ text|safe_html_thumbnails }}')

    def test_markdown_filter(self):
        self.assertEqual(self.MARKDOWN_TEMPLATE.render(Context({
            'text': 'image: ![Title](/image.jpg)'
        })), 'image: ![Title](thumbnails-cache/09a/e5965fd6bcafba14e3e696059acfa3db6ca8e.jpg)')

        self.assertEqual(self.MARKDOWN_TEMPLATE.render(Context({
            'text': 'image: ![](/image.jpg)'
        })), 'image: ![](thumbnails-cache/09a/e5965fd6bcafba14e3e696059acfa3db6ca8e.jpg)')

    def test_html_filter(self):
        self.assertEqual(self.HTML_TEMPLATE.render(Context({
            'text': 'image: <img src="/image.jpg" alt="Title" />'
        })), 'image: <img src="thumbnails-cache/09a/e5965fd6bcafba14e3e696059acfa3db6ca8e.jpg"'
             ' alt="Title" />')

        self.assertEqual(self.HTML_TEMPLATE.render(Context({
            'text': 'image: <img src="/image.jpg" alt="" />'
        })), 'image: <img src="thumbnails-cache/09a/e5965fd6bcafba14e3e696059acfa3db6ca8e.jpg"'
             ' alt="" />')

        self.assertEqual(self.HTML_TEMPLATE.render(Context({
            'text': 'image: <img src="/image.jpg" />'
        })), 'image: <img src="thumbnails-cache/09a/e5965fd6bcafba14e3e696059acfa3db6ca8e.jpg" />')

    def test_safe_html_filter(self):
        self.assertEqual(self.SAFE_HTML_TEMPLATE.render(Context({
            'text': 'image: <img src="/image.jpg" alt="Title" />'
        })), 'image: &lt;img src=&quot;thumbnails-cache/09a/e5965fd6bcafba14e3e696059acfa3db6ca8e'
             '.jpg&quot; alt=&quot;Title&quot; /&gt;')

        self.assertEqual(self.SAFE_HTML_TEMPLATE.render(Context({
            'text': 'image: <img src="/image.jpg" alt="" />'
        })), 'image: &lt;img src=&quot;thumbnails-cache/09a/e5965fd6bcafba14e3e696059acfa3db6ca8e'
             '.jpg&quot; alt=&quot;&quot; /&gt;')

        self.assertEqual(self.SAFE_HTML_TEMPLATE.render(Context({
            'text': 'image: <img src="/image.jpg" />'
        })), 'image: &lt;img src=&quot;thumbnails-cache/09a/e5965fd6bcafba14e3e696059acfa3db6ca8e'
             '.jpg&quot; /&gt;')
