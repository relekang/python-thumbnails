# -*- coding: utf-8 -*-

from thumbnails.conf import settings
from thumbnails.engines import DummyEngine
from thumbnails.helpers import get_engine, generate_filename, get_cache_backend
from thumbnails.images import SourceFile, Thumbnail

__version__ = '0.5.1'


def get_thumbnail(original, size, **options):
    """
    Creates or gets an already created thumbnail for the given image with the given size and
    options.

    :param original: File-path, url or base64-encoded string of the image that you want an
                     thumbnail.
    :param size: String with the wanted thumbnail size. On the form: ``200x200``, ``200`` or
                 ``x200``.

    :param crop: Crop settings, should be ``center``, ``top``, ``right``, ``bottom``, ``left``.
    :param force: If set to ``True`` the thumbnail will be created even if it exists before.
    :param quality: Overrides ``THUMBNAIL_QUALITY``, will set the quality used by the backend while
                    saving the thumbnail.
    :param scale_up: Overrides ``THUMBNAIL_SCALE_UP``, if set to ``True`` the image will be scaled
                     up if necessary.
    :param colormode: Overrides ``THUMBNAIL_COLORMODE``, The default colormode for thumbnails.
                      Supports all values supported by pillow. In other engines there is a best
                      effort translation from pillow modes to the modes supported by the current
                      engine.
    :param format: Overrides the format the thumbnail will be saved in. This will override both the
                   detected file type as well as the one specified in ``THUMBNAIL_FALLBACK_FORMAT``.
    :return: A Thumbnail object
    """

    engine = get_engine()
    cache = get_cache_backend()
    original = SourceFile(original)
    crop = options.get('crop', None)
    options = engine.evaluate_options(options)
    thumbnail_name = generate_filename(original, size, crop)

    if settings.THUMBNAIL_DUMMY:
        engine = DummyEngine()
        return engine.get_thumbnail(thumbnail_name, engine.parse_size(size), crop, options)

    cached = cache.get(thumbnail_name)

    force = options is not None and 'force' in options and options['force']
    if not force and cached:
        return cached

    thumbnail = Thumbnail(thumbnail_name, engine.get_format(original, options))
    if force or not thumbnail.exists:
        size = engine.parse_size(size)
        thumbnail.image = engine.get_thumbnail(original, size, crop, options)
        thumbnail.save(options)

        for resolution in settings.THUMBNAIL_ALTERNATIVE_RESOLUTIONS:
            resolution_size = engine.calculate_alternative_resolution_size(resolution, size)
            image = engine.get_thumbnail(original, resolution_size, crop, options)
            thumbnail.save_alternative_resolution(resolution, image, options)

    cache.set(thumbnail)
    return thumbnail
