
import os
from django.conf import settings

class EncodingOptions(object):
    
    specs_module = []
    input_file = 'input_filefield'
    
    def __init__(self, opts):
        if opts:
            for key, value in opts.__dict__.iteritems():
                setattr(self, key, value)
    

class Specification(object):
    pass
    