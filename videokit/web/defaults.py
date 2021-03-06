# -*- coding: utf-8 -*-

from videokit.meta import Specification

class Video_x264(Specification):
    
    identifier = 'x264'
    output_file = '%(identifier)s_file'
    # optional
    verbose_name = '%(identifier)s specification'
    match = '.+\.jpg'
    specs_field = None
    
    filters = {
        'scaling': {'width': 1024, 'height': 768,},
        'cropping': {'x': 16, 'y': 16,},
    }
    
    extensions = ['mp4',]
