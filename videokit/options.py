
import os
from django.conf import settings

class EncodingOptions(object):
    
    presets = []
    input_field = 'input_file'
    
    def __init__(self, opts):
        if opts:
            for key, value in opts.__dict__.iteritems():
                setattr(self, key, value)
    

    