import os 
from .base import *

stage = os.getenv('STAGE')
match stage:
    case 'development' :
        from .development import *
    case 'production':
        from .production import *
    case _:
        raise ImportError('STAGE argument must be either production or development')

if not ALLOWED_HOSTS :
    raise ValueError('ALLOWED_HOST is empty.')