# -*- coding: utf-8 -*-
from thumbnails.conf import settings
from thumbnails.images import Thumbnail

from .base import BaseThumbnailEngine


class DummyEngine(BaseThumbnailEngine):
    """
    A Engine that will use a placeholder service in order to show the Thumbnails. It uses
    ``THUMBNAIL_DUMMY_URL`` to build the url of the thumbnail. More info can be found in the
    dummy-mode section of the documentation.
    """

    def create(self, original, size, crop, options=None):
        thumbnail = Thumbnail('dummy_{}x{}'.format(size[0], size[1]), 'jpg')
        thumbnail.size = size
        thumbnail._url = self._get_url(size)
        return thumbnail

    def _get_url(self, size):
        return settings.THUMBNAIL_DUMMY_URL.format(width=size[0], height=size[1])

    def cleanup(self, original):
        pass
