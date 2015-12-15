# -*- coding: utf-8 -*-
import base64
import os

import requests

from thumbnails.compat import BytesIO
from thumbnails.conf import settings
from thumbnails.helpers import get_engine, get_storage_backend


class Thumbnail(object):

    size = None, None
    image = None
    _url = None

    def __init__(self, name):
        self.name = '/'.join(name)

    @property
    def path(self):
        return os.path.join(settings.THUMBNAIL_PATH, '{}.{}'.format(self.name, self.extension))

    @property
    def url(self):
        if self._url:
            return self._url
        return '/'.join([settings.THUMBNAIL_URL, '{}.{}'.format(self.name, self.extension)])\
                  .replace('//', '/')

    @property
    def extension(self):
        return 'jpg'

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def ratio(self):
        return float(self.width) / float(self.height)

    @property
    def is_portrait(self):
        return self.ratio < 1

    @property
    def is_landscape(self):
        return self.ratio > 1

    @property
    def exists(self):
        return get_storage_backend().exists(self.path)

    def save(self, options):
        return get_storage_backend().save(self.path, get_engine().raw_data(self.image, options))

    def alternative_resolution_path(self, resolution):
        return os.path.join(
            settings.THUMBNAIL_PATH,
            '{}@{}x.{}'.format(self.name, resolution, self.extension)
        )

    def save_alternative_resolution(self, resolution, image, options):
        path = self.alternative_resolution_path(resolution)
        return get_storage_backend().save(path, get_engine().raw_data(image, options))


class SourceFile(object):

    def __init__(self, source_file):
        if hasattr(source_file, 'name'):
            self.file = source_file.name
        else:
            self.file = source_file

    def open(self):
        if self.file.startswith('http'):
            return requests.get(self.file, stream=True).raw
        elif self.file.startswith(r'data:image/'):
            return BytesIO(base64.b64decode(self.file.replace('data:image/jpeg;base64,', '')))
        return get_storage_backend().open(self.file)
