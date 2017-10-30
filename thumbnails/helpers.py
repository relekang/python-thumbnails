# -*- coding: utf-8 -*-
import hashlib
import importlib

from thumbnails.conf import settings


def generate_filename(original, size, crop):
    h = hashlib.sha1(':'.join([original.file, str(size), str(crop)]).encode()).hexdigest()
    return [h[:3], h[3:]]


def import_attribute(module_string):
    modules = module_string.split('.')
    return getattr(importlib.import_module('.'.join(modules[:len(modules) - 1])), modules[-1])()


def get_engine():
    return import_attribute(settings.THUMBNAIL_ENGINE)


def get_cache_backend():
    return import_attribute(settings.THUMBNAIL_CACHE_BACKEND)


def get_storage_backend():
    return import_attribute(settings.THUMBNAIL_STORAGE_BACKEND)
