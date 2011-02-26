# -*- coding: utf-8 -*-

from videokit.meta import Specification

class Video_x264(Specification):
    
    identifier = 'x264'
    
    # optional
    verbose_name = '%(identifier)s specification'
    match = '.+\.jpg'
    specs_field = None
    
    filters = {}
    
