import os

from .base  import *
from .app import *
from .third_party import *
from .celery import *
from .drf import *
from .databases import *
from .security import *


DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = []

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda x: False,
}