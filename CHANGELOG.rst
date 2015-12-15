Changes since last release
~~~~~~~~~~~~~~~~~~~~~~~~~~

0.6.0
~~~~~
 - Reintroduce support for Python 2

0.5.0
~~~~~
 - Drop support for Python 2
 - Add django filters for markdown and html
 - Tested against release version of Django 1.8
 - Add ``THUMBNAIL_FORCE_FORMAT``
 - Add ``THUMBNAIL_FALLBACK_FORMAT``
 - Change ``THUMBNAIL_DUMMY_URL`` to use keyword arguments in string format

0.4.1
~~~~~
 - Add missing call of colormode in engine.create

0.4.0
~~~~~
 - Add support for base64 encoded images as source
 - Add support for colormode through setting the option ``colormode`` or the setting
   ``THUMBNAIL_COLORMODE``.

0.3.0
~~~~~
 - Add Django templatetag ``get_thumbnail``
 - Catch IOError and OSError in PillowEngine.engine_load_image and throw ThumbnailError, which
   will be caught in get_thumbnail if ``THUMBNAIL_DEBUG = False``.

0.2.1
~~~~~

0.2.0
~~~~~

 - PgmagickEngine
 - WandEngine
 - Higher maxblock in PillowEngine.engine_raw_data

0.1.0
~~~~~

 - Expendable image engine, storage backend and cache backend
 - PillowBackend
 - FilesystemStorageBackend
 - SimpleCacheBackend
 - RedisCacheBackend
 - Django integrations

   - DjangoStorageBackend
   - DjangoCacheBackend
   - Settings integration and defaults for django

 - Support for dummy thumbnails
